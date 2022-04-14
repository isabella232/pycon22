# PyCon 2022

This is small demo application that shows you how to ingest data into Elasticsearch and then use it in your Flask project.

# Getting started

### Start services

There is a `docker-compose.yml` that starts a Postgres database, Elasticsearch and Kibana. Just run this command to start everything:

```bash
docker-compose up
```

Now you have a running Elasticsearch on http://localhost:9200

### Create Postgres DB

The docker compose file starts Postgres on the default port 5432. To create a database do the following:

```bash
docker exec -it <container_name> psql -h localhost -U postgres
```

This should log you into the Postgres console (without asking for a password). No enter the following sql command:

```sql
create database pycon22;
```

Voila, you have a Postgres database.

### Setup and start the Flask project

You need to have fairly new Python 3 installed.

Call the `run.sh` script in the base folder of the project:

```bash
./run.sh
```

This will:

- Create a Python virtual environment
- Install the Python dependencies
- Run the Flask project on http://localhost:5000

The first time you try this you will get an error. This is because the Postgres database is still empty.

### Populate the Postgres DB with data

- Create the database schema

  Call the following to create all the tables necessary to run the project:

  ```
  source .venv/bin/activate
  flask db init
  flask db migrate
  flask db upgrade
  ```

- Import the data

  Now you have a database schema, but no data. So we need to run a special Flask endpoint to load all the sample data from the file `data/netflix_titles.csv` into Postgres:

  ```
  ./run.sh
  ```

  Then point your browser to: http://localhost:5000/populate-db

  This will take some time (and hopefully will not time out. If it does you need to look at the Flask configuration on how to increase the timeout. Or you will figure out how to call this function from the command line or something)

# Ingesting data into Elasticsearch

If you have done everything in _Getting Started_ you have a Flask app, Postgres, Elasticsearch and Kibana running.

Postgres contains all the data and there is nothing in Elasticsearch.

Let's change that.

You have to run Flask and then call a special endpoint to ingest everything:

```
./run.sh
```

Then point your browser to: http://localhost:5000/bulk-ingest

Now you have a Elasticsearch index called `shows` that contains all the shows from your Postgres db.
You can check it out by pointing your browser to:

```
http://localhost:9200/shows/_search?size=10000&q=*:*
```
