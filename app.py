import pandas as pd
from dateutil import parser
from elasticsearch import Elasticsearch, helpers
from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

SAMPLE_DATA_CSV_FILENAME = "data/netflix_titles.csv"
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/pycon22"

ELASTICSEARCH_HOST = "http://localhost:9200"
INDEX_NAME = "shows"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/", methods=["GET", "POST"])
def main():
    return render_template('index.html')


@app.route("/search")
def search_es():
    search_term = request.args.get("q")
    result_data = {}
    hit_count = None

    if search_term:
        es = Elasticsearch(ELASTICSEARCH_HOST)

        # Simple Query String Query
        # see: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html
        # TODO: filter only rating G (general) and PG (parental guidance)
        es_query =  {
            "query": {
                "simple_query_string" : {
                    "query": search_term,
#                    "fields": ["name"],
                    "fields": ["name^5", "director^3", "cast^2", "description"],
                    "default_operator": "and"
                }
            }
        }

        resp = es.search(index=INDEX_NAME, body=es_query, size=1000)

        hit_count = resp['hits']['total']['value']
        result_data = [hit["_source"] for hit in resp["hits"]["hits"]]

    results = {
        "query": search_term,
        "result_data": result_data,
        "hit_count": hit_count,
    }

    return jsonify(results)



@app.route("/bulk-ingest")
def bulk_ingest():
    """Ingest all shows into Elasticsearch index.

    You can look at the index in the browser with this URL:
    http://localhost:9200/shows/_search?size=10000&q=*:*
    """

    es = Elasticsearch(ELASTICSEARCH_HOST)

    resp = helpers.bulk(es, _generate_bulk_show_data())
    print(f"Bulk indexing done: {resp}")

    return "<p>Bulk ingest done.</p>"


def _generate_bulk_show_data():
    """Generator that yields all shows in a JSON format Elasticsearch can ingest."""

    for show in ShowModel.query.all():
        yield {
            '_index': INDEX_NAME,
            '_id': show.id,
            '_source': show.search_document(),
        }


@app.route("/shows/new", methods = ['POST'])
def new_show():
    """Create a new Show

    For testing your can use this CURL command to send data to the endpoint:
    curl -X POST http://localhost:5000/shows/new -i -H 'Content-Type: application/json' -d '{ "show_type": "Movie", "name": "TRON", "director": "Steven Linsberger", "cast": "Jeff Bridges, Cindy Morgan", "country": "United States", "date_added": "1982-01-01", "release_year": "1982", "rating": "PG", "duration": "96 min", "description": "A computer hacker is abducted into the digital world and forced to participate in gladiatorial games where his only chance of escape is with the help of a heroic security program." }'
    """
    data = request.get_json()
    new_show = ShowModel(
        show_type=data['show_type'] if 'show_type' in data else None,
        name=data['name'] if 'name' in data else None,
        director=data['director'] if 'director' in data else None,
        cast=data['cast'] if 'cast' in data else None,
        country=data['country'] if 'country' in data else None,
        date_added=parser.parse(data['date_added']) if 'date_added' in data else None,
        release_year=data['release_year'] if 'release_year' in data else None,
        rating=data['rating'] if 'rating' in data else None,
        duration=data['duration'] if 'duration' in data else None,
        description=data['description'] if 'description' in data else None,
    )
    db.session.add(new_show)
    db.session.commit()

    result = {
        "status": "OK",
        "message": f"Show '{new_show.name}' (id: {new_show.id}) created.",
    }

    return result, 201



@app.route("/populate-db")
def populate_db():
    """Populates the relational db with sample data.

    Reads the CSV file in data/netflix_titles.csv and saves them in a `show` table in the database.
    """
    df = pd.read_csv(SAMPLE_DATA_CSV_FILENAME, header=0, index_col=0)
    df = df.where(pd.notnull(df), None)  # replace NaN with None

    for _, row in df.iterrows():

        show = row.to_dict()
        # save show to db
        try:
            new_show = ShowModel(
                show_type=show['show_type'],
                name=show['title'],
                director=show['director'],
                cast=show['cast'],
                country=show['countries'].split(',')[0] if type(show['countries']) == str else '',
                date_added=parser.parse(show['date_added']),
                release_year=show['release_year'],
                rating=show['rating'],
                duration=show['duration'],
                description=show['description'],
            )
            db.session.add(new_show)
            db.session.commit()
        except Exception as ex:
            print(f'IGNORED: {ex}')
            # Ignore errors, it is just sample data.
            # raise(ex)
            pass

    return f"<p>Done populating db! ({len(df)} Shows inserted.) Have a nice day.</p>"  # count will be not correct because of swallowed errors, but it is just sample data


class ShowModel(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    show_type = db.Column(db.String())
    name = db.Column(db.String())
    director = db.Column(db.String())
    cast = db.Column(db.String())
    country = db.Column(db.String())
    date_added = db.Column(db.DateTime)
    release_year = db.Column(db.Integer)
    rating = db.Column(db.String())
    duration = db.Column(db.String())
    description = db.Column(db.String())

    def __init__(self, show_type, name, director, cast, country, date_added, release_year, rating, duration, description):
        self.show_type = show_type
        self.name = name
        self.director = director
        self.cast = cast
        self.country = country
        self.date_added = date_added
        self.release_year = release_year
        self.rating = rating
        self.duration = duration
        self.description = description

    def __repr__(self):
        return f"<Show {self.name}>"

    def search_document(self):
        return {
            "type": self.show_type,
            "name": self.name,
            "director": self.director,
            "cast": self.cast,
            "country": self.country,
            "date_added": self.date_added,
            "release_year": self.release_year,
            "rating": self.rating,
            "duration": self.duration,
            "description": self.description,
        }


@event.listens_for(ShowModel, 'after_insert')
def add_show_to_elasticsearch(mapper, connection, show):
    """Adds a given show to the Elasticsearch index"""

    es = Elasticsearch(ELASTICSEARCH_HOST)

    resp = es.index(
        index = INDEX_NAME,
        id = show.id,
        body = show.search_document(),
    )

    print(f"Updated show in ElasticSearch Index: {resp}")
