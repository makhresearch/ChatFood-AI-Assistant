import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List

# LangChain & LangGraph Core
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic.v1 import BaseModel, Field

# ابزارهای ماژولار ما
from tools import get_order_status, cancel_order, search_food, get_order_history, get_special_offers, search_and_filter_food, view_cart

# کتابخانه‌های جانبی
import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# ==================== Caching ====================
_embedding_model = None
_retriever = None
def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    return _embedding_model
def get_retriever():
    global _retriever
    if _retriever is None:
        db_path = os.path.join(os.getcwd(), "db")
        connection = lancedb.connect(db_path)
        embeddings = get_embedding_model()
        vectorstore = LanceDB(connection=connection, table_name="food_rag", embedding=embeddings)
        _retriever = vectorstore.as_retriever()
    return _retriever

# ==================== ابزارها (Tools) با Docstring کامل ====================
@tool
def get_order_status_tool(order_id: int) -> str:
    """وضعیت یک سفارش را با استفاده از شناسه آن برمی‌گرداند."""
    return get_order_status(order_id)

@tool
def cancel_order_tool(order_id: int) -> str:
    """یک سفارش را لغو می‌کند."""
    return cancel_order(order_id)

@tool
def simple_food_search_tool(query: str) -> list:
    """برای جستجوی ساده غذاها بر اساس نام یا دسته‌بندی استفاده می‌شود."""
    return search_food(query)

@tool
def advanced_food_search_tool(query: str, max_price: float = None) -> list:
    """برای جستجوی غذاها با شرایط خاص مانند نام، دسته‌بندی و حداکثر قیمت استفاده می‌شود."""
    return search_and_filter_food(query, max_price)

@tool
def knowledge_base_retriever_tool(query: str) -> List[Document]:
    """برای یافتن اطلاعات در مورد غذاها از پایگاه دانش محلی استفاده می‌کند."""
    return get_retriever().invoke(query)

@tool
def web_search_tool(query: str) -> str:
    """زمانی که دانش محلی کافی نیست، برای جستجوی اطلاعات در اینترنت استفاده می‌شود."""
    return DuckDuckGoSearchRun().run(query)

@tool
def view_cart_tool() -> str:
    """زمانی که کاربر می‌خواهد سبد خرید خود را ببیند، از این ابزار استفاده کن."""
    return view_cart()

# ==================== تنظیمات مشترک و State ====================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    tool_output: list | None
def should_continue(state: AgentState):
    return "end" if not state["messages"][-1].tool_calls else "continue"

# ==================== ایجنت‌ها ====================

# --- ایجنت مدیر سفارش ---
order_manager_tools = [get_order_status_tool, cancel_order_tool]
order_manager_model = llm.bind_tools(order_manager_tools)
def order_manager_node(state: AgentState):
    response = order_manager_model.invoke(state["messages"])
    return {"messages": [response], "tool_output": None}
order_manager_workflow = StateGraph(AgentState)
order_manager_workflow.add_node("agent", order_manager_node)
order_manager_workflow.add_node("tools", ToolNode(order_manager_tools))
order_manager_workflow.set_entry_point("agent")
order_manager_workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
order_manager_workflow.add_edge("tools", "agent")
order_manager_agent = order_manager_workflow.compile()

# --- ایجنت جستجوی ساده ---
food_search_tools = [simple_food_search_tool]
food_search_model = llm.bind_tools(food_search_tools)
def food_search_agent_node(state: AgentState):
    response = food_search_model.invoke(state["messages"])
    return {"messages": [response]}
def simple_tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    tool_output = simple_food_search_tool.invoke(tool_call['args'])
    string_output = "\n".join([f"نام: {i.get('name', '')}, رستوران: {i.get('restaurant', '')}, قیمت: {i.get('price', '')}" for i in tool_output])
    return {"messages": [ToolMessage(content=string_output, tool_call_id=tool_call['id'])], "tool_output": tool_output}
food_search_workflow = StateGraph(AgentState)
food_search_workflow.add_node("agent", food_search_agent_node)
food_search_workflow.add_node("tools", simple_tool_node)
food_search_workflow.set_entry_point("agent")
food_search_workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
food_search_workflow.add_edge("tools", "agent")
food_search_agent = food_search_workflow.compile()

# --- ایجنت جستجوی فیلتردار ---
filter_agent_tools = [advanced_food_search_tool]
filter_agent_model = llm.bind_tools(filter_agent_tools)
def filter_agent_node(state: AgentState):
    response = filter_agent_model.invoke(state["messages"])
    return {"messages": [response]}
def advanced_tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    tool_output = advanced_food_search_tool.invoke(tool_call['args'])
    string_output = "\n".join([f"نام: {i.get('name', '')}, رستوران: {i.get('restaurant', '')}, قیمت: {i.get('price', '')}" for i in tool_output])
    return {"messages": [ToolMessage(content=string_output, tool_call_id=tool_call['id'])], "tool_output": tool_output}
