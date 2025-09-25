import sqlite3
import os

# مسیر دیتابیس را مشخص می‌کنیم
DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "chatfood.db")

def create_database():
    """
    ساختار پایگاه داده را ایجاد کرده و جدول غذاها (foods) را با داده‌های اولیه پر می‌کند.
    این اسکریپت باید فقط یک بار در ابتدا اجرا شود.
    """
    # اطمینان حاصل می‌کنیم که پوشه db وجود دارد
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ۱. ساخت جدول غذاها (foods)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        restaurant_name TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')

    # ۲. ساخت جدول سفارش‌ها (orders)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        food_name TEXT NOT NULL,
        status TEXT NOT NULL,
        review TEXT
    )
    ''')

    # ۳. پر کردن جدول غذاها فقط در صورتی که خالی باشد
    cursor.execute("SELECT COUNT(*) FROM foods")
    if cursor.fetchone()[0] == 0:
        sample_foods = [
            ('پیتزا پپرونی', 'فست فود', 'پیتزا هات', 150000),
            ('چیزبرگر', 'فست فود', 'برگرلند', 120000),
            ('جوجه کباب', 'ایرانی', 'رستوران اصیل', 180000),
            ('پاستا آلفردو', 'ایتالیایی', 'کافه روما', 200000),
            # غذاهای جدید که با لیست پیشنهادهای ویژه هماهنگ هستند
            ('کباب بختیاری', 'ایرانی', 'رستوران اصیل', 250000),
            ('سالاد سزار', 'پیش غذا', 'کافه روما', 110000),
            ('برگر ذغالی', 'فست فود', 'برگرلند', 160000)
        ]
        cursor.executemany("INSERT INTO foods (name, category, restaurant_name, price) VALUES (?, ?, ?, ?)", sample_foods)
        print("✅ جدول 'foods' با ۷ غذای نمونه با موفقیت پر شد.")
    else:
        print("ℹ️ جدول 'foods' از قبل دارای داده بود. تغییری ایجاد نشد.")

    conn.commit()
    conn.close()
    print(f"✅ پایگاه داده با موفقیت در مسیر '{DB_PATH}' ایجاد/بررسی شد.")

if __name__ == '__main__':
    create_database()