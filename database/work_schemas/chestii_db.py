import sqlite3

# Database path (update this if needed)
DATABASE_PATH = r"C:\Chestii\Programe\Sqlite\TabelMPP\navy.db"

def fetch_all_ships():
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Fetch all ships
        cursor.execute("SELECT * FROM ships")
        ships = cursor.fetchall()

        # Display the results
        if not ships:
            print("No ships found in the database.")
        else:
            print(f"\nTotal ships in database: {len(ships)}")
            print("\nShips list:")
            for ship in ships:
                print(f"- {ship[1]} (Built: {ship[2]}, Commissioned: {ship[3]}, Stricken: {ship[4]}, Country: {ship[5]})")

    except sqlite3.Error as e:
        print(f"Error retrieving ships: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fetch_all_ships()
