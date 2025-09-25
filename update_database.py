import sqlite3
import os

DB_PATH = os.path.join('db', 'chatfood.db')

def update_sample_orders():
    """
    جدول سفارش‌ها (orders) را با یک تاریخچه غنی برای کاربر نمونه 'user123' به‌روز می‌کند.
    این اسکریپت برای تست ایجنت پیشنهاددهنده ضروری است.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # ۱. حذف تمام سفارش‌های قبلی برای جلوگیری از تکرار و اطمینان از تازگی داده‌ها
        cursor.execute("DELETE FROM orders")
        print("ℹ️ تمام سفارش‌های قدیمی از جدول 'orders' حذف شدند.")

        # ۲. اضافه کردن تاریخچه سفارش جدید برای کاربران مختلف
        sample_orders = [
            # تاریخچه غنی برای user123
            (201, 'user123', 'پیتزا پپرونی', 'تحویل داده شده', 'خوب بود'),
            (202, 'user123', 'جوجه کباب', 'تحویل داده شده', 'عالی و خوشمزه!'),
            (204, 'user123', 'پاستا آلفردو', 'لغو شده', None),
            (205, 'user123', 'جوجه کباب', 'تحویل داده شده', 'باز هم عالی بود!'),
            # سفارش برای یک کاربر دیگر
            (203, 'user456', 'چیزبرگر', 'تحویل داده شده', 'معمولی بود.'),
            # یک سفارش فعال برای تست
            (101, 'user123', 'پیتزا پپرونی', 'در حال آماده‌سازی', None)
        ]
        
        cursor.executemany("INSERT INTO orders (id, user_id, food_name, status, review) VALUES (?, ?, ?, ?, ?)", sample_orders)

        conn.commit()
        conn.close()
        print("✅ داده‌های نمونه برای تاریخچه سفارش کاربر 'user123' با موفقیت در جدول 'orders' درج شد.")

    except sqlite3.Error as e:
        print(f"❌ خطایی در هنگام به‌روزرسانی پایگاه داده رخ داد: {e}")
        print("لطفاً ابتدا مطمئن شوید که فایل 'setup_database.py' را اجرا کرده‌اید.")


if __name__ == '__main__':
    update_sample_orders()