CREATE TABLE cubecana_draft(
    pk INT NOT NULL AUTO_INCREMENT,
    draft_id binary(16) NOT NULL,
    start_time_epoch_seconds INT,
    game_mode VARCHAR(32) NOT NULL,
    draft_source_type VARCHAR(32) NOT NULL,
    draft_source_id BINARY(16) NOT NULL,  -- cube_id or retail_set_id

    end_time_epoch_seconds INT,
    draft_status VARCHAR(32) NOT NULL,

    PRIMARY KEY(pk),
    UNIQUE(draft_id)
);