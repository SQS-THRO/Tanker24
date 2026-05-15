---
icon: simple/docker
---

# Prerequisites
To start the application you need to set proper values for the environment variables.  

The repository includes an example environment file: `.env.example`.
Copy the file to `.env` as described below. You want to change the following settings:  

- ``TANKERKOENIG_API_KEY``: This must be the valid API key from the Tankerkoenig API. It is provided to you upon request or hand in with this course work to the professor. 
- `INVITATION_KEYS`: This is a comma separated list of invitation keys. To create a new account it is necessary to use a invitation key that has not been use before hand. You do not need to add quotes around the individual keys. The keys **must be** a 32 characters long **hex** string.

You can change the database settings with prefix `postgres` as you wish when using the skeleton installation. The demo database expects the example configuration.

# Installation

First, install our repository
```bash
git clone https://github.com/SQS-THRO/Tanker24
```
```bash
cd Tanker24
```

Then start it like this
```bash
cp .env.example .env
```

To use the ``skeleton`` or ```default`` version of Tanker24

```bash
docker compose up -d
```

To use the ``demo`` version of Tanker24 use the following command:

```bash
docker compose -f compose.yaml -f compose.demo.yaml up --build -d
```

# Demo setup

Creating a new database dump should be done with this command:

```bash
docker exec -t postgres_db pg_dump -U myuser -d tanker24 --clean --if-exists --inserts > db/seed/demo-data.sql
```