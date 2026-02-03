import rumps
from pynput import keyboard
import pyperclip
from deep_translator import GoogleTranslator
import time
import threading
import os
from AppKit import (
    NSPanel, NSWindowStyleMaskHUDWindow, NSWindowStyleMaskUtilityWindow,
    NSWindowStyleMaskNonactivatingPanel, NSFloatingWindowLevel,
    NSBackingStoreBuffered, NSMakeRect, NSScreen, NSColor, NSFont,
    NSTextView, NSScrollView, NSNoBorder, NSEvent, NSApplication,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSTextAlignmentLeft, NSAttributedString, NSMutableAttributedString,
    NSFontAttributeName, NSForegroundColorAttributeName, NSSize
)

class TranslationPanel:
    def __init__(self):
        mask = (NSWindowStyleMaskHUDWindow | 
                NSWindowStyleMaskUtilityWindow | 
                NSWindowStyleMaskNonactivatingPanel |
                NSWindowStyleMaskTitled | 
                NSWindowStyleMaskClosable)

        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 250),
            mask,
            NSBackingStoreBuffered,
            False
        )
        self.panel.setLevel_(NSFloatingWindowLevel)
        self.panel.setHidesOnDeactivate_(False)
        self.panel.setBackgroundColor_(NSColor.colorWithWhite_alpha_(0.1, 0.9))
        self.panel.setTitle_("Selection Translator")
        self.panel.setMovableByWindowBackground_(True)
        
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(10, 10, 380, 230))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setBorderType_(NSNoBorder)
        scroll_view.setDrawsBackground_(False)
        
        content_size = scroll_view.contentSize()
        text_frame = NSMakeRect(0, 0, content_size.width, content_size.height)
        
        self.text_view = NSTextView.alloc().initWithFrame_(text_frame)
        from AppKit import NSSize
        self.text_view.setTextContainerInset_(NSSize(5, 5))
        self.text_view.setTextColor_(NSColor.whiteColor())
        self.text_view.setFont_(NSFont.systemFontOfSize_(15))
        self.text_view.setBackgroundColor_(NSColor.clearColor())
        self.text_view.setAlignment_(NSTextAlignmentLeft)
        self.text_view.setEditable_(False)
        self.text_view.setSelectable_(True)
        self.text_view.setVerticallyResizable_(True)
        self.text_view.setHorizontallyResizable_(False)
        self.text_view.textContainer().setWidthTracksTextView_(True)
        
        scroll_view.setDocumentView_(self.text_view)
        self.panel.contentView().addSubview_(scroll_view)

    def show(self, text, original_text="", font_size=14):
        final_str = NSMutableAttributedString.alloc().init()
        
        attrs_result = {
            NSFontAttributeName: NSFont.systemFontOfSize_(font_size),
            NSForegroundColorAttributeName: NSColor.whiteColor()
        }
        str_result = NSAttributedString.alloc().initWithString_attributes_(text + "\n", attrs_result)
        final_str.appendAttributedString_(str_result)
        
        if original_text:
            final_str.appendAttributedString_(NSAttributedString.alloc().initWithString_("\n"))
            
            attrs_label = {
                NSFontAttributeName: NSFont.systemFontOfSize_(10),
                NSForegroundColorAttributeName: NSColor.colorWithWhite_alpha_(0.9, 1.0)
            }
            str_label = NSAttributedString.alloc().initWithString_attributes_("ORIGINAL CONTENT:\n", attrs_label)
            final_str.appendAttributedString_(str_label)
            
            attrs_orig = {
                NSFontAttributeName: NSFont.systemFontOfSize_(13),
                NSForegroundColorAttributeName: NSColor.colorWithWhite_alpha_(0.9, 1.0)
            }
            str_orig = NSAttributedString.alloc().initWithString_attributes_(original_text, attrs_orig)
            final_str.appendAttributedString_(str_orig)

        self.text_view.textStorage().setAttributedString_(final_str)
        
        from AppKit import NSMakeRange
        self.text_view.scrollRangeToVisible_(NSMakeRange(0, 0))
        
        mouse_loc = NSEvent.mouseLocation()
        
        x = mouse_loc.x + 20
        y = mouse_loc.y - 250 
        
        screen_frame = NSScreen.mainScreen().frame()
        if x + 400 > screen_frame.size.width:
            x = mouse_loc.x - 420 
        if y < 0:
            y = 20
            
        self.panel.setFrameOrigin_((x, y))
        self.panel.makeKeyAndOrderFront_(None)

    def close(self):
        self.panel.close()

