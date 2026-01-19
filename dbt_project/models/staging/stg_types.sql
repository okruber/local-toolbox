
with raw as (
    select * from {{ source('duckdb', 'raw_types') }}
)

select 
    id as type_id,
    name as type_name,
    generation,
    move_damage_class
from raw
