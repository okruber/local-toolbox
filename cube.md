# Cube Semantic Layer

Cube provides a semantic layer on top of DuckDB, exposing data through REST API, GraphQL, and a PostgreSQL-compatible SQL interface.

## Access Methods

### 1. Cube Playground (Interactive UI)

Visit http://localhost:4000 to explore schemas and run queries interactively.

### 2. REST API

Query via HTTP POST:

```bash
# Get count of all Pokemon
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["MartPokedex.count"]
  }'

# Get average height and weight by type
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["MartPokedex.avgHeight", "MartPokedex.avgWeight"],
    "dimensions": ["MartPokedex.typeName"]
  }'

# Get top 10 heaviest Pokemon
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["MartPokedex.pokemonName", "MartPokedex.weight"],
    "order": {"MartPokedex.weight": "desc"},
    "limit": 10
  }'

# Get schema metadata
curl http://localhost:4000/cubejs-api/v1/meta
```

### 3. SQL API (PostgreSQL Wire Protocol)

Connect using any PostgreSQL-compatible client on port 15432:

```bash
psql -h localhost -p 15432 -U cube
```

Example queries:

```sql
SELECT COUNT(*) FROM mart_pokedex;

SELECT
  type_name,
  AVG(height) as avg_height,
  AVG(weight) as avg_weight
FROM mart_pokedex
GROUP BY type_name
ORDER BY avg_weight DESC;

SELECT
  pokemon_name,
  weight
FROM mart_pokedex
ORDER BY weight DESC
LIMIT 10;
```

## Data Models

### MartPokedex

Semantic model for Pokemon analytics.

**Measures:**
- `count` - Total number of Pokemon
- `avgHeight` - Average height
- `avgWeight` - Average weight
- `avgBaseExperience` - Average base experience

**Dimensions:**
- `pokemonId` - Unique identifier
- `pokemonName` - Name
- `height` - Height
- `weight` - Weight
- `baseExperience` - Base experience points
- `typeName` - Primary type
- `typeGeneration` - Generation when type was introduced
- `moveDamageClass` - Damage class (physical, special, status)

## Development

### Modifying Schemas

1. Edit files in `cube/model/`
2. Changes are hot-reloaded automatically (dev mode enabled)
3. Refresh Cube Playground to see updates

### Adding New Models

1. Create new `.js` file in `cube/model/`
2. Define cube with SQL query, measures, and dimensions
3. Restart Cube service or wait for hot-reload

## Configuration

Environment variables (set in `docker-compose.yaml`):

| Variable | Description | Default |
|----------|-------------|---------|
| `CUBEJS_DEV_MODE` | Enable development features | `true` |
| `CUBEJS_DB_TYPE` | Database type | `duckdb` |
| `CUBEJS_DB_DUCKDB_DATABASE_PATH` | Path to DuckDB file | `/cube/dwh/pokedex.duckdb` |

Cube connects to DuckDB in read-only mode via file mount. The database file is located at `dwh/pokedex.duckdb`.

## Troubleshooting

### Cube Can't Connect to DuckDB

Ensure the DuckDB file exists and contains materialized dbt models:

```bash
ls -lh dwh/pokedex.duckdb
```

### Schema Not Appearing in Playground

Check Cube logs for errors:

```bash
docker compose logs cube
```

Verify the model file syntax is correct and restart the service if needed.
