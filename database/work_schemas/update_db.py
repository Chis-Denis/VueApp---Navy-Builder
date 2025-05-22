import sqlite3
import os

# Database path (same as in main.py)
DATABASE_PATH = r"C:\Chestii\Programe\Sqlite\TabelMPP\navy.db"

def update_database():
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Read and execute the SQL script
        with open('update_database.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)

        # Commit the changes
        conn.commit()
        print("Database updated successfully!")

        # Verify the changes
        cursor.execute("PRAGMA table_info(ships)")
        columns = cursor.fetchall()
        print("\nUpdated table structure:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")

    except sqlite3.Error as e:
        print(f"Error updating database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_database() 