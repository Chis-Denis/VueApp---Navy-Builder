-- Script to delete all ships with ID higher than 1000 from the database
-- This should be run with caution and ideally after backing up the database

-- Begin transaction
BEGIN TRANSACTION;

-- Count total ships in the database (for information purposes)
SELECT COUNT(*) as total_ships FROM ships;

-- Count ships that will be deleted
SELECT COUNT(*) as ships_to_delete FROM ships WHERE id > 100;

-- Delete all ships with ID > 1000
DELETE FROM ships 
WHERE id > 100;

-- Commit the transaction
COMMIT;

-- Print a message (this is for SQLite clients that support the .echo command)
-- .echo Deleted all ships with ID > 1000 