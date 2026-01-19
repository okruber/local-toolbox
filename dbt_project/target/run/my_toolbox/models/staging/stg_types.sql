
  
  create view "pokedex"."main"."stg_types__dbt_tmp" as (
    with raw as (
    select * from "pokedex"."main"."raw_types"
)

select 
    id as type_id,
    name as type_name,
    generation,
    move_damage_class
from raw
  );
