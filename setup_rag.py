import os
import lancedb
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings  # نسخه‌ی جدید و توصیه‌شده

def setup_vector_database():
    # ۱. بارگذاری اسناد
    loader = TextLoader('food_knowledge.txt', encoding='utf-8')
    documents = loader.load()

    # ۲. تقسیم اسناد به قطعات کوچکتر (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # ۳. انتخاب مدل امبدینگ (متن → وکتور)
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # ۴. تعیین مسیر دیتابیس داخل پروژه
    db_path = os.path.join(os.getcwd(), "db")  # پوشه "db" در پروژه
    connection = lancedb.connect(db_path)

    # ۵. ساخت پایگاه داده وکتوری
    LanceDB.from_documents(
        docs,
        embeddings,
        connection=connection,
        table_name="food_rag"
    )
    
    print(f"✅ پایگاه داده وکتوری با موفقیت ایجاد شد در مسیر: {db_path}")

if __name__ == '__main__':
    setup_vector_database()
