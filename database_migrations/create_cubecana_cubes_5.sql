-- Migration to support emojis in cube descriptions and other text fields
-- Convert table and relevant columns to utf8mb4 charset to support 4-byte UTF-8 characters (emojis)

ALTER TABLE cubecana_cubes CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Explicitly update the columns that may contain emojis
ALTER TABLE cubecana_cubes 
    MODIFY COLUMN name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY COLUMN link varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY COLUMN author varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY COLUMN edit_secret varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY COLUMN featured_card_printing varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY COLUMN cube_description varchar(4096) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY COLUMN card_id_to_count TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
