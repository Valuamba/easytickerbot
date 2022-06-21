# EasyTicketsBot

## Development

### General

    python -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -r requirements/development-only.txt
    pre-commit install
    cp docker-compose.override.example.yml docker-compose.override.yml

### Frontend

    docker-compose run frontend npm run watch
