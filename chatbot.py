from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_chain import llm, vectorstore

# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    return_source_documents=True
)

# Chatbot response function
def get_chatbot_response(user_query: str):
    relevant_docs = vectorstore.similarity_search(user_query, k=2)
    if not relevant_docs:
        return "I don’t have this type of data or information. For more details, you may contact this person at +966542924317."
    result = qa_chain.invoke({"question": user_query})
    return result["answer"]
