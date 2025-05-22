#!/usr/bin/env python3
"""
Script to delete all ships with ID higher than 1000 from the database.
This can be helpful for maintenance or performance optimization.
"""

import sys
import os

# Add the parent directory to the path so we can import from database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, Ship
from sqlalchemy import func

def delete_ships_above_id(threshold_id=100):
    """
    Delete all ships with ID higher than the specified threshold.
    
    Args:
        threshold_id (int): ID threshold, ships with ID > this will be deleted (default: 100)
    """
    try:
        # Get database session
        db = next(get_db())
        
        # Get total count of ships in the database
        total_ships = db.query(func.count(Ship.id)).scalar()
        print(f"Total ships in database: {total_ships}")
        
        # Count ships to be deleted
        ships_to_delete_count = db.query(func.count(Ship.id)).filter(Ship.id > threshold_id).scalar()
        print(f"Found {ships_to_delete_count} ships with ID > {threshold_id}")
        
        if ships_to_delete_count == 0:
            print(f"No ships with ID > {threshold_id} to delete.")
            return
        
        # Delete ships with ID > threshold
        result = db.query(Ship).filter(Ship.id > threshold_id).delete()
        
        # Commit the changes
        db.commit()
        
        print(f"Successfully deleted {result} ships with ID > {threshold_id}")
        
    except Exception as e:
        print(f"Error deleting ships: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Check if a custom threshold was provided
    if len(sys.argv) > 1:
        try:
            threshold = int(sys.argv[1])
            delete_ships_above_id(threshold)
        except ValueError:
            print(f"Invalid threshold ID: {sys.argv[1]}. Using default 100.")
            delete_ships_above_id()
    else:
        delete_ships_above_id() 