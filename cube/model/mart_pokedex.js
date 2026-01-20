// Cube schema for mart_pokedex - Pokemon analytics semantic layer
// Maps to dbt mart model: dbt_project/models/marts/mart_pokedex.sql

cube('MartPokedex', {
  sql: `SELECT * FROM mart_pokedex`,

  measures: {
    count: {
      type: 'count',
      description: 'Total number of Pokemon'
    },

    avgHeight: {
      sql: 'height',
      type: 'avg',
      description: 'Average height of Pokemon',
      format: '.2f'
    },

    avgWeight: {
      sql: 'weight',
      type: 'avg',
      description: 'Average weight of Pokemon',
      format: '.2f'
    },

    avgBaseExperience: {
      sql: 'base_experience',
      type: 'avg',
      description: 'Average base experience of Pokemon',
      format: '.2f'
    }
  },

  dimensions: {
    pokemonId: {
      sql: 'pokemon_id',
      type: 'number',
      primaryKey: true,
      description: 'Unique Pokemon identifier'
    },

    pokemonName: {
      sql: 'pokemon_name',
      type: 'string',
      description: 'Name of the Pokemon'
    },

    height: {
      sql: 'height',
      type: 'number',
      description: 'Height of the Pokemon'
    },

    weight: {
      sql: 'weight',
      type: 'number',
      description: 'Weight of the Pokemon'
    },

    baseExperience: {
      sql: 'base_experience',
      type: 'number',
      description: 'Base experience points for the Pokemon'
    },

    typeName: {
      sql: 'type_name',
      type: 'string',
      description: 'Primary type of the Pokemon'
    },

    typeGeneration: {
      sql: 'type_generation',
      type: 'number',
      description: 'Generation when the type was introduced'
    },

    moveDamageClass: {
      sql: 'move_damage_class',
      type: 'string',
      description: 'Damage class of the Pokemon type (physical, special, status)'
    }
  }
});
