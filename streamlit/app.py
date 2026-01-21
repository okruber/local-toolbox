# ABOUTME: Streamlit application for natural language queries against Cube semantic layer.
# Chat interface that translates questions to Cube queries via LLM.

import json

import pandas as pd
import streamlit as st

from cube_client import CubeClient, CubeClientError, schema_to_prompt_context
from llm_client import LLMClient, create_llm_client


def init_cube_client() -> CubeClient:
    if "cube_client" not in st.session_state:
        st.session_state.cube_client = CubeClient()
    return st.session_state.cube_client


def init_llm_client() -> LLMClient:
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = create_llm_client()
    return st.session_state.llm_client


def fetch_schema_context(cube_client: CubeClient) -> str | None:
    if "schema_context" not in st.session_state:
        try:
            schemas = cube_client.get_schema()
            st.session_state.schema_context = schema_to_prompt_context(schemas)
        except CubeClientError as e:
            st.error(f"Failed to connect to Cube: {e}")
            return None
    return st.session_state.schema_context


def main() -> None:
    st.set_page_config(page_title="Pokemon Data Explorer", page_icon="🔍", layout="wide")

    st.title("Pokemon Data Explorer")
    st.markdown("Ask questions about Pokemon data in natural language.")

    cube_client = init_cube_client()
    llm_client = init_llm_client()

    schema_context = fetch_schema_context(cube_client)
    if schema_context is None:
        st.warning("Cannot proceed without Cube connection. Please ensure Cube is running.")
        st.stop()

    with st.expander("View available schema"):
        st.text(schema_context)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "query" in msg:
                with st.expander("Generated Cube query"):
                    st.code(json.dumps(msg["query"], indent=2), language="json")
            if "dataframe" in msg:
                st.dataframe(msg["dataframe"], use_container_width=True)

    if question := st.chat_input("Ask a question about Pokemon data..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Translating question..."):
                try:
                    llm_response = llm_client.translate_query(schema_context, question)
                    query = llm_response.query
                except json.JSONDecodeError:
                    st.error("Failed to parse LLM response as valid JSON query.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Sorry, I couldn't generate a valid query for that question.",
                    })
                    st.stop()
                except Exception as e:
                    st.error(f"LLM error: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error communicating with LLM: {e}",
                    })
                    st.stop()

            with st.expander("Generated Cube query"):
                st.code(json.dumps(query, indent=2), language="json")

            with st.spinner("Executing query..."):
                try:
                    result = cube_client.execute_query(query)
                except CubeClientError as e:
                    st.error(f"Query execution failed: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Query execution failed: {e}",
                        "query": query,
                    })
                    st.stop()

            if result.data:
                df = pd.DataFrame(result.data)
                st.dataframe(df, use_container_width=True)

                row_count = len(result.data)
                response_text = f"Found {row_count} result{'s' if row_count != 1 else ''}."
            else:
                response_text = "No results found for your query."
                df = None

            st.markdown(response_text)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "query": query,
                "dataframe": df,
            })


if __name__ == "__main__":
    main()
