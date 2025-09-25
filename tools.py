import sqlite3
import os
from typing import List

DB_PATH = os.path.join('db', 'chatfood.db')

def get_order_status(order_id: int) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return f"وضعیت سفارش {order_id}، '{result[0]}' است."
        return f"سفارشی با شناسه {order_id} پیدا نشد."
    except sqlite3.Error as e:
        print(f"!!! خطای پایگاه داده در get_order_status: {e}")
        return "متاسفم، در حال حاضر مشکلی در اتصال به پایگاه داده سفارش‌ها وجود دارد."

def cancel_order(order_id: int) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return f"سفارشی با شناسه {order_id} پیدا نشد."
        if result[0] == 'در حال آماده‌سازی':
            cursor.execute("UPDATE orders SET status = 'لغو شده' WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()
            return f"سفارش {order_id} با موفقیت لغو شد."
        else:
            conn.close()
            return f"امکان لغو سفارش {order_id} وجود ندارد زیرا وضعیت آن '{result[0]}' است."
    except sqlite3.Error as e:
        print(f"!!! خطای پایگاه داده در cancel_order: {e}")
        return "متاسفم، در حال حاضر مشکلی در اتصال به پایگاه داده سفارش‌ها وجود دارد."

def search_food(query: str) -> list:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("SELECT name, restaurant_name, price FROM foods WHERE name LIKE ? OR category LIKE ?", (search_term, search_term))
        results = cursor.fetchall()
        conn.close()
        if not results:
            return []
        return [{"name": name, "restaurant": restaurant, "price": price} for name, restaurant, price in results]
    except sqlite3.Error as e:
        print(f"!!! خطای پایگاه داده در search_food: {e}")
        return [{"error": "متاسفم، مشکلی در اتصال به پایگاه داده منوی غذاها وجود دارد."}]

def get_order_history(user_id: str) -> list:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT food_name FROM orders WHERE user_id = ? AND status = 'تحویل داده شده'", (user_id,))
        results = cursor.fetchall()
        conn.close()
        return [row[0] for row in results]
    except sqlite3.Error as e:
        print(f"!!! خطای پایگاه داده در get_order_history: {e}")
        return []

def get_special_offers() -> list:
    return [
        {'name': 'کباب بختیاری', 'restaurant': 'رستوران اصیل', 'discount': '۱۵٪ تخفیف'},
        {'name': 'سالاد سزار', 'restaurant': 'کافه روما', 'offer': 'جدید در منو'},
        {'name': 'برگر ذغالی', 'restaurant': 'برگرلند', 'discount': '۲۰٪ تخفیف'}
    ]

def search_and_filter_food(query: str, max_price: float = None) -> List[dict]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        search_term = f"%{query}%"
        sql_query = "SELECT name, restaurant_name, price FROM foods WHERE (name LIKE ? OR category LIKE ?)"
        params = [search_term, search_term]
        if max_price is not None:
            sql_query += " AND price <= ?"
            params.append(max_price)
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        conn.close()
        if not results:
            return []
        return [{"name": name, "restaurant": restaurant, "price": price} for name, restaurant, price in results]
    except sqlite3.Error as e:
        print(f"!!! خطای پایگاه داده در search_and_filter_food: {e}")
        return [{"error": "متاسفم، مشکلی در اتصال به پایگاه داده منوی غذاها وجود دارد."}]

def view_cart() -> str:
    """این تابع زمانی فراخوانی می‌شود که کاربر می‌خواهد محتویات سبد خرید خود را ببیند."""
    # این تابع فقط یک سیگنال به UI می‌فرستد. منطق اصلی در app.py است.
    return "ACTION:VIEW_CART"