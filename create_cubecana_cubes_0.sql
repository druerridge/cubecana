CREATE TABLE cubecana_cubes(
    pk INT NOT NULL AUTO_INCREMENT,
    id binary(16) NOT NULL,
    name varchar(255),
    tags JSON,
    link varchar(2048),
    author varchar(255),
    last_updated_epoch_seconds INT,
    edit_secret varchar(255),
    boosters_per_player INT,
    cards_per_booster INT,
    set_card_colors INT,
    color_balance_packs INT,
    with_replacement INT,
    popularity INT,
    card_id_to_count Text,
    PRIMARY KEY(pk),
    UNIQUE(id)
);