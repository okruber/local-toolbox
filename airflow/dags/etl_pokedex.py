from datetime import datetime
from pathlib import Path
import json

import duckdb
import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

RAW_DATA_PATH = Path("/opt/airflow/data/raw")
DB_PATH = Path("/opt/airflow/dwh/pokedex.duckdb")

def extract_pokemon() -> None:
    """Extract Pokemon data from PokeAPI and save to JSON."""
    pokemon_data = []
    for i in range(1, 21):
        url = f"https://pokeapi.co/api/v2/pokemon/{i}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            simplified = {
                "id": data["id"],
                "name": data["name"],
                "height": data["height"],
                "weight": data["weight"],
                "types": [t["type"]["name"] for t in data["types"]],
                "base_experience": data["base_experience"],
            }
            pokemon_data.append(simplified)
        print(f"Fetched {i}")

    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
    (RAW_DATA_PATH / "pokemon.json").write_text(
        json.dumps(pokemon_data), encoding="utf-8"
    )

def extract_types() -> None:
    """Extract Pokemon type data from PokeAPI and save to JSON."""
    url = "https://pokeapi.co/api/v2/type"
    response = requests.get(url)
    if response.status_code != 200:
        return

    data = response.json()
    type_details = []
    for item in data["results"][:10]:
        r = requests.get(item["url"])
        if r.status_code == 200:
            t_data = r.json()
            move_damage_class = t_data.get("move_damage_class")
            simplified = {
                "id": t_data["id"],
                "name": t_data["name"],
                "generation": t_data["generation"]["name"],
                "move_damage_class": move_damage_class["name"] if move_damage_class else None,
            }
            type_details.append(simplified)

    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
    (RAW_DATA_PATH / "types.json").write_text(
        json.dumps(type_details), encoding="utf-8"
    )

def load_to_duckdb() -> None:
    """Load extracted JSON data into DuckDB tables."""
    con = duckdb.connect(str(DB_PATH))

    pokemon_json = RAW_DATA_PATH / "pokemon.json"
    types_json = RAW_DATA_PATH / "types.json"

    con.execute(
        f"CREATE OR REPLACE TABLE raw_pokemon AS SELECT * FROM read_json_auto('{pokemon_json}')"
    )
    con.execute(
        f"CREATE OR REPLACE TABLE raw_types AS SELECT * FROM read_json_auto('{types_json}')"
    )
    con.close()

with DAG('pokedex_etl', start_date=datetime(2024, 1, 1), schedule_interval='@daily', catchup=False) as dag:
    
    t1 = PythonOperator(
        task_id='extract_pokemon',
        python_callable=extract_pokemon
    )

    t2 = PythonOperator(
        task_id='extract_types',
        python_callable=extract_types
    )

    t3 = PythonOperator(
        task_id='load_to_duckdb',
        python_callable=load_to_duckdb
    )

    t4 = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir .'
    )

    [t1, t2] >> t3 >> t4
