# Single-database configuration for Flask.

## Initialize the database


> flask db init

generate migration script
> flask db migrate -m "tables"

Apply changes to the database
> flask db upgrade

Undo the last migration then delete the old migration script and generate a new one.
> flask db downgrade

## Test out the database

In python session
```commandline
from application import app, db
from application.models import Media, Log
import sqlalchemy as sa

app.app_context().push()

m = Media(title="Inside Out", type="film", description="emotions")
db.session.add(m)
db.session.commit()
db.session.rollback() # to abort the session and remove any changes stored in it

m2 = Media(title="Inside Out 2", type="film", description="more emotions")
db.session.add(m2)
db.session.commit()

# return all media
query = sa.select(Media)
all_media = db.session.scalars(query).all() # [<Media Inside Out>, <Media Inside Out 2>]

all_media = db.session.scalars(query)
for m in all_media:
    print(m.id, m.title)

# 1 Inside Out
# 2 Inside Out 2

# Get a media record given an id
m = db.session.get(Media, 1) # <Media Inside Out>

# Add logs
log1 = Log(media=m)
db.session.add(log1)
db.session.commit()

# Get all logs for the given media
logs_query = m.logs.select()
db.session.scalars(logs_query).all() # [<Log(id=1, date=2024-12-30, media_id=1)>]

# Media with no logs
m2 = db.session.get(Media, 2)
logs_query = m2.logs.select()
db.session.scalars(logs_query).all() # []

# For all logs, print the title and date
query = sa.select(Log)
logs = db.session.scalars(query)
for log in logs:
    print(log.date, log.media.title, log.media.type) # 2024-12-30 Inside Out film

# More example queries
# get media in reverse alphabetical order
query = sa.select(Media).order_by(Media.title.desc())
db.session.scalars(query).all()
# [<Media Inside Out 2>, <Media Inside Out>]

m = Media(title="Deadpool & Wolverine", type="film")
db.session.add(m)
db.session.commit()

# get all media that have titles starting with "D"

query = sa.select(Media).where(Media.title.like('D%'))
db.session.scalars(query).all()
# [<Media Deadpool & Wolverine>]
```

Alternatively, run this to start a Python interpreter in the context of the application.
> flask shell

## Quickly empty tables
> flask db downgrade base
flask db upgrade

## Run the app

```
flask run
```

Resources:
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
- https://www.sqlalchemy.org
