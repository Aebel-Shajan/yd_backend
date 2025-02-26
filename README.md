## Year in Data Python pipeline / backend

Post request files -> run pipeline on files -> store in sql db -> Get request jsons

## Usage

Commands | Description
-|-
`poetry run fastapi dev api/main.py` | Serve the background API using FastAPI
`poetry run python main.py` | Run the data pipeline

## Tech stack 

Tech | Description
-|-
poetry | Python dependency management
fastapi | Fast web framework
graphql | Used to fetch info from github api. Allows use of one single query instead of multiple fetches.
pandas | Data analysis library
