from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import hashlib
import time
import json
from typing import Optional
load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = ("neo4j", os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)

def make_uid(key):
    now = str(time.time_ns())
    base = f"{key}-{now}"
    hash_digest = hashlib.sha256(base.encode()).hexdigest()[:8]
    return f"{key}_{now}_{hash_digest}"

def prepare_properties(properties: dict) -> dict:
    f"""
    Ensures each property has a unique UUID and returns a string of the properties and a map of UUIDs to values.
    """
    properties_string = []
    uuid_to_value_map = {}
    for key, value in properties.items():
        if value is not None:
            uuid = make_uid(key)
            properties_string.append(f"{key}: ${uuid}")
            uuid_to_value_map[uuid] = value
    return ", ".join(properties_string), uuid_to_value_map
    
def create_node(label: str, properties: dict) -> None:
    properties_string, uuid_to_value_map = prepare_properties(properties)
    with driver.session() as session:
        creation_string = f"MERGE (n:{label} {{ {properties_string} }})"
        session.run(creation_string, **uuid_to_value_map)

def create_relationship(source: str, source_properties: dict, relationship: str, target: str, target_properties: dict) -> None:
    with driver.session() as session:
        source_properties_string, source_uuid_to_value_map = prepare_properties(source_properties)
        target_properties_string, target_uuid_to_value_map = prepare_properties(target_properties)
        print(source_properties_string)
        print(target_properties_string)
        creation_string = f"MATCH (s:{source} {{ {source_properties_string} }}) MATCH (t:{target} {{ {target_properties_string} }}) MERGE (s)-[:{relationship}]->(t)"
        session.run(creation_string, **source_uuid_to_value_map, **target_uuid_to_value_map)

def delete_node(label: str, properties: dict) -> None:
    with driver.session() as session:
        session.run(f"MATCH (n:{label} {properties}) DELETE n")

def delete_relationship(source: str, relationship: str, target: str) -> None:
    with driver.session() as session:
        session.run(f"MATCH (s:{source})-[:{relationship}]->(t:{target}) DELETE (s)-[:{relationship}]->(t)")

def _apply_limit(cypher: str, limit: Optional[int]) -> str:
    if limit is None:
        return cypher
    cypher_clean = cypher.strip().rstrip(";")
    cypher_upper = cypher_clean.upper()
    if "RETURN" in cypher_upper and "LIMIT" not in cypher_upper:
        return f"{cypher_clean} LIMIT {int(limit)}"
    return cypher_clean

def run_cypher(cypher: str, parameters: Optional[dict] = None, limit: Optional[int] = 25) -> dict:
    """
    Executes a single Cypher statement and returns records and summary stats.
    """
    cypher_to_run = _apply_limit(cypher, limit)
    with driver.session() as session:
        result = session.run(cypher_to_run, **(parameters or {}))
        records = [record.data() for record in result]
        summary = result.consume()
    counters = summary.counters
    counters_payload = {
        "nodes_created": counters.nodes_created,
        "nodes_deleted": counters.nodes_deleted,
        "relationships_created": counters.relationships_created,
        "relationships_deleted": counters.relationships_deleted,
        "properties_set": counters.properties_set,
        "labels_added": counters.labels_added,
        "labels_removed": counters.labels_removed,
        "indexes_added": counters.indexes_added,
        "indexes_removed": counters.indexes_removed,
        "constraints_added": counters.constraints_added,
        "constraints_removed": counters.constraints_removed,
        "contains_updates": counters.contains_updates,
        "contains_system_updates": counters.contains_system_updates,
    }
    return {
        "records": records,
        "summary": {
            "counters": counters_payload,
            "result_available_after_ms": summary.result_available_after,
            "result_consumed_after_ms": summary.result_consumed_after,
        },
    }

if __name__ == "__main__":
    with open("./lib/db_objects.json", "r") as f:
        db_objects = json.load(f)
    test = db_objects["entities"][0]
    create_node(test["type"], test["properties"])
