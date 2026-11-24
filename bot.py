import os
import time
import requests
from urllib.parse import urlparse

# ضع توكن البوت بين علامتي الاقتباس أدناه.
# الأفضل استخدام GitHub Secret باسم BOT_TOKEN بدلاً من كتابة التوكن هنا.
BOT_TOKEN = os.getenv("BOT_TOKEN", "9063389269:AAHvZP5Uc_bBwJjXv8_5yAWfJ9icDlRy81o")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
MAX_BYTES = 45 * 1024 * 1024  # حد تقريبي لتجنب تجاوز حد رفع Telegram Bot API


def telegram(method, data=None, files=None, timeout=60):
    response = requests.post(
        f"{API}/{method}", data=data, files=files, timeout=timeout
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API error"))
    return result["result"]


def send_text(chat_id, text):
    telegram("sendMessage", {"chat_id": chat_id, "text": text})


def download_direct_video(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("أرسل رابط HTTPS مباشر وآمن.")
    # لا يستخرج الفيديو من صفحات المواقع ولا يتجاوز تسجيل الدخول أو الحماية.
    r = requests.get(url, stream=True, timeout=(15, 60), headers={
        "User-Agent": "AuthorizedVideoDownloader/1.0"
    })
    r.raise_for_status()

    content_type = r.headers.get("Content-Type", "").lower()
    if not (content_type.startswith("video/") or urlparse(url).path.lower().endswith(
        (".mp4", ".mov", ".webm", ".m4v")
    )):
        raise ValueError("الرابط لا يبدو رابط فيديو مباشر. أرسل رابط ملف فيديو مباشر.")

    total = int(r.headers.get("Content-Length", "0") or 0)
    if total > MAX_BYTES:
        raise ValueError("حجم الفيديو أكبر من الحد المسموح للبوت (45 MB).")

    path = "/tmp/telegram_video.mp4"
    size = 0
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 256):
            if not chunk:
                continue
            size += len(chunk)
            if size > MAX_BYTES:
                raise ValueError("تجاوز الفيديو الحد المسموح (45 MB).")
            f.write(chunk)
    return path


def handle_message(message):
    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()

    if text == "/start":
        send_text(
            chat_id,
            "أهلاً بك. أرسل رابط HTTPS مباشر لملف فيديو تملك حق تنزيله. "
            "لا يدعم البوت استخراج الفيديو من صفحات المواقع أو تجاوز الحماية."
        )
        return

    if not text.startswith("https://"):
        send_text(chat_id, "أرسل رابط HTTPS مباشر لملف فيديو مصرح بتنزيله.")
        return

    send_text(chat_id, "جاري فحص الرابط وتنزيل الفيديو...")
    path = None
    try:
        path = download_direct_video(text)
        with open(path, "rb") as video:
            telegram(
                "sendVideo",
                data={"chat_id": chat_id, "caption": "تم تجهيز الفيديو."},
                files={"video": ("video.mp4", video, "video/mp4")},
                timeout=180
            )
    except Exception as exc:
        send_text(chat_id, f"تعذر تنزيل/إرسال الفيديو: {exc}")
    finally:
        if path and os.path.exists(path):
            os.remove(path)


def main():
    if not BOT_TOKEN or BOT_TOKEN == "اكتب_توكن_البوت_هنا":
        raise SystemExit("أضف BOT_TOKEN في GitHub Secrets أو داخل الملف.")
    offset = None
    print("Bot started. GitHub Actions runner has a limited runtime.")
    while True:
        try:
            params = {"timeout": 50}
            if offset is not None:
                params["offset"] = offset
            result = requests.get(f"{API}/getUpdates", params=params, timeout=60)
            result.raise_for_status()
            updates = result.json().get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
        except Exception as exc:
            print("Polling error:", exc)
            time.sleep(5)


if __name__ == "__main__":
    main()
