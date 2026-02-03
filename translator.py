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
    NSTextAlignmentLeft
)

# --- Class giao diện Floating Window ---
class TranslationPanel:
    def __init__(self):
        # Tạo cửa sổ kiểu HUD + Có tiêu đề (để kéo) + Có nút đóng
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
        self.panel.setLevel_(NSFloatingWindowLevel) # Luôn nổi trên cùng
        self.panel.setHidesOnDeactivate_(False)
        self.panel.setBackgroundColor_(NSColor.colorWithWhite_alpha_(0.1, 0.9)) # Màu nền tối
        self.panel.setTitle_("Selection Translator") # Tiêu đề
        self.panel.setMovableByWindowBackground_(True) # Cho phép kéo bằng cách giữ nền (tiện hơn)
        
        # Scroll View để chứa văn bản dài
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(10, 10, 380, 230))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setBorderType_(NSNoBorder)
        scroll_view.setDrawsBackground_(False)
        
        # Text View hiển thị nội dung
        # Lấy kích thước scroll view để tạo frame cho text view
        content_size = scroll_view.contentSize()
        text_frame = NSMakeRect(0, 0, content_size.width, content_size.height)
        
        self.text_view = NSTextView.alloc().initWithFrame_(text_frame)
        self.text_view.setTextColor_(NSColor.whiteColor())
        self.text_view.setFont_(NSFont.systemFontOfSize_(14))
        self.text_view.setBackgroundColor_(NSColor.clearColor())
        self.text_view.setAlignment_(NSTextAlignmentLeft) # Fix lỗi giãn chữ
        self.text_view.setEditable_(False) # Không cho sửa
        self.text_view.setSelectable_(True) # Cho phép copy lại
        self.text_view.setVerticallyResizable_(True)
        self.text_view.setHorizontallyResizable_(False) # Bắt buộc xuống dòng
        self.text_view.textContainer().setWidthTracksTextView_(True) # Wrap theo chiều ngang
        
        scroll_view.setDocumentView_(self.text_view)
        self.panel.contentView().addSubview_(scroll_view)

    def show(self, text, original_text=""):
        # Nếu có văn bản gốc thì hiện ngăn cách, không thì chỉ hiện text chính (dùng cho thông báo/lỗi)
        if original_text:
            full_content = f"{text}\n\n----------------\n[Original]:\n{original_text}"
        else:
            full_content = text
        self.text_view.setString_(full_content)
        
        # Reset scroll về đầu trang (Dùng NSMakeRange thay vì NSMakeRect)
        from AppKit import NSMakeRange
        self.text_view.scrollRangeToVisible_(NSMakeRange(0, 0))
        
        # Lấy vị trí chuột hiện tại
        mouse_loc = NSEvent.mouseLocation()
        
        # Tính toán vị trí cửa sổ (cạnh chuột)
        # Lưu ý: Hệ tọa độ Y của macOS bị ngược (gốc ở dưới cùng), nhưng mouseLocation cũng trả về như vậy nên ta dùng luôn.
        x = mouse_loc.x + 20
        y = mouse_loc.y - 250 # Dịch lên trên một chút để không bị che
        
        # Đảm bảo không bay ra ngoài màn hình
        screen_frame = NSScreen.mainScreen().frame()
        if x + 400 > screen_frame.size.width:
            x = mouse_loc.x - 420 # Nếu sát lề phải thì hiển thị sang trái
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
        self.floating_panel = None # Khởi tạo sau để tránh lỗi luồng

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
        msg += "2. Input Monitoring (Giám sát đầu vào):\n   -> Để App nhận được phím tắt.\n\n"
        msg += "Nếu không cấp quyền, app sẽ không hoạt động!"
        self.floating_panel.show(msg)

    def perform_translation(self):
        print("\n--- Đang bắt đầu dịch ---")
        
        # 1. Đợi người dùng thả phím tắt
        time.sleep(0.3)
        
        # 2. Xóa clipboard
        old_text = pyperclip.paste()
        pyperclip.copy("")
        time.sleep(0.1)
        
        # 3. Gửi lệnh Cmd+C bằng pynput
        print("DEBUG: Đang gửi lệnh Cmd+C (pynput)...")
        from pynput.keyboard import Key, Controller
        keyboard = Controller()
        with keyboard.pressed(Key.cmd):
            keyboard.press('c')
            keyboard.release('c')
            
        # 4. Đợi văn bản mới
        text = ""
        for i in range(15):
            time.sleep(0.1)
            text = pyperclip.paste().strip()
            if text:
                print(f"DEBUG: Tự động Copy thành công sau {i/10}s")
                break
        
        # 5. Fallback
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
            
            # HIỂN THỊ FLOATING PANEL (Full text)
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
    with keyboard.GlobalHotKeys({
            '<cmd>+<shift>+t': callback,
            '<cmd>+T': callback}) as h:
        h.join()

if __name__ == "__main__":
    app = TranslatorApp()
    t = threading.Thread(target=start_hotkey_listener, args=(app.on_hotkey_signal,), daemon=True)
    t.start()
    app.run()
