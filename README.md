# SARI Ontology

## About

A ResearchSpace instance that contains the ontologies created by SARI.


## How to use

Prerequisites: [Docker](http://docker.io) including Docker Compose

Copy and (if required) edit the `.env.example`
```sh
cp .env.example .env
```

Run the project with
```sh
docker compose up -d
```

ResearchSpace comes with some preloaded ontologies. To start with a clean slate, remove all triples after the first run.