
/*
    Staging model for Pokemon.
    Keeps types as an array to maintain one row per pokemon.
*/
with raw as (
    select * from {{ source('duckdb', 'raw_pokemon') }}
)

select
    id as pokemon_id,
    name,
    height,
    weight,
    base_experience,
    types
from raw
