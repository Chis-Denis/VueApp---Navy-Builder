import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, Ship

def delete_ships():
    try:
        # Get database session
        db = next(get_db())
        
        # Find all ships with ID >= 102
        ships_to_delete = db.query(Ship).filter(Ship.id >= 100).all()
        
        # Get count of ships to be deleted
        count = len(ships_to_delete)
        
        # Delete the ships
        db.query(Ship).filter(Ship.id >= 100).delete()
        
        # Commit the changes
        db.commit()
        
        print(f"Successfully deleted {count} ships with ID >= 100")
        
    except Exception as e:
        print(f"Error deleting ships: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_ships()