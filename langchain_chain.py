import os
import re
from typing import List, Dict, Any, Optional

from supabase import create_client
from langchain_community.vectorstores import SupabaseVectorStore
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_groq import ChatGroq  # Using Groq for the LLM instead of OpenAI
from langchain.schema import HumanMessage, Document
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader

# Arabic processing and language detection
from pyarabic import araby
from langdetect import detect, DetectorFactory
import requests

# Ensure deterministic language detection
DetectorFactory.seed = 0

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# English table configuration (default)
SUPABASE_TABLE_NAME = os.getenv("SUPABASE_TABLE_NAME", "documents").strip("'\"")
SUPABASE_MATCH_RPC = os.getenv("SUPABASE_MATCH_RPC", "match_documents").strip("'\"")

# Arabic table configuration
ARABIC_SUPABASE_TABLE_NAME = os.getenv("ARABIC_SUPABASE_TABLE_NAME", "arabic_documents").strip("'\"")
ARABIC_SUPABASE_MATCH_RPC = os.getenv("ARABIC_SUPABASE_MATCH_RPC", "match_arabic_documents").strip("'\"")

# Embedding model name (default to multilingual for Arabic support)
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

# Google Translate API (force Arabic output)
GOOGLE_TRANSLATE_API_KEY = (
    os.getenv("GOOGLE_TRANSLATE_API_KEY")
    or os.getenv("GOOGLE_API_KEY")  # fallback to common name
)
FORCE_ARABIC_OUTPUT = os.getenv("FORCE_ARABIC_OUTPUT", "true").lower() in {"1", "true", "yes"}

# -------------------------------
# Initialize Supabase client
# -------------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# Initialize Groq LLM
# -------------------------------
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-70b-versatile"  # Updated to new model after llama3-70b-8192 deprecation
)

# -------------------------------
# Embeddings and Vector Store (multilingual for Arabic)
# -------------------------------
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Create vector stores for both languages
vectorstore_english = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name=SUPABASE_TABLE_NAME,
    query_name=SUPABASE_MATCH_RPC,
)

vectorstore_arabic = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name=ARABIC_SUPABASE_TABLE_NAME,
    query_name=ARABIC_SUPABASE_MATCH_RPC,
)

# Default vectorstore for backward compatibility
vectorstore = vectorstore_english

def get_vectorstore_for_language(lang: str) -> SupabaseVectorStore:
    """Get the appropriate vectorstore based on language."""
    if lang == "ar":
        return vectorstore_arabic
    return vectorstore_english

def get_table_name_for_language(lang: str) -> str:
    """Get the appropriate table name based on language."""
    if lang == "ar":
        return ARABIC_SUPABASE_TABLE_NAME
    return SUPABASE_TABLE_NAME

# -------------------------------
# Arabic language utilities
# -------------------------------

def is_arabic_text(text: str) -> bool:
    """Detect presence of Arabic letters."""
    return bool(re.search(r"[\u0600-\u06FF]", text or ""))


def detect_lang(text: str) -> str:
    """Detect language - if ANY Arabic character exists, treat as Arabic."""
    # IMPORTANT: If even a single Arabic character is present, use Arabic route
    if is_arabic_text(text or ""):
        return "ar"

    # Otherwise, try langdetect for other cases
    try:
        lang = detect(text or "")
        if lang and lang.startswith("ar"):
            return "ar"
        return "en"
    except Exception:
        return "en"  # Default to English if no Arabic detected


def normalize_arabic(text: str) -> str:
    """Basic Arabic normalization pipeline using PyArabic utilities."""
    if not text:
        return text
    normalized = araby.normalize_hamza(text)
    normalized = araby.strip_tatweel(normalized)
    normalized = araby.strip_tashkeel(normalized)
    # Note: unshape is not available in newer versions of pyarabic
    # normalized = araby.unshape(normalized)
    return normalized.strip()


def translate_to_arabic(text: str) -> str:
    """Translate given text to Arabic using Google Cloud Translation v2."""
    if not text:
        return text
    if not GOOGLE_TRANSLATE_API_KEY:
        print("Google Translate API key not configured")
        return text
    try:
        endpoint = "https://translation.googleapis.com/language/translate/v2"
        params = {"key": GOOGLE_TRANSLATE_API_KEY}
        form = {"q": text, "target": "ar", "format": "text"}
        resp = requests.post(endpoint, params=params, data=form, timeout=15)
        if not resp.ok:
            resp = requests.post(endpoint, params=params, json=form, timeout=15)
        resp.raise_for_status()
        payload = resp.json() or {}
        translated = (
            payload.get("data", {})
            .get("translations", [{}])[0]
            .get("translatedText")
        )
        return translated or text
    except requests.exceptions.HTTPError as e:
        if "403" in str(e):
            print(f"Google Translate API key may be invalid or disabled: {e}")
        else:
            print(f"Translate-to-Arabic HTTP error: {e}")
        return text
    except Exception as e:
        print(f"Translate-to-Arabic failed: {e}")
        return text


