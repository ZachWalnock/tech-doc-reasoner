# Tech-Doc Reasoner

Extracts entities and relationships from technical drawings, loads them into Neo4j, and provides a simple terminal Q&A loop over the resulting graph.

## What this does
- Send an image of a technical drawing to OpenAI for structured extraction.
- Write the extracted JSON to disk for inspection and reuse.
- Load entities and relationships into Neo4j.
- Ask questions in a terminal loop that are answered using graph reasoning.

## Project layout
- `app.py` Terminal Q&A loop using `query_kg`.
- `pipeline.py` Image -> OpenAI -> JSON -> Neo4j loader.
- `ai/client.py` OpenAI client (image extraction + graph reasoning).
- `ai/PROMPT.py` System instructions and output format.
- `data/db_objects.json` Example graph payload.
- `data/graph_schema.txt` LLM-friendly schema description.
- `lib/db.py` Neo4j helpers.

## Requirements
- Python 3.10+
- Neo4j database (local or remote)

Install dependencies (example):
```
pip install openai python-dotenv neo4j
```

## Environment variables
Create a `.env` file at the project root with:
```
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5-mini
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=your_password
```

## Run the pipeline
This will send the image, save the model response to `ai/output.txt`, attempt to extract JSON, and load `data/db_objects.json` into Neo4j.
```
python pipeline.py
```

## Ask questions
Run the terminal app and ask questions about the loaded graph:
```
python app.py
```

## Notes
- `pipeline.py` currently uses `data/Cage Filter.jpg` as the sample input.
- If you change the image, update the path in `pipeline.py`.
- `ai/client.py` uses `ai/PROMPT.py` for instructions and output format.
