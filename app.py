from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import pandas as pd
from dateutil import parser


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/pycon22"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

CSV_FILENAME = "data/netflix_titles.csv"

@app.route("/populate-db")
def populate_db():
    df = pd.read_csv(CSV_FILENAME, header=0, index_col=0)
    for index, row in df.iterrows():
        show = row.to_dict()
        for key in show.keys():
            if key == "director":
                pass
                # TODO
                # split on ,
                # multiple

            elif key == "cast":
                pass
                # TODO
                # split on ,
                # multiple

            elif key == "country":
                pass
                # TODO
                # split on ,
                # multiple

            elif key == "date_added":
                pass
                # TODO
                # parse "monthname date, year"

            elif key == "duration":
                pass
                # TODO
                # 90 min
                # 2 Seasons
                # 1 Season

            elif key == "listed_in":
                pass
                # TODO
                # split on ,
                # multiple

        # save show to db
        try:
            new_show = ShowModel(
                show_type=show['show_type'],
                name=show['title'],
                date_added=parser.parse(show['date_added']),
                release_year=show['release_year'],
                rating=show['rating'],
                duration=show['duration'],
                description=show['description'],
            )
            db.session.add(new_show)
            db.session.commit()
        except:
            # Ignore errors, it is just sample data.
            pass

    return f"<p>Done populating db! ({len(df)} Shows inserted.) Have a nice day.</p>"  # count will be not correct because of swallowed errors, but it is just sample data

'''
$ flask db init
$ flask db migrate
$ flask db upgrade
'''
class ShowModel(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    show_type = db.Column(db.String())
    name = db.Column(db.String())
    # director TODO
    # cast TODO
    # country TODO
    date_added = db.Column(db.DateTime)
    release_year = db.Column(db.Integer)
    rating = db.Column(db.String())
    duration = db.Column(db.String())
    #categories TODO
    description = db.Column(db.String())

    def __init__(self, show_type, name, date_added, release_year, rating, duration, description):
        self.show_type = show_type
        self.name = name
        self.date_added = date_added
        self.release_year = release_year
        self.rating = rating
        self.duration = duration
        self.description = description
        
    def __repr__(self):
        return f"<Show {self.name}>"

class CountryModel(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Country {self.name}>"


class PersonModel(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Person {self.name}>"        


class CategoryModel(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Category {self.name}>"                