def ensure_arabic_output(text: str) -> str:
    """If configured, translate output to Arabic. Otherwise return as-is."""
    if not FORCE_ARABIC_OUTPUT:
        return text
    if is_arabic_text(text):
        return text
    try:
        lang = detect(text)
        if lang and lang.startswith("ar"):
            return text
    except Exception:
        pass
    return translate_to_arabic(text)

# -------------------------------
# Small talk responses
# -------------------------------
SMALL_TALK = {
    "hi": "Hello! How can I assist you with Tijarah360 today?",
    "hello": "Hi there! How can I help you with Tijarah360?",
    "how are you": "I'm just a bot, but I'm functioning perfectly! How about you?",
    "what's up": "I'm here to help you with Tijarah360. How can I assist?",
    "hey": "Hey! How can I assist you today?",
    "good morning": "Good morning! How can I help you with Tijarah360 today?",
    "good afternoon": "Good afternoon! How can I assist you with Tijarah360?",
    "good evening": "Good evening! How can I help you with Tijarah360?",
    "bye": "Goodbye! Feel free to return if you need help with Tijarah360.",
    "goodbye": "Goodbye! Have a great day!",
    "thanks": "You're welcome! Is there anything else I can help you with regarding Tijarah360?",
    "thank you": "You're welcome! Is there anything else I can help you with regarding Tijarah360?",
    "ok": "Great! How can I assist you with Tijarah360?",
    "okay": "Great! How can I assist you with Tijarah360?",
    "yes": "Great! What would you like to know about Tijarah360?",
    "no": "No problem! Let me know if you need help with Tijarah360 later.",
    "maybe": "Take your time! I'm here when you need help with Tijarah360.",
    "sure": "Perfect! How can I help you with Tijarah360?",
    "alright": "Alright! What can I help you with regarding Tijarah360?"
}

SIMPLE_GREETINGS = [
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
    "how are you", "what's up", "bye", "goodbye", "thanks", "thank you",
    "ok", "okay", "yes", "no", "maybe", "sure", "alright"
]

VERY_SHORT_GREETINGS = [
    "hi", "hello", "hey", "bye", "ok", "okay", "yes", "no", "maybe", "sure", "alright"
]

def is_simple_greeting(query: str) -> bool:
    query_lower = query.strip().lower()
    query_clean = query_lower.replace('?', '').replace('!', '').replace('.', '').strip()
    if query_clean in SMALL_TALK:
        return True
    words = query_clean.split()
    if len(words) <= 2:
        if all(word in VERY_SHORT_GREETINGS for word in words):
            return True
        if len(query_clean) <= 10:
            return True
    if query_clean in SIMPLE_GREETINGS:
        return True
    greeting_patterns = ['good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'thank you']
    for pattern in greeting_patterns:
        if pattern == query_clean:
            return True
    if query_clean in ['how r u', 'how are u', 'how r you', 'how are you']:
        return True
    return False

# -------------------------------
# Functions
# -------------------------------

def load_sheet_to_supabase(csv_path: str, language: str = "en") -> SupabaseVectorStore:
    loader = CSVLoader(file_path=csv_path, source_column="Question", encoding="utf-8")
    documents = loader.load()

    # Get appropriate table and RPC based on language
    if language == "ar":
        table_name = ARABIC_SUPABASE_TABLE_NAME
        match_rpc = ARABIC_SUPABASE_MATCH_RPC
        vectorstore_to_return = vectorstore_arabic
    else:
        table_name = SUPABASE_TABLE_NAME
        match_rpc = SUPABASE_MATCH_RPC
        vectorstore_to_return = vectorstore_english

    SupabaseVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        client=supabase,
        table_name=table_name,
        query_name=match_rpc,
        chunk_size=500,
    )
    return vectorstore_to_return