filter_agent_workflow = StateGraph(AgentState)
filter_agent_workflow.add_node("agent", filter_agent_node)
filter_agent_workflow.add_node("tools", advanced_tool_node)
filter_agent_workflow.set_entry_point("agent")
filter_agent_workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
filter_agent_workflow.add_edge("tools", "agent")
filter_agent = filter_agent_workflow.compile()

# --- ایجنت سبد خرید ---
cart_agent_tools = [view_cart_tool]
cart_agent_model = llm.bind_tools(cart_agent_tools)
def cart_agent_node(state: AgentState):
    response = cart_agent_model.invoke(state["messages"])
    return {"messages": [response], "tool_output": None}
cart_agent_workflow = StateGraph(AgentState)
cart_agent_workflow.add_node("agent", cart_agent_node)
cart_agent_workflow.add_node("tools", ToolNode(cart_agent_tools))
cart_agent_workflow.set_entry_point("agent")
cart_agent_workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
cart_agent_workflow.add_edge("tools", "agent")
cart_agent = cart_agent_workflow.compile()

# --- ایجنت اطلاعات (RAG) ---
rag_tools = [knowledge_base_retriever_tool, web_search_tool]
rag_model = llm.bind_tools(rag_tools)
def rag_agent_node(state: AgentState):
    response = rag_model.invoke(state["messages"])
    return {"messages": [response], "tool_output": None}
rag_workflow = StateGraph(AgentState)
rag_workflow.add_node("agent", rag_agent_node)
rag_workflow.add_node("tools", ToolNode(rag_tools))
rag_workflow.set_entry_point("agent")
rag_workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
rag_workflow.add_edge("tools", "agent")
rag_agent = rag_workflow.compile()

# --- ایجنت پیشنهاددهنده ---
async def recommendation_agent_node(state: AgentState):
    user_id = "user123"
    order_history, special_offers = get_order_history(user_id), get_special_offers()
    prompt = ChatPromptTemplate.from_template("شما یک دستیار فروش دوستانه هستید. با توجه به تاریخچه سفارش کاربر ({history}) و پیشنهادهای ویژه امروز ({offers})، یک پیام خوش‌آمدگویی جذاب و شخصی‌سازی شده بساز.")
    chain = prompt | llm
    response = await chain.ainvoke({"history": order_history, "offers": special_offers})
    return {"messages": [response], "tool_output": None}

# ==================== مسیریاب (Router) ====================
class RouterQuery(BaseModel):
    destination: str = Field(description="مقصد بعدی. گزینه‌ها: 'CartAgent', 'FilterAgent', 'OrderManager', 'FoodSearch', 'InformationAgent'")
prompt_text = """شما یک دستیار هوشمند مسیریاب هستید. وظیفه شما ارسال درخواست به یکی از ایجنت‌های زیر است:
'CartAgent': برای تمام درخواست‌های مربوط به مشاهده سبد خرید.
'FilterAgent': برای سوالاتی که شامل چندین شرط هستند، به خصوص اگر شرط قیمت داشته باشد.
'FoodSearch': برای سوالات ساده در مورد منو یا جستجوی یک آیتم خاص بدون شرط قیمت.
'OrderManager': برای تمام درخواست‌های مربوط به سفارش‌ها.
'InformationAgent': فقط برای سوالات عمومی و دانشنامه‌ای.
بر اساس آخرین پیام کاربر و تاریخچه، بهترین مقصد را انتخاب کن.
**تاریخچه گفتگو:** {history}
**آخرین پیام کاربر:** <user_input>{input}</user_input>"""
prompt = ChatPromptTemplate.from_template(prompt_text)
router_chain = prompt | llm.with_structured_output(RouterQuery)
def get_destination(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[:-1]])
    result = router_chain.invoke({"history": history_str, "input": last_message.content})
    print(f"\n--- مسیریاب (با حافظه) تصمیم گرفت: {result.destination} ---")
    return result.destination

# ==================== توابع ساخت گراف ====================
def get_recommendation_app():
    workflow = StateGraph(AgentState)
    workflow.add_node("recommend", recommendation_agent_node)
    workflow.set_entry_point("recommend")
    workflow.add_edge("recommend", END)
    return workflow.compile()

def get_app():
    super_workflow = StateGraph(AgentState)
    super_workflow.add_node("cart_agent", cart_agent)
    super_workflow.add_node("filter_agent", filter_agent)
    super_workflow.add_node("order_manager", order_manager_agent)
    super_workflow.add_node("food_search", food_search_agent)
    super_workflow.add_node("information_agent", rag_agent)
    super_workflow.add_conditional_edges("__start__", get_destination, {
        "CartAgent": "cart_agent",
        "FilterAgent": "filter_agent",
        "OrderManager": "order_manager",
        "FoodSearch": "food_search",
        "InformationAgent": "information_agent",
    })
    super_workflow.add_edge("cart_agent", END)
    super_workflow.add_edge("filter_agent", END)
    super_workflow.add_edge("order_manager", END)
    super_workflow.add_edge("food_search", END)
    super_workflow.add_edge("information_agent", END)
    return super_workflow.compile()

if __name__ == "__main__":
    print("فایل main.py با موفقیت بارگذاری شد و آماده ایمپورت شدن توسط app.py است.")