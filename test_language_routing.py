#!/usr/bin/env python3
"""
Test script to verify language-based routing for Supabase tables
"""

from langchain_chain import (
    detect_lang,
    get_table_name_for_language,
    get_vectorstore_for_language,
    get_total_documents_count,
    debug_vector_search
)

def test_language_routing():
    """Test the language detection and table routing"""

    print("=" * 60)
    print("LANGUAGE DETECTION AND TABLE ROUTING TEST")
    print("=" * 60)

    # Test cases
    test_queries = [
        ("How to create a purchase order?", "English"),
        ("What is the refund policy?", "English"),
        ("كيف أقوم بإنشاء أمر شراء؟", "Arabic"),
        ("ما هي سياسة الاسترداد؟", "Arabic"),
        ("How to reset password", "English"),
        ("كيفية إعادة تعيين كلمة المرور", "Arabic"),
    ]

    print("\n1. TESTING LANGUAGE DETECTION:")
    print("-" * 40)
    for query, expected_lang in test_queries:
        detected_lang = detect_lang(query)
        table_name = get_table_name_for_language(detected_lang)
        lang_label = "Arabic" if detected_lang == "ar" else "English"

        print(f"\nQuery: {query[:50]}...")
        print(f"  Expected: {expected_lang}")
        print(f"  Detected: {lang_label} ('{detected_lang}')")
        print(f"  Table: {table_name}")
        print(f"  ✓ Correct" if lang_label == expected_lang else f"  ✗ Incorrect")

    print("\n" + "=" * 60)
    print("2. DOCUMENT COUNTS BY TABLE:")
    print("-" * 40)
    try:
        counts = get_total_documents_count()
        print(f"English documents: {counts['english']}")
        print(f"Arabic documents: {counts['arabic']}")
        print(f"Total documents: {counts['total']}")
    except Exception as e:
        print(f"Error getting document counts: {e}")

    print("\n" + "=" * 60)
    print("3. TESTING VECTOR SEARCH ROUTING:")
    print("-" * 40)

    # Test English vector search
    print("\nEnglish query search test:")
    english_query = "How to create order"
    try:
        results = debug_vector_search(english_query, k=2)
        if results:
            for result in results:
                print(f"  - Table: {result['table']}")
                print(f"    Language: {result['language']}")
                print(f"    Content preview: {result['content'][:100]}...")
                break  # Show only first result
        else:
            print("  No results found")
    except Exception as e:
        print(f"  Error: {e}")

    # Test Arabic vector search
    print("\nArabic query search test:")
    arabic_query = "كيف أقوم بإنشاء طلب"
    try:
        results = debug_vector_search(arabic_query, k=2)
        if results:
            for result in results:
                print(f"  - Table: {result['table']}")
                print(f"    Language: {result['language']}")
                print(f"    Content preview: {result['content'][:100]}...")
                break  # Show only first result
        else:
            print("  No results found")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_language_routing()