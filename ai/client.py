import base64
import json
import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from .PROMPT import INSTRUCTIONS, OUTPUT_FORMAT, TOOLS, ENTITIES_AND_RELATIONSHIPS
from lib.db import run_cypher

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        load_dotenv()
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def _guess_mime_type(image_path: Path) -> str:
    extension = image_path.suffix.lower()
    if extension in {".jpg", ".jpeg"}:
        return "image/jpeg"
    return f"image/{extension}"


def _encode_image_base64(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("ascii")


def call_openai_with_image(image_path: str, model: Optional[str] = None) -> str:
    image_file = Path(image_path)
    image_b64 = _encode_image_base64(image_file)
    mime_type = _guess_mime_type(image_file)

    system_instructions = f"{INSTRUCTIONS}\n\n{OUTPUT_FORMAT}"
    model_name = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
    print("Before response with model", model_name)
    response = _get_client().responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": system_instructions},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Analyze this technical document."},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{image_b64}",
                        "detail": "high",
                    },
                ],
            },
        ],
    )
    print("After response with model")
    return response.output_text


def _get_item_value(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def call_openai_with_graph_reasoning(user_query: str, model: Optional[str] = None) -> str:
    system_instructions = (
        "You are a technical reasoning assistant with access to a Neo4j graph database of "
        "engineering drawings, parts, features, dimensions, notes, and relationships. "
        "Use the graph_query tool to read or update the graph. "
        "When you infer a relationship, use MERGE to add it and set properties "
        "{inferred: true, rationale: <short reason>}. "
        "Use a single Cypher statement per tool call. Prefer parameterized queries. "
        "If you use RETURN, keep results small and use LIMIT when possible. "
        "Provide tool arguments as JSON."
        f"Here is the basic schema of the graph: {ENTITIES_AND_RELATIONSHIPS}"
        "Some of these entities and relationships may not be present in the graph, if so just assume its not present in the drawing."
    )
    model_name = model or os.getenv("OPENAI_MODEL", "gpt-5.2")

    response = _get_client().responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_query},
        ],
        tools=TOOLS,
    )

    max_rounds = 3
    for _ in range(max_rounds):
        tool_calls = [
            item
            for item in response.output
            if _get_item_value(item, "type") == "function_call"
            and _get_item_value(item, "name") == "graph_query"
        ]
        if not tool_calls:
            return response.output_text

        tool_outputs = []
        for call in tool_calls:
            arguments = _get_item_value(call, "arguments", "{}")
            try:
                payload = json.loads(arguments) if isinstance(arguments, str) else arguments
            except json.JSONDecodeError:
                payload = {"cypher": str(arguments)}
            cypher = payload.get("cypher", "")
            parameters = payload.get("parameters")
            limit = payload.get("limit", 25)
            try:
                result = run_cypher(cypher, parameters=parameters, limit=limit)
            except Exception as e:
                print(f"Error running Cypher: {e}")
                result = {"error": str(e)}
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": _get_item_value(call, "call_id"),
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

        response = _get_client().responses.create(
            model=model_name,
            input=tool_outputs,
            previous_response_id=response.id,
            tools=TOOLS,
        )

    return response.output_text


if __name__ == "__main__":
    response = call_openai_with_image("test.png")
    print(response)
