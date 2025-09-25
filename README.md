# 🤖 ChatFood - دستیار هوشمند و چند-ایجتی سفارش غذا

![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-⚡-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-🔗-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

این پروژه، پیاده‌سازی یک دستیار هوشمند مکالمه‌ای برای یک اپلیکیشن فرضی سفارش غذاست. این سیستم که به عنوان تسک ورودی برای **شرکت مهیمن** توسعه داده شده، با استفاده از **LangGraph** و معماری **چند-ایجتی (Multi-Agent)** ساخته شده و قابلیت‌های پیشرفته‌ای را برای ارائه یک تجربه کاربری هوشمند، سریع و کاملاً تعاملی فراهم می‌کند.

---

## 🎥 نمایش کوتاه عملکرد (Demo)

**(توصیه بسیار مهم: یک ویدیوی کوتاه یا GIF از اجرای سناریوی نهایی ضبط کرده و در اینجا قرار دهید. این کار تأثیر فوق‌العاده‌ای خواهد داشت. می‌توانید از ابزارهایی مانند ScreenToGif یا LICEcap استفاده کنید.)**

!https://youtu.be/C5aKreuoC9U
*در این دمو، عملکرد پیشنهاد فعال، جستجوی پیچیده با کارت‌های تعاملی، افزودن به سبد خرید و مشاهده سبد خرید به نمایش گذاشته شده است.*

---

## ✨ قابلیت‌های کلیدی (Key Features)

-   **معماری چند-ایجنتی پیشرفته:**
    -   یک **مسیریاب هوشمند (Router)** وظایf را به صورت دینامیک بین ایجنت‌های متخصص توزیع می‌کند تا بهترین ابزار برای هر درخواست انتخاب شود.
-   **پیشنهاد فعال و شخصی‌سازی شده:**
    -   ربات به صورت **فعال (Proactive)** گفتگو را با پیشنهادهای ویژه بر اساس تاریخچه سفارش‌های کاربر آغاز می‌کند و با دکمه‌های تعاملی، کاربر را درگیر می‌کند.
-   **رابط کاربری کاملاً تعاملی:**
    -   با استفاده از **Chainlit**، نتایج جستجو به صورت **کارت‌های زیبا** با جزئیات کامل و دکمه‌های **"افزودن به سبد خرید"** نمایش داده می‌شوند.
-   **سیستم سبد خرید کاربردی:**
    -   کاربران می‌توانند آیتم‌ها را مستقیماً از کارت‌های غذا به سبد خرید اضافه کرده و در هر زمان محتویات سبد خود را مشاهده کنند. وضعیت سبد خرید در حافظه جلسه مدیریت می‌شود.
-   **جستجوی هوشمند و دوگانه:**
    -   **`FoodSearchAgent`:** برای جستجوهای ساده و سریع بر اساس نام یا دسته‌بندی.
    -   **`FilterAgent`:** برای جستجوهای پیچیده با **چندین شرط**، به خصوص فیلتر بر اساس **قیمت**.
-   **بازیابی اطلاعات پیشرفته (RAG):**
    -   یک ایجنت RAG با استفاده از پایگاه داده وکتوری **LanceDB** و قابلیت جستجوی وب، به سوالات عمومی کاربران پاسخ‌های دقیق و جامعی ارائه می‌دهد.
-   **عملکرد بهینه و سریع:**
    -   با پیاده‌سازی تکنیک **Caching** برای مدل‌های سنگین Embedding، زمان پاسخ‌دهی در عملیات RAG از چندین دقیقه به **کمتر از ۳ ثانیه** کاهش یافته است.

## 🛠️ تکنولوژی‌های استفاده شده

-   **هوش مصنوعی و Backend:** Python, LangChain, LangGraph, OpenAI API (GPT-4o-mini)
-   **پایگاه داده:** SQLite (برای سفارش‌ها و منو), LanceDB (برای RAG)
-   **رابط کاربری:** Chainlit

## 🚀 نحوه اجرا

**۱. پیش‌نیازها:**
-   Python 3.11+
-   Git

**۲. نصب و راه‌اندازی:**

```bash
# 1. Clone the repository
git clone https://github.com/makhresearch/ChatFood-AI-Assistant.git
cd ChatFood-AI-Assistant

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# 3. Install dependencies from the requirements file
pip install -r requirements.txt

# 4. Setup API Key
# Create a .env file in the root directory and add your OpenAI API key:
# OPENAI_API_KEY="sk-..."

# 5. Setup databases and knowledge base
# These scripts will create and populate the necessary databases.
python setup_database.py
python update_database.py
python setup_rag.py

# 6. Run the application
chainlit run app.py -w
```

## 📈 بهبودهای آینده (Future Roadmap)

-   **سیستم کامل احراز هویت و مدیریت کاربران.**
-   **تکمیل چرخه سفارش** با قابلیت پرداخت و به‌روزرسانی وضعیت سفارش.
-   **درک محاوره‌ای عمیق‌تر** با استفاده از استخراج موجودیت (Entity Extraction) برای سفارش‌های پیچیده.
-   **استقرار (Deployment)** روی یک سرور ابری برای دسترسی عمومی.

---

**توسعه‌دهنده:** [Majid Khorramgah]