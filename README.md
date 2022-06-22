# EasyTicketsBot

## Development
docker run -d --name easyticket_db -p 5436:5432 -e POSTGRES_USER=robot -e POSTGRES_PASSWORD=12zomole -e POSTGRES_DB=easyticket postgres:13.3


docker ps -a | grep 'db' |  xargs docker container rm \
docker volume ls | grep 'db' |  xargs docker volume rm
### General

    python -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -r requirements/development-only.txt
    pre-commit install
    cp docker-compose.override.example.yml docker-compose.override.yml

### Frontend

    docker-compose run frontend npm run watch
