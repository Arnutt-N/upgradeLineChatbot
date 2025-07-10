import sqlite3
import os

def check_database():
    db_path = "chatbot.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== DATABASE ANALYSIS ===")
        print(f"Database file: {db_path}")
        print()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("TABLES:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
        print()
        
        # Analyze each table
        for table in tables:
            table_name = table[0]
            print(f"=== TABLE: {table_name} ===")
            
            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("COLUMNS:")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                default = f" DEFAULT {col[4]}" if col[4] else ""
                print(f"  - {col_name}: {col_type} ({nullable}){default}")
            
            # Get count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"RECORDS: {count}")
            
            # Sample data (first 3 records)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print("SAMPLE DATA:")
                for i, row in enumerate(sample_data, 1):
                    print(f"  Row {i}: {row}")
            
            print()
        
        conn.close()
        print("=== ANALYSIS COMPLETED ===")
        
    except Exception as e:
        print(f"Error analyzing database: {e}")

if __name__ == "__main__":
    check_database()
