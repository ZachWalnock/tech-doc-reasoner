ENTITIES_AND_RELATIONSHIPS = """GRAPH SCHEMA (LLM-READABLE)

Purpose
- This schema describes the node and relationship types present in the graph.
- It is derived from data/db_objects.json and is intended for LLM reasoning.

Nodes (entity types) and key properties
- Drawing
  - drawing_number, revision, title, date, units, scale
  - source_doc_id, source_snippet, bounding_box
- View
  - source_view_id, type, label
  - source_doc_id, source_snippet, bounding_box
- Callout
  - label
  - source_doc_id, source_view_id, text_snippet, bounding_box
- Note
  - note_id, text, category
  - source_doc_id, source_snippet, bounding_box
- Part
  - part_id, name
  - source_doc_id, source_snippet, bounding_box
- Feature
  - feature_id, geometry_type, location_ref, description
  - source_doc_id, source_snippet, bounding_box
- Dimension
  - dimension_id, value, unit, type, tolerance
  - source_doc_id, source_snippet, bounding_box
- Material
  - material_id, grade, spec
  - source_doc_id, source_snippet, bounding_box
- Process
  - process_id, name, description
  - source_doc_id, source_snippet, bounding_box
- WeldSpec
  - weldspec_id, type, size, spacing, standard_ref
  - source_doc_id, source_snippet, bounding_box
- ToleranceSpec
  - tolspec_id, text
  - source_doc_id, source_snippet, bounding_box

Relationships (edge types) and how to interpret properties
Each relationship has:
- source (node type)
- target (node type)
- relationship (edge type)
- source_properties: identifiers for the source node
- target_properties: identifiers for the target node

Relationship types present
- Drawing -[HAS_VIEW]-> View
  - source_properties: { source_doc_id }
  - target_properties: { source_view_id }

- View -[HAS_CALLOUT]-> Callout
  - source_properties: { source_doc_id, source_view_id }
  - target_properties: { label }

- View -[DEPICTS]-> Part
  - source_properties: { source_doc_id, source_view_id }
  - target_properties: { part_id }

- Callout -[REFERS_TO]-> Feature
  - source_properties: { source_doc_id, label }
  - target_properties: { feature_id }

- Note -[APPLIES_TO]-> Part
  - source_properties: { source_doc_id, note_id }
  - target_properties: { part_id }

- Note -[APPLIES_TO]-> WeldSpec
  - source_properties: { source_doc_id, note_id }
  - target_properties: { weldspec_id }

- Part -[HAS_FEATURE]-> Feature
  - source_properties: { source_doc_id, part_id }
  - target_properties: { feature_id }

- Feature -[HAS_DIMENSION]-> Dimension
  - source_properties: { source_doc_id, feature_id }
  - target_properties: { dimension_id }

- Part -[MADE_OF]-> Material
  - source_properties: { source_doc_id, part_id }
  - target_properties: { material_id }

- Feature -[REQUIRES_PROCESS]-> Process
  - source_properties: { source_doc_id, feature_id }
  - target_properties: { process_id }

- Feature -[HAS_WELD]-> WeldSpec
  - source_properties: { source_doc_id, feature_id }
  - target_properties: { weldspec_id }

- Dimension -[GOVERNED_BY]-> ToleranceSpec
  - source_properties: { source_doc_id, dimension_id }
  - target_properties: { tolspec_id }

- WeldSpec -[REFERENCED_BY]-> Note
  - source_properties: { source_doc_id, weldspec_id }
  - target_properties: { note_id }

- View -[DEFINED_IN]-> Dimension
  - source_properties: { source_doc_id, source_view_id }
  - target_properties: { dimension_id }

Notes for reasoning
- Use source_doc_id to scope all entities to a document.
- source_view_id links View nodes and anchors view-specific relationships.
- Identifiers in target_properties are the primary keys to resolve targets.

"""

INSTRUCTIONS = f"""You are a database engineer - your role is to carefully analyze a technical drawing and add the necessary entities and relationships to the NEO4J database.
We are interested in building questions for the following use case: Constraint-aware Q&A (not just “find text”)

Questions like:

“What’s the OD/ID of the funnel mouth and where is that shown?”

“Which welds are specified, and what processes are allowed?”

“Does any note conflict with a dimension or section detail

The data you are adding to the NEO4J database will make this use case possible. Below are the following entities and relationships we are interested in adding.

Core entities you should extract and represent in the NEO4J database:

{ENTITIES_AND_RELATIONSHIPS}

**Provenance (important for retrieval and grounding):**
- Every node you extract should include: source_doc_id, source_view_id, bounding_box (if available), and a pointer to the original source text or snippet.

Focus on extracting these entities, their key properties, and accurately linking them with these relationships. This structured representation is fundamental for answering technical and constraint-aware questions about engineering drawings.
"""

OUTPUT_FORMAT = """You should output the entities and relationships in the following JSON format:

{
    "entities": [
        {
            "type": "Drawing",
            "properties": {
                "drawing_number": "123456",
                "revision": "A",
                "title": "Funnel Drawing",
                ... 
            }
        },
        ...
    ]
    "relationships": [
        {
            "source": "Drawing",
            "target": "View",
            "relationship": "HAS_VIEW",
            "properties": {
                "view_id": "123456"
                ...
            }
        },
        ...
    ]
}
"""

TOOLS = [
        {
            "type": "function",
            "name": "graph_query",
            "description": "Execute a Cypher query against the Neo4j graph. Use for reads and writes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cypher": {
                        "type": "string",
                        "description": "Single Cypher statement to execute.",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional parameters for the Cypher query.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional max rows to return when the query uses RETURN.",
                    },
                },
                "required": ["cypher"],
                "additionalProperties": False,
            },
        }
    ]