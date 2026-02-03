# 🇻🇳 Selection Translator (MacOS)

**Ứng dụng dịch thuật nhanh chóng trên MacOS cho người Việt.**  
Không cần copy-paste thủ công, không cần mở Google Dịch. Chỉ cần bôi đen và nhấn phím tắt!

---

## 🚀 Tính năng chính

- ✅ **Dịch tức thì**: Bôi đen chữ bất kỳ đâu -> Nhấn `Command + Control + S`.
- ✅ **Giao diện hiện đại**: Cửa sổ kết quả tối giản, hiện ngay cạnh con trỏ chuột.
- ✅ **Thông minh**: Tự động copy văn bản giúp bạn.
- ✅ **Tiện lợi**: Cửa sổ luôn nổi (Always on Top) để bạn dễ vừa đọc vừa làm việc.

---

## Tải xuống & Cài đặt

1.  Truy cập mục **[Releases](https://github.com/ch-hnhu/selection_translator_macos/releases)**.
2.  Tải file `SelectionTranslator.dmg`.
3.  Mở file `.dmg` vừa tải.
4.  Kéo **Selection Translator** vào thư mục **Applications** (Ứng dụng).

---

## ⚙️ Thiết lập lần đầu (Quan trọng ⚠️)

Vì ứng dụng cần "nghe" phím tắt và "copy" giúp bạn, macOS sẽ hỏi quyền bảo mật. Bạn cần cấp quyền **một lần duy nhất** để app hoạt động trơn tru:

### 1. Cấp quyền Trợ năng (Accessibility)

Để app có thể tự động lấy văn bản bạn đã bôi đen.

- Vào **System Settings** > **Privacy & Security** > **Accessibility**.
- Tìm **Selection Translator** và tick vào ô checkbox để cấp quyền.

### 2. Cấp quyền Phím tắt (Input Monitoring)

Để app nhận diện được khi bạn nhấn `Command + Control + S`.

- Vào **System Settings** > **Privacy & Security** > **Input Monitoring**.
- Tìm **Selection Translator** và tick vào ô checkbox để cấp quyền.

> ⚠️ **Lưu ý**: Nếu không tìm thấy ứng dụng, hãy thêm thủ công bằng nút (+).

_(Nếu mở app lên mà không thấy dịch được, hãy kiểm tra lại 2 quyền này!)_

---

## 📖 Cách sử dụng

1.  **Bôi đen** đoạn văn bản.
2.  Nhấn tổ hợp phím: **`Command` + `Control` + `S`**
3.  Xem kết quả dịch hiện ra ngay bên cạnh!

---

<details>
<summary>Dành cho người muốn tự build app và vọc vạch code</summary>

### Yêu cầu hệ thống:

- **macOS**: Monterey (12.0) trở lên.
- **Python**: 3.9+ (Gõ `python3 --version` để kiểm tra).
- **Git**: Đã cài đặt.

### Các bước thực hiện:

```bash
git clone https://github.com/ch-hnhu/selection_translator_macos.git
cd selection_translator_macos

# Tạo và kích hoạt môi trường ảo (Khuyên dùng)
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python3 translator.py
```

**Lưu ý:** Khi chạy bằng code, bạn cần cấp quyền **Accessibility** và **Input Monitoring** cho **Terminal** hoặc VS Code (nơi bạn chạy code) thay vì cho App để có thể hoạt động được.

</details>
