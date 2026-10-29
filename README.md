# Liferay 7.4 DXP

Liferay DXP 7.4 running on docker compose.

## Requirements

* Docker and Docker Compose (CE edition) - version 24.0.2

## Start the environment

```
docker compose up --build -d
```

## Get logs:

```
docker compose logs -f liferay
```

## Access

Access http://localhost:8080/ and login with [USER] and [PASSWORD]

## DUMP

```
docker compose exec database rm -rf /docker-entrypoint-initdb.d/database.sql
docker compose exec database pg_dump -U root --format=plain --no-owner --no-acl -d lportal -f /docker-entrypoint-initdb.d/database.sql
```