from sheets_service import get_sheet_data
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_knowledgebase_docs():
    rows = get_sheet_data()
    docs = []
    for row in rows:
        text = f"Q: {row['Question']}\nA: {row['Answer']}"
        docs.append(Document(page_content=text))
    return docs

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_documents(docs)
