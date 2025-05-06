UPDATE cubecana_cubes SET tags = JSON_UNQUOTE(tags) WHERE JSON_VALID(tags) AND JSON_TYPE(tags) = 'STRING';

UPDATE cubecana_cubes
SET 
	tags = JSON_REMOVE(tags, JSON_UNQUOTE(JSON_SEARCH(tags, 'one', 'Powered'))),
	power_band = 'MAX'
WHERE JSON_VALID(tags) AND JSON_TYPE(tags) = 'ARRAY' AND JSON_SEARCH(tags, 'one', 'Powered') IS NOT NULL;

UPDATE cubecana_cubes
SET 
	tags = JSON_REMOVE(tags, JSON_UNQUOTE(JSON_SEARCH(tags, 'one', 'Overpowered'))),
	power_band = 'OVERPOWERED'
WHERE JSON_VALID(tags) AND JSON_TYPE(tags) = 'ARRAY' AND JSON_SEARCH(tags, 'one', 'Overpowered') IS NOT NULL;