import os
import sys
from faker import Faker
import random
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Ship, SessionLocal, Base, engine

# Number of ships to generate
NUM_SHIPS = 100_000

# Countries and prefixes for variety
COUNTRIES = [
    "USA", "UK", "France", "Germany", "Japan", "Italy", "Spain", "Australia", "Canada", "Russia", "China", "Brazil", "India", "South Korea", "South Africa"
]
PREFIXES = [
    "USS", "HMS", "FS", "KMS", "IJN", "RN", "SNS", "HMAS", "HMCS", "RFS", "CNS", "BNS", "INS", "ROKS", "SAS"
]
TYPES = ["Battleship", "Cruiser", "Destroyer", "Submarine", "Carrier"]

fake = Faker()

def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    ships = []
    current_year = fake.date_this_century().year
    for i in tqdm(range(NUM_SHIPS), desc="Generating ships"):
        country = random.choice(COUNTRIES)
        prefix = PREFIXES[COUNTRIES.index(country)]
        ship_type = random.choice(TYPES)
        name = f"{prefix} {ship_type}-{i+1:06d}"
        year_built = random.randint(1850, 2023)
        commissioned = year_built + random.randint(0, 3)
        stricken = commissioned + random.randint(5, 50) if random.random() < 0.7 else None
        ship = Ship(
            name=name,
            year_built=year_built,
            commissioned_date=commissioned,
            stricken_date=stricken,
            country_of_origin=country
        )
        ships.append(ship)
        if len(ships) % 5000 == 0:
            session.bulk_save_objects(ships)
            session.commit()
            ships = []
    if ships:
        session.bulk_save_objects(ships)
        session.commit()
    session.close()
    print(f"Inserted {NUM_SHIPS} ships into the database.")

if __name__ == "__main__":
    main() 