# Telegram Video Bot (GitHub Actions)

## التشغيل
1. ارفع الملفات إلى مستودع GitHub خاص.
2. افتح Settings → Secrets and variables → Actions.
3. أنشئ Repository secret باسم `BOT_TOKEN` وضع قيمة توكن BotFather فيه.
4. افتح تبويب Actions ثم اختر `Telegram Video Bot` واضغط `Run workflow`.

## ملاحظات مهمة
- GitHub Actions ليس استضافة دائمة؛ هذا التشغيل اليدوي محدود المدة (حتى أقل من 6 ساعات)، وقد يتوقف بعدها.
- البوت يقبل رابط HTTPS مباشر لملف فيديو فقط. لا يستخرج ملفات من صفحات XNXX أو أي موقع، ولا يتجاوز تسجيل الدخول أو الحماية أو قيود الموقع.
- استخدمه فقط مع فيديوهات تملك حق تنزيلها. حد الإرسال مضبوط تقريباً على 45 MB.
- لا تكتب التوكن في مستودع عام. استخدم GitHub Secret باسم `BOT_TOKEN`.
