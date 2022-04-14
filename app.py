import pandas as pd
from dateutil import parser
from elasticsearch import Elasticsearch, helpers
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/pycon22"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


CSV_FILENAME = "data/netflix_titles.csv"


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"




@app.route("/bulk-ingest")
def bulk_ingest():
    """Ingest all shows into Elasticsearch index."""
    
    es = Elasticsearch()

    doc = {
        'author': 'kimchy',
        'text': 'Elasticsearch: cool. bonsai cool.',
        'timestamp': datetime.now(),
    }
    resp = es.index(index="test-index", id=1, document=doc)
    print(resp['result'])



@app.route("/populate-db")
def populate_db():
    """Populates the relational db with sample data.

    Reads the CSV file in data/netflix_titles.csv and saves them in a `show` table in the database.
    """
    df = pd.read_csv(CSV_FILENAME, header=0, index_col=0)
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
                date_added=parser.parse(show['date_added']) if type(show['date_added']) == str else None,
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


"""
Just because I keep forgetting:

$ flask db init
$ flask db migrate
$ flask db upgrade
"""
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
