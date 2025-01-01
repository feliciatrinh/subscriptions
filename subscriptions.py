import sqlalchemy as sa
import sqlalchemy.orm as so
from application import create_app, db
from application.models import Media, Log

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    creates a shell context that adds the database instance and models to the shell session
    """
    return {'sa': sa, 'so': so, 'db': db, 'Media': Media, 'Log': Log}
