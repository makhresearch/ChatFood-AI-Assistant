import chainlit as cl
import random
from main import get_app, get_recommendation_app
from langchain_core.messages import HumanMessage, AIMessage

# ==================== Action Callbacks ====================

@cl.action_callback("add_to_cart")
async def on_add_to_cart(action: cl.Action):
    """زمانی اجرا می‌شود که کاربر روی دکمه 'افزودن به سبد خرید' کلیک می‌کند."""
    food_name = action.payload.get("food_name")
    cart = cl.user_session.get("cart", [])
    cart.append(food_name)
    cl.user_session.set("cart", cart)

    await cl.Message(
        content=f"✅ **{food_name}** با موفقیت به سبد خرید اضافه شد!\nشما در حال حاضر **{len(cart)}** آیتم در سبد دارید."
    ).send()

@cl.action_callback("offer_response")
async def on_offer_response(action: cl.Action):
    """زمانی اجرا می‌شود که کاربر به پیشنهاد ویژه پاسخ می‌دهد."""
    user_choice = action.payload.get("value")
    if user_choice == "accept":
        await cl.Message(
            content="عالی! شما به پیشنهاد ویژه علاقه‌مند شدید. می‌توانید غذای مورد نظر را جستجو کرده و سفارش دهید."
        ).send()
    else:
        await cl.Message(
            content="متوجه شدم. چطور می‌توانم به شکل دیگری کمکتان کنم؟"
        ).send()

# ==================== توابع کمکی ====================

def is_food_list_response(tool_output: list | None) -> bool:
    """تشخیص می‌دهد آیا خروجی ابزار، لیستی از غذاهاست."""
    return isinstance(tool_output, list) and len(tool_output) > 0 and isinstance(tool_output[0], dict) and "name" in tool_output[0]

# ==================== شروع چت ====================

@cl.on_chat_start
async def on_chat_start():
    app = get_app()
    cl.user_session.set("app", app)
    cl.user_session.set("message_history", [])
    cl.user_session.set("cart", [])

    message_history = cl.user_session.get("message_history")

    # ایجاد پیام پیشنهاد ویژه
    if random.choice([True, True]):
        processing_msg = cl.Message(content="لحظه‌ای لطفاً، در حال آماده کردن یک پیشنهاد ویژه برای شما هستم...")
        await processing_msg.send()

        recommendation_app = get_recommendation_app()
        inputs = {"messages": [HumanMessage(content="یک پیشنهاد برای user123 بساز")]}
        proactive_message_content = ""

        async for event in recommendation_app.astream(inputs):
            for key, value in event.items():
                if "messages" in value:
                    proactive_message_content = value["messages"][-1].content

        await processing_msg.remove()

        actions = [
            cl.Action(name="offer_response", label="😍 بله، عالیه!", payload={"value": "accept"}),
            cl.Action(name="offer_response", label="🤔 نه، ممنون", payload={"value": "reject"}),
        ]

        await cl.Message(content=proactive_message_content, actions=actions).send()
        message_history.append(AIMessage(content=proactive_message_content))
        cl.user_session.set("message_history", message_history)
    else:
        welcome_message = "سلام! من ربات ChatFood هستم. چطور می‌توانم امروز به شما کمک کنم؟"
        await cl.Message(content=welcome_message).send()
        message_history.append(AIMessage(content=welcome_message))
        cl.user_session.set("message_history", message_history)

# ==================== دریافت پیام از کاربر ====================

@cl.on_message
async def on_message(message: cl.Message):
    app = cl.user_session.get("app")
    message_history = cl.user_session.get("message_history")
    message_history.append(HumanMessage(content=message.content))
    inputs = {"messages": message_history, "tool_output": None}

    final_response_content = ""
    food_items = None

    async with cl.Step(type="tool") as step:
        step.name = "Processing Agent"
        step.input = message.content
        await step.send()

        try:
            current_node = ""
            async for event in app.astream(inputs):
                for key, value in event.items():
                    current_node = key
                    step.output = f"🔄 در حال پردازش: {current_node.replace('_', ' ').title()}..."
                    await step.update()

                    if "messages" in value:
                        last_message = value["messages"][-1]
                        if last_message.type == "ai" and not last_message.tool_calls and getattr(last_message, 'content', ''):
                            final_response_content = last_message.content

                    if value.get("tool_output"):
                        food_items = value.get("tool_output")

            if final_response_content:
                message_history.append(AIMessage(content=final_response_content))
            cl.user_session.set("message_history", message_history)
            step.output = "✅ انجام شد!"
            await step.update()

        except Exception as e:
            print(f"!!! خطای اجرای گراف: {e}")
            final_response_content = "متاسفم، یک خطای پیش‌بینی نشده رخ داد."
            step.output = f"❌ Error: {e}"
            await step.update()

    # ==================== نمایش پاسخ ====================
    if current_node == "cart_agent":
        cart = cl.user_session.get("cart", [])
        if not cart:
            await cl.Message(content="🛒 سبد خرید شما خالی است.").send()
        else:
            cart_content = "\n".join([f"- **{item}**" for item in cart])
            await cl.Message(content=f"🛒 اقلام موجود در سبد خرید شما:\n{cart_content}").send()

    elif is_food_list_response(food_items):
        # نمایش هر آیتم با دکمه افزودن به سبد خرید
        for item in food_items:
            await cl.Message(
                content=f"🍽 **{item['name']}**\nرستوران: {item['restaurant']}\nقیمت: {float(item['price']):,} تومان",
                actions=[
                    cl.Action(
                        name="add_to_cart",
                        label="🛒 افزودن به سبد خرید",
                        payload={"food_name": item["name"]}
                    )
                ]
            ).send()

    elif final_response_content:
        await cl.Message(content=final_response_content).send()