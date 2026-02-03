from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ai.client import call_openai_with_image
from lib.db import create_node, create_relationship

def extract_json_from_text(text: str) -> Any | None:
    code_fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
    for match in code_fence_pattern.finditer(text):
        candidate = match.group(1).strip()
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "{[":
            continue
        try:
            result, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        return result

    return None

if __name__ == "__main__":
    response = call_openai_with_image("data/Cage Filter.jpg")
    output_path = Path("ai/output.txt")
    output_path.write_text(response, encoding="utf-8")
    json_payload = extract_json_from_text(response)
    if json_payload is not None:
        db_objects_path = Path("db_objects.json")
        db_objects_path.write_text(
            json.dumps(json_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    with open("./data/db_objects.json", "r") as f:
        db_objects = json.load(f)
    for entity in db_objects["entities"]:
        create_node(entity["type"], entity["properties"])
    for relationship in db_objects["relationships"]:
        source = relationship["source"]
        target = relationship["target"]
        source_properties = relationship["source_properties"]
        target_properties = relationship["target_properties"]
        create_relationship(source, source_properties, relationship["relationship"], target, target_properties)