def add_texts_to_supabase(texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
    # Separate texts by language
    arabic_texts: List[str] = []
    english_texts: List[str] = []
    arabic_metadata: List[Dict[str, Any]] = []
    english_metadata: List[Dict[str, Any]] = []

    for i, t in enumerate(texts):
        if is_arabic_text(t):
            arabic_texts.append(normalize_arabic(t))
            if metadatas:
                arabic_metadata.append(metadatas[i] if i < len(metadatas) else {})
        else:
            english_texts.append(t)
            if metadatas:
                english_metadata.append(metadatas[i] if i < len(metadatas) else {})

    # Add to appropriate vectorstores
    if arabic_texts:
        vectorstore_arabic.add_texts(texts=arabic_texts, metadatas=arabic_metadata or [])
    if english_texts:
        vectorstore_english.add_texts(texts=english_texts, metadatas=english_metadata or [])

def create_and_store_embedding(text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # Detect language and use appropriate vectorstore
    if is_arabic_text(text):
        value = normalize_arabic(text)
        vectorstore_arabic.add_texts(texts=[value], metadatas=[metadata or {}])
    else:
        value = text
        vectorstore_english.add_texts(texts=[value], metadatas=[metadata or {}])
    return {"status": "ok", "stored": 1}

def get_documents_count(language: Optional[str] = None) -> int:
    """Get document count. If language is None, returns English count for backward compatibility."""
    try:
        table_name = get_table_name_for_language(language or "en")
        resp = supabase.table(table_name).select("id", count="exact").limit(0).execute()
        if hasattr(resp, "count") and isinstance(resp.count, int):
            return resp.count
        return len(resp.data or [])
    except Exception:
        return 0

def get_total_documents_count() -> Dict[str, int]:
    """Get document count for both English and Arabic tables."""
    return {
        "english": get_documents_count("en"),
        "arabic": get_documents_count("ar"),
        "total": get_documents_count("en") + get_documents_count("ar")
    }

def query_supabase(query: str) -> Optional[str]:
    try:
        # Detect language and use appropriate table
        lang = detect_lang(query)
        table_name = get_table_name_for_language(lang)

        query_processed = normalize_arabic(query) if lang == "ar" else query
        search_results = (
            supabase
            .table(table_name)
            .select("content, metadata, question, answer")
            .ilike("content", f"%{query_processed}%")
            .execute()
        )
        if getattr(search_results, "data", None) and search_results.data:
            first = search_results.data[0]
            return (
                first.get("content")
                or first.get("answer")
                or first.get("metadata", {}).get("question", "")
                or first.get("question")
            )
    except Exception as e:
        print(f"Primary fallback search failed: {e}")
    return None

def debug_vector_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    try:
        # Detect language and use appropriate vectorstore
        lang = detect_lang(query)
        vs = get_vectorstore_for_language(lang)

        docs: List[Document] = vs.similarity_search(query, k=k)
        results = []
        for i, doc in enumerate(docs):
            score = doc.metadata.get("score", 1.0)
            results.append({
                "rank": i + 1,
                "score": score,
                "language": lang,
                "table": get_table_name_for_language(lang),
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            })
        return results
    except Exception as e:
        print(f"Debug vector search failed: {e}")
        return []

def get_rag_response(query: str, similarity_threshold: float = 0.3) -> str:
    query_lower = query.strip().lower()
    query_clean = query_lower.replace('?', '').replace('!', '').replace('.', '').strip()

    if query_clean in SMALL_TALK:
        print(f"Using small talk response for: '{query}'")
        return SMALL_TALK[query_clean]

    if is_simple_greeting(query):
        print(f"Using greeting response for: '{query}'")
        return "Hello! I'm here to help you with Tijarah360. How can I assist you today?"

    print(f"Performing vector search for: '{query}'")
    try:
        # Detect language and use appropriate vectorstore
        lang = detect_lang(query)
        vs = get_vectorstore_for_language(lang)
        print(f"Using {'Arabic' if lang == 'ar' else 'English'} vectorstore (table: {get_table_name_for_language(lang)})")

        query_for_search = normalize_arabic(query) if lang == "ar" else query
        docs = vs.similarity_search(query_for_search, k=1)
        if docs:
            print(f"Found FAQ match: {docs[0].page_content[:100]}...")
            return ensure_arabic_output(docs[0].page_content)
    except Exception as e:
        print(f"Vector search failed: {e}")

    try:
        lang = detect_lang(query)
        system_prompt = (
            "You are a helpful assistant. Reply concisely in Arabic."
            if lang == "ar"
            else "You are a helpful assistant. Reply concisely in English."
        )
        messages = [HumanMessage(content=f"{system_prompt}\n\nUser: {query}")]
        llm_response = llm.invoke(messages)
        if llm_response and len(str(llm_response.content).strip()) > 0:
            response_content = str(llm_response.content)
            if not response_content.startswith("ID:"):
                print(f"Using Groq LLM response: {response_content[:100]}...")
                return ensure_arabic_output(response_content)
    except Exception as e:
        print("Groq LLM failed:", e)

    return ensure_arabic_output("I don't have this type of data or information. For more details, contact +966542924317.")

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    # Example usage with language-specific loading
    # For Arabic data:
    # arabic_csv_path = r"C:\Users\adila\Desktop\tijarah360_ai_agent\ai-chatbot-app\src\backend\result.csv"
    # load_sheet_to_supabase(arabic_csv_path, language="ar")

    # For English data:
    # english_csv_path = r"C:\Users\adila\Desktop\tijarah360_ai_agent\ai-chatbot-app\src\backend\faq_data.csv"
    # load_sheet_to_supabase(english_csv_path, language="en")

    # Test with English queries
    print("Testing English query:")
    print(get_rag_response("How to create a purchase order?"))

    # Test with Arabic queries
    print("\nTesting Arabic query:")
    print(get_rag_response("كيف أقوم بإنشاء أمر شراء؟"))

    # Get document counts
    print("\nDocument counts:")
    print(get_total_documents_count())
