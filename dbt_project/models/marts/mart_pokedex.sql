
with pokemon as (
    select * from {{ ref('stg_pokemon') }}
)

select
    pokemon_id,
    name as pokemon_name,
    height,
    weight,
    base_experience,
    types
from pokemon
