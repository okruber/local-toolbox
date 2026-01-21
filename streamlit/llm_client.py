# ABOUTME: LLM client for natural language to Cube query translation.
# Supports OpenAI, Anthropic, and Ollama backends via environment configuration.

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


SYSTEM_PROMPT = """You are a data analyst assistant that translates natural language questions into Cube.js queries.

You will be given:
1. A schema describing available cubes, dimensions, and measures
2. A user question in natural language

Your task is to generate a valid Cube.js query JSON object that answers the question.

IMPORTANT RULES:
- Only use dimensions and measures that exist in the provided schema
- Use the exact names from the schema (they are case-sensitive)
- Filter values should be LOWERCASE (e.g., "charmander" not "Charmander", "fire" not "Fire")
- Return ONLY the JSON query object, no explanations or markdown
- The query format is: {"dimensions": [...], "measures": [...], "filters": [...], "limit": N}
- Filters use the format: {"member": "Cube.field", "operator": "equals|notEquals|contains|gt|lt|gte|lte", "values": [...]}
- For counting, use the count measure if available
- For averages, use the avg measures if available
- Default limit to 100 unless the user asks for a specific number

Example queries:

Simple query:
{"dimensions": ["MartPokedex.pokemonName", "MartPokedex.typeName"], "measures": ["MartPokedex.count"], "limit": 10}

Query with filter (note: filters is an ARRAY):
{"dimensions": ["MartPokedex.pokemonName"], "measures": ["MartPokedex.count"], "filters": [{"member": "MartPokedex.typeName", "operator": "equals", "values": ["fire"]}], "limit": 100}
"""


@dataclass(frozen=True)
class LLMResponse:
    query: dict
    raw_response: str


class LLMClient(ABC):
    @abstractmethod
    def translate_query(self, schema_context: str, user_question: str) -> LLMResponse:
        pass


class OpenAIClient(LLMClient):
    def __init__(self, model: str | None = None) -> None:
        import openai

        self.client = openai.OpenAI()
        self.model = model or os.environ.get("LLM_MODEL", "gpt-4o")

    def translate_query(self, schema_context: str, user_question: str) -> LLMResponse:
        user_message = f"{schema_context}\n\nUser question: {user_question}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )

        raw = response.choices[0].message.content or ""
        query = _parse_query_json(raw)
        return LLMResponse(query=query, raw_response=raw)


class AnthropicClient(LLMClient):
    def __init__(self, model: str | None = None) -> None:
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model or os.environ.get("LLM_MODEL", "claude-sonnet-4-20250514")

    def translate_query(self, schema_context: str, user_question: str) -> LLMResponse:
        user_message = f"{schema_context}\n\nUser question: {user_question}"

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = response.content[0].text
        query = _parse_query_json(raw)
        return LLMResponse(query=query, raw_response=raw)


class OllamaClient(LLMClient):
    def __init__(self, model: str | None = None) -> None:
        import ollama

        self.client = ollama.Client(host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
        self.model = model or os.environ.get("LLM_MODEL", "llama3")

    def translate_query(self, schema_context: str, user_question: str) -> LLMResponse:
        user_message = f"{schema_context}\n\nUser question: {user_question}"

        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )

        raw = response["message"]["content"]
        query = _parse_query_json(raw)
        return LLMResponse(query=query, raw_response=raw)


def _parse_query_json(raw: str) -> dict:
    cleaned = raw.strip()

    json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(1)

    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)

    return json.loads(cleaned)


def create_llm_client() -> LLMClient:
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()

    if provider == "openai":
        return OpenAIClient()
    if provider == "anthropic":
        return AnthropicClient()
    if provider == "ollama":
        return OllamaClient()

    raise ValueError(f"Unknown LLM provider: {provider}. Use 'openai', 'anthropic', or 'ollama'.")
