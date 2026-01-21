# Natural Language Query UI

A Streamlit application that enables natural language queries against the Cube semantic layer. Ask questions about Pokemon data in plain English, and the app translates them to Cube queries via an LLM.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│    LLM API      │     │   Cube Core     │
│   (port 8501)   │     │ (OpenAI/Ollama) │     │   (port 4000)   │
└────────┬────────┘     └─────────────────┘     └────────▲────────┘
         │                                               │
         │  1. User asks question                        │
         │  2. Fetch schema from Cube /meta              │
         │  3. Send question + schema to LLM             │
         │  4. LLM returns Cube query JSON               │
         │  5. Execute query via Cube /load ─────────────┘
         │  6. Display results in table
         ▼
┌─────────────────┐
│   DuckDB        │
│   (via Cube)    │
└─────────────────┘
```

## LLM Configuration

Configure the LLM provider via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider: `anthropic`, `openai`, or `ollama` | `anthropic` |
| `LLM_MODEL` | Model name (provider-specific) | Provider default |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OLLAMA_HOST` | Ollama server URL | `http://host.docker.internal:11434` |

### Provider Examples

**Anthropic (default):**
```bash
export ANTHROPIC_API_KEY=your-key-here
docker compose up nl-query-ui
```

**OpenAI:**
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-key-here
docker compose up nl-query-ui
```

**Ollama (local, no API key needed):**
```bash
# Start Ollama locally first
ollama serve

# Then run with Ollama provider (cube must also be running)
LLM_PROVIDER=ollama LLM_MODEL=gemma3:4b docker compose up cube nl-query-ui
```

### Model Selection

Override the default model with `LLM_MODEL`:

```bash
# Use GPT-4 Turbo
LLM_PROVIDER=openai LLM_MODEL=gpt-4-turbo docker compose up nl-query-ui

# Use Claude Haiku for faster responses
LLM_PROVIDER=anthropic LLM_MODEL=claude-3-haiku-20240307 docker compose up nl-query-ui

# Use a local Mistral model
LLM_PROVIDER=ollama LLM_MODEL=mistral docker compose up nl-query-ui
```

## Local Development

Run the Streamlit app outside Docker for faster iteration:

```bash
cd streamlit

# Install dependencies
uv sync

# Set environment variables
export CUBE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=your-key-here

# Run the app
uv run streamlit run app.py
```

## Example Questions
