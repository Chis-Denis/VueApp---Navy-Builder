-- Add new columns to the ships table
ALTER TABLE ships ADD COLUMN commissioned_date INTEGER;
ALTER TABLE ships ADD COLUMN stricken_date INTEGER;
ALTER TABLE ships ADD COLUMN country_of_origin TEXT;

-- Update existing records with some sample data (optional)
-- UPDATE ships SET commissioned_date = 1945, stricken_date = 1970, country_of_origin = 'USA' WHERE id = 1; 