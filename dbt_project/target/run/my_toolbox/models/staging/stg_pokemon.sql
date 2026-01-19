
  
  create view "pokedex"."main"."stg_pokemon__dbt_tmp" as (
    /*
    Staging model for Pokemon.
    Unnests the 'types' list to create a grain of pokemon_id per type if we wanted, 
    but for this simple mart, we might just keep it as a list or take the primary type.
    Let's unnest to have rows like (pikachu, electric).
*/
with raw as (
    select * from "pokedex"."main"."raw_pokemon"
),

unnested as (
    select 
        id as pokemon_id,
        name,
        height,
        weight,
        base_experience,
        unnest(types) as type_name
    from raw
)

select * from unnested
  );
