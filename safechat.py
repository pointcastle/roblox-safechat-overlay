import sys
import os
import xml.etree.ElementTree as ET
import time

import wx
import keyboard  # pip install keyboard
import psutil
import ctypes
import win32gui
import win32process

# Application version
__version__ = "1.0.0"

# Determine base path, whether running as script or bundled by PyInstaller
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Constants
XML_FILE = os.path.join(base_dir, "safechat.xml")
ICON_FILE = os.path.join(base_dir, "app.ico")  # Path to your .ico file

# Win32 constant for SetForegroundWindow
user32 = ctypes.windll.user32

def find_roblox_hwnds():
    hwnds = []
    def enum_handler(hwnd, _):
        if not (win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd)):
            return True
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = psutil.Process(pid)
            pname = proc.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True
        if 'robloxplayer' not in pname:
            return True
        title = win32gui.GetWindowText(hwnd) or ''
        if 'roblox' not in title.lower():
            return True
        hwnds.append(hwnd)
        return True
    win32gui.EnumWindows(enum_handler, None)
    return hwnds

class OverlayFrame(wx.Frame):
    TITLE_HEIGHT = 32

    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        title = f"Roblox SafeChat Overlay v{__version__}"
        super().__init__(None, title=title, style=style)

        # Set custom icon if available
        if os.path.exists(ICON_FILE):
            try:
                icon = wx.Icon(ICON_FILE, wx.BITMAP_TYPE_ICO)
                self.SetIcon(icon)
            except Exception:
                pass

        # Load chat phrases
        self.categories, self.phrases = self.load_phrases()
        self.buttons = {}
        self._dragging = False
        self._drag_offset = None

        # Semi-transparent
        self.SetTransparent(230)

        # Main sizer
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Title bar
        self.title = wx.Panel(self, size=(-1, self.TITLE_HEIGHT))
        self.title.SetBackgroundColour(wx.Colour(204, 204, 204))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.title.SetSizer(hbox)

        # Toggle menu visibility
        self.toggle_btn = wx.Button(self.title, label="▼", size=(28,28))
        self.toggle_btn.Bind(wx.EVT_BUTTON, self.on_toggle)
        hbox.Add(self.toggle_btn, flag=wx.LEFT|wx.CENTER, border=5)

        # Always-on-top toggle (📌 = pinned, 📍 = unpinned)
        self.ontop_btn = wx.Button(self.title, label="📌", size=(28,28))
        self.ontop_btn.SetToolTip("Toggle Always On Top")
        self.ontop_btn.Bind(wx.EVT_BUTTON, self.on_ontop_toggle)
        hbox.Add(self.ontop_btn, flag=wx.LEFT|wx.CENTER, border=5)

        hbox.AddStretchSpacer()
        vbox.Add(self.title, flag=wx.EXPAND)

        # Content
        self.content = wx.Panel(self)
        self.content.SetBackgroundColour(wx.Colour(255,255,255))
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content.SetSizer(self.content_sizer)
        for cat in self.categories:
            btn = wx.Button(self.content, label=cat)
            btn.Bind(wx.EVT_BUTTON, lambda e, c=cat: self.on_show_phrases(c))
            self.content_sizer.Add(btn, flag=wx.EXPAND|wx.ALL, border=2)
            self.buttons[cat] = btn
        vbox.Add(self.content, flag=wx.EXPAND)

        self.SetSizer(vbox)
        self.Fit()
        self.Raise()
        self.CenterOnScreen()

        # Drag events
        self.title.Bind(wx.EVT_LEFT_DOWN, self.on_title_down)
        self.title.Bind(wx.EVT_MOTION, self.on_title_motion)
        self.title.Bind(wx.EVT_LEFT_UP, self.on_title_up)

    def load_phrases(self):
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        cats, phs = [], {}
        for ut in root.findall('utterance'):
            cat = (ut.text or "").strip()
            if not cat:
                continue
            cats.append(cat)
            leafs = []
            def recurse(node):
                for c in node.findall('utterance'):
                    txt = (c.text or "").strip()
                    if c.findall('utterance'):
                        recurse(c)
                    elif txt:
                        leafs.append(txt)
            recurse(ut)
            phs[cat] = leafs or [cat]
        return cats, phs

    def on_title_down(self, event):
        pos = wx.GetMousePosition()
        fx, fy = self.GetPosition()
        self._dragging = True
        self._drag_offset = (pos.x - fx, pos.y - fy)
        event.Skip()

    def on_title_motion(self, event):
        if self._dragging and event.Dragging() and event.LeftIsDown():
            pos = wx.GetMousePosition()
            dx, dy = self._drag_offset
            self.Move(pos.x - dx, pos.y - dy)
        event.Skip()

    def on_title_up(self, event):
        self._dragging = False
        self._drag_offset = None
        event.Skip()

    def on_toggle(self, event):
        vis = self.content.IsShown()
        self.content.Show(not vis)
        self.toggle_btn.SetLabel("▲" if vis else "▼")
        self.Fit()

    def on_ontop_toggle(self, event):
        style = self.GetWindowStyleFlag()
        pinned = False
        if style & wx.STAY_ON_TOP:
            style &= ~wx.STAY_ON_TOP
        else:
            style |= wx.STAY_ON_TOP
            pinned = True
        self.SetWindowStyleFlag(style)
        self.ontop_btn.SetLabel("📌" if pinned else "📍")
        self.Raise()

    def on_show_phrases(self, category):
        menu = wx.Menu()
        for phrase in self.phrases.get(category, []):
            item = menu.Append(wx.ID_ANY, phrase)
            menu.Bind(wx.EVT_MENU, lambda e, txt=phrase: self.send_phrase(txt), item)
        btn = self.buttons[category]
        w, h = btn.GetSize()
        pt = btn.ClientToScreen((0, h))
        self.PopupMenu(menu, self.ScreenToClient(pt))
        menu.Destroy()

    def send_phrase(self, text):
        hwnds = find_roblox_hwnds()
        if hwnds:
            user32.SetForegroundWindow(hwnds[0])
            time.sleep(0.05)
        keyboard.press_and_release('/')
        time.sleep(0.05)
        keyboard.write(text)
        time.sleep(0.05)
        keyboard.press_and_release('enter')

if __name__ == '__main__':
    app = wx.App(False)
    frame = OverlayFrame()
    frame.Show()
    app.MainLoop()
