ALTER TABLE cubecana_cubes
    ADD COLUMN card_list_views INT DEFAULT 0,
    ADD COLUMN page_views INT DEFAULT 0,
    ADD COLUMN drafts INT DEFAULT 0;

ALTER TABLE cubecana_cubes
    ADD INDEX popularity (popularity);