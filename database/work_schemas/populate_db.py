import sqlite3

# Database path (same as in main.py)
DATABASE_PATH = r"C:\Chestii\Programe\Sqlite\TabelMPP\navy.db"

# Example ships data
ships_data = [
    {
        "name": "USS Enterprise (CVN-65)",
        "year_built": 1960,
        "commissioned_date": 1961,
        "stricken_date": 2017,
        "country_of_origin": "USA"
    },
    {
        "name": "HMS Victory",
        "year_built": 1765,
        "commissioned_date": 1778,
        "stricken_date": 1922,
        "country_of_origin": "United Kingdom"
    },
    {
        "name": "Bismarck",
        "year_built": 1939,
        "commissioned_date": 1940,
        "stricken_date": 1941,
        "country_of_origin": "Germany"
    },
    {
        "name": "Yamato",
        "year_built": 1940,
        "commissioned_date": 1941,
        "stricken_date": 1945,
        "country_of_origin": "Japan"
    },
    {
        "name": "USS Missouri (BB-63)",
        "year_built": 1944,
        "commissioned_date": 1944,
        "stricken_date": 1995,
        "country_of_origin": "USA"
    },
    {
        "name": "HMS Dreadnought",
        "year_built": 1906,
        "commissioned_date": 1906,
        "stricken_date": 1923,
        "country_of_origin": "United Kingdom"
    },
    {
        "name": "Richelieu",
        "year_built": 1939,
        "commissioned_date": 1940,
        "stricken_date": 1968,
        "country_of_origin": "France"
    },
    {
        "name": "Vittorio Veneto",
        "year_built": 1937,
        "commissioned_date": 1940,
        "stricken_date": 1948,
        "country_of_origin": "Italy"
    },
    {
        "name": "Sovetsky Soyuz",
        "year_built": 1938,
        "commissioned_date": None,
        "stricken_date": 1948,
        "country_of_origin": "Soviet Union"
    },
    {
        "name": "HMS Hood",
        "year_built": 1918,
        "commissioned_date": 1920,
        "stricken_date": 1941,
        "country_of_origin": "United Kingdom"
    }
]

def populate_database():
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Ensure the ships table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                year_built INTEGER,
                commissioned_date INTEGER,
                stricken_date INTEGER,
                country_of_origin TEXT
            )
        """)

        # Insert new ships, ignoring duplicates
        for ship in ships_data:
            cursor.execute("""
                INSERT OR IGNORE INTO ships (name, year_built, commissioned_date, stricken_date, country_of_origin)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ship["name"],
                ship["year_built"],
                ship["commissioned_date"],
                ship["stricken_date"],
                ship["country_of_origin"]
            ))

        # Commit the changes
        conn.commit()
        print("Database updated successfully with new ships!")

        # Verify the data
        cursor.execute("SELECT * FROM ships")
        ships = cursor.fetchall()
        print(f"\nTotal ships in database: {len(ships)}")
        print("\nFirst few ships:")
        for ship in ships[:3]:
            print(f"- {ship[1]} (Built: {ship[2]}, Country: {ship[5]})")

    except sqlite3.Error as e:
        print(f"Error populating database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    populate_database()
