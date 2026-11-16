# Liferay 7.4 DXP

Liferay DXP 7.4 running on docker compose.

## Requirements

* Docker and Docker Compose (CE edition) - version 24.0.2

## Start the environment

There is an issue when start liferay at the same time as search, so start one by one:

```
docker compose build
docker compose up -d database
docker compose up -d search
docker compose up -d
```

## Get logs:

```
docker compose logs -f liferay
```

## Access

Edit your /etc/hosts:

```
127.0.0.1 dev.tokiomarine inst01.tokiomarine inst02.tokiomarine inst03.tokiomarine
```

Access http://localhost:8080/ and login with test@liferay.com
Access http://dev.tokiomarine:8080/ and login with test@liferay.com

## DUMPs

Keep the dump updated

```
docker compose exec database rm -rf /docker-entrypoint-initdb.d/database.sql
docker compose exec database pg_dump -U root --format=plain --no-owner --no-acl -d lportal -f /docker-entrypoint-initdb.d/database.sql
docker compose exec database chmod 777 /docker-entrypoint-initdb.d/database.sql
```