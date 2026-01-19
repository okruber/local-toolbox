with pokemon as (
    select * from "pokedex"."main"."stg_pokemon"
),

types as (
    select * from "pokedex"."main"."stg_types"
)

select 
    p.pokemon_id,
    p.name as pokemon_name,
    p.height,
    p.weight,
    p.base_experience,
    p.type_name,
    t.generation as type_generation,
    t.move_damage_class
from pokemon p
left join types t on p.type_name = t.type_name