class TranslatorApp(rumps.App):
    def __init__(self):
        super(TranslatorApp, self).__init__("🇻🇳")
        self.menu = ["Dịch văn bản", "Đóng cửa sổ dịch", "Hướng dẫn quyền"]
        self.translator = GoogleTranslator(source='auto', target='vi')
        self.trigger_translation = False
        self.floating_panel = None 

    def ensure_panel(self):
        if not self.floating_panel:
            self.floating_panel = TranslationPanel()

    @rumps.clicked("Dịch văn bản")
    def test_run(self, _):
        self.on_hotkey_signal()

    @rumps.clicked("Đóng cửa sổ dịch")
    def close_panel_menu(self, _):
        if self.floating_panel:
            self.floating_panel.close()

    @rumps.clicked("Hướng dẫn quyền")
    def help_perm(self, _):
        self.ensure_panel()
        msg = "Hướng dẫn cấp quyền để app hoạt động:\n\n"
        msg += "👉 Vào System Settings -> Privacy & Security -> Cấp quyền cho 'Selection Translator' (hoặc app chạy code) cho 2 mục sau:\n\n"
        msg += "1. Accessibility (Trợ năng):\n   -> Để App tự động Copy văn bản.\n\n"
        msg += "2. Input Monitoring (Giám sát đầu vào):\n   -> Để App nhận được phím tắt (Command+Ctrl+S).\n\n"
        msg += "Nếu không cấp quyền, app sẽ không hoạt động!"
        self.floating_panel.show(msg, font_size=12.5)

    def perform_translation(self):
        print("\n--- Đang bắt đầu dịch ---")
        
        time.sleep(0.3)
        
        old_text = pyperclip.paste()
        pyperclip.copy("")
        time.sleep(0.1)
        
        print("DEBUG: Đang gửi lệnh Command+C (pynput)...")
        from pynput.keyboard import Key, Controller
        keyboard = Controller()
        with keyboard.pressed(Key.cmd):
            keyboard.press('c')
            keyboard.release('c')
            
        text = ""
        for i in range(15):
            time.sleep(0.1)
            text = pyperclip.paste().strip()
            if text:
                print(f"DEBUG: Tự động Copy thành công sau {i/10}s")
                break
        
        if not text:
            if old_text and old_text.strip() and "DEBUG:" not in old_text:
                print("DEBUG: Fallback - Sử dụng văn bản cũ.")
                text = old_text.strip()
            else:
                self.ensure_panel()
                self.floating_panel.show("⚠️ Không lấy được văn bản.\n\nVui lòng kiểm tra lại quyền:\n1. Accessibility\n2. Input Monitoring\n\n(Click menu 'Hướng dẫn quyền' để xem chi tiết)", "")
                return

        try:
            print(f"DEBUG: Đang dịch...")
            translated = self.translator.translate(text)
            
            self.ensure_panel()
            self.floating_panel.show(translated, text)
            
        except Exception as e:
            self.ensure_panel()
            self.floating_panel.show(f"Lỗi: {str(e)}", "")

    def on_hotkey_signal(self):
        self.trigger_translation = True

    @rumps.timer(0.1)
    def check_trigger(self, _):
        if self.trigger_translation:
            self.trigger_translation = False
            self.perform_translation()

def start_hotkey_listener(callback):
    def on_activate():
        callback()

    def for_canonical(f):
        return lambda k: f(l.canonical(k))

    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<cmd>+<ctrl>+s'),
        on_activate
    )

    with keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)) as l:
        l.join()

if __name__ == "__main__":
    app = TranslatorApp()
    t = threading.Thread(target=start_hotkey_listener, args=(app.on_hotkey_signal,), daemon=True)
    t.start()
    app.run()
