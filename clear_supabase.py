import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# English table configuration
SUPABASE_TABLE_NAME = os.getenv("SUPABASE_TABLE_NAME", "documents").strip("'\"")

# Arabic table configuration
ARABIC_SUPABASE_TABLE_NAME = os.getenv("ARABIC_SUPABASE_TABLE_NAME", "arabic_documents").strip("'\"")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def clear_supabase_table(table_name=None, language=None):
    """Clear all documents from the Supabase vector table

    Args:
        table_name: Specific table name to clear (overrides language parameter)
        language: 'en' for English, 'ar' for Arabic, 'both' for both tables
    """
    # Determine which tables to clear
    if table_name:
        tables_to_clear = [(table_name, table_name)]
    elif language == "ar":
        tables_to_clear = [("Arabic", ARABIC_SUPABASE_TABLE_NAME)]
    elif language == "both":
        tables_to_clear = [("English", SUPABASE_TABLE_NAME), ("Arabic", ARABIC_SUPABASE_TABLE_NAME)]
    else:  # Default to English for backward compatibility
        tables_to_clear = [("English", SUPABASE_TABLE_NAME)]

    overall_success = True

    for table_label, table in tables_to_clear:
        print(f"\n🧹 Clearing {table_label} table ({table})...")
        try:
            # First, get all document IDs
            result = supabase.table(table).select("id").execute()

            if not result.data:
                print(f"ℹ️ {table_label} table is already empty")
                continue

            # Delete each document by its ID
            deleted_count = 0
            for doc in result.data:
                try:
                    doc_id = doc['id']
                    supabase.table(table).delete().eq("id", doc_id).execute()
                    deleted_count += 1
                    print(f"🗑️ Deleted document {doc_id} from {table_label} table")
                except Exception as e:
                    print(f"⚠️ Failed to delete document {doc_id} from {table_label} table: {e}")

            print(f"✅ Successfully deleted {deleted_count} documents from {table_label} table")

        except Exception as e:
            print(f"❌ Error clearing {table_label} table: {e}")
            overall_success = False

    return overall_success

def check_table_status(language=None):
    """Check the current status of the table(s)

    Args:
        language: 'en' for English, 'ar' for Arabic, 'both' for both tables
    """
    if language == "ar":
        tables_to_check = [("Arabic", ARABIC_SUPABASE_TABLE_NAME)]
    elif language == "both":
        tables_to_check = [("English", SUPABASE_TABLE_NAME), ("Arabic", ARABIC_SUPABASE_TABLE_NAME)]
    else:  # Default to English
        tables_to_check = [("English", SUPABASE_TABLE_NAME)]

    total_count = 0
    for table_label, table in tables_to_check:
        try:
            result = supabase.table(table).select("id", count="exact").limit(0).execute()
            count = result.count if hasattr(result, 'count') else len(result.data or [])
            print(f"📊 {table_label} table ({table}) document count: {count}")
            total_count += count
        except Exception as e:
            print(f"❌ Error checking {table_label} table: {e}")

    if language == "both":
        print(f"📊 Total documents across both tables: {total_count}")

    return total_count

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--arabic", "-ar", "arabic", "ar"]:
            language = "ar"
        elif arg in ["--both", "-b", "both", "all"]:
            language = "both"
        elif arg in ["--english", "-en", "english", "en"]:
            language = "en"
        else:
            print("Usage: python clear_supabase.py [--english|--arabic|--both]")
            print("  --english, -en: Clear English documents table")
            print("  --arabic, -ar: Clear Arabic documents table")
            print("  --both, -b: Clear both tables")
            print("  (default: English table)")
            sys.exit(1)
    else:
        language = "en"  # Default to English

    print(f"🧹 Clearing Supabase vector database...")

    # Check current status
    current_count = check_table_status(language)

    if current_count > 0:
        # Clear the table(s)
        if clear_supabase_table(language=language):
            print("\n✅ Database cleared successfully!")
            # Verify it's empty
            new_count = check_table_status(language)
            if new_count == 0:
                print("🎉 Database is now empty and ready for fresh data!")
            else:
                print(f"⚠️ Database still has {new_count} documents")
        else:
            print("❌ Failed to clear database")
    else:
        print("ℹ️ Database is already empty")
