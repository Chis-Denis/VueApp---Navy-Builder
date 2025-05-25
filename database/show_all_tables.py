from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./navy.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

inspector = inspect(engine)

def print_table(table_name):
    print(f"\nTable: {table_name}")
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    print(" | ".join(columns))
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT * FROM {table_name}")).fetchall()
        for row in rows:
            print(" | ".join(str(x) for x in row))

if __name__ == "__main__":
    tables = inspector.get_table_names()
    for table in tables:
        print_table(table) 