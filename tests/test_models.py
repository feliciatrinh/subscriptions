import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
basedir = os.path.abspath(os.path.dirname(__file__))

import pytest
import sqlalchemy as sa
from datetime import date, timedelta
from application import app as _app, db as _db
from application.models import Log, Media, MediaType, PaymentFrequency, Subscription

current_date = date.today()
yesterday = current_date - timedelta(days=1)
tomorrow = current_date + timedelta(days=1)
NETFLIX = "Netflix"
PEACOCK = "Peacock"
INSIDE_OUT = "Inside Out"
INSIDE_OUT_2 = "Inside Out 2"

@pytest.fixture(scope="session")
def app():
    db_uri = 'sqlite:///' + os.path.join(basedir, 'test.db')
    _app.config['TESTING'] = True
    _app.config['WTF_CSRF_ENABLED'] = False
    _app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    yield _app


@pytest.fixture(autouse=True)
def app_context(app):
    """
    Given app is session-wide, sets up a app context per test to ensure that
    app stack is not shared between tests.
    """
    ctx = app.app_context()
    ctx.push()
    yield  # tests will run here
    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    """Returns session-wide initialized database"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Creates a new database session for each test, rolling back changes afterwards"""
    connection = _db.engine.connect()
    transaction = connection.begin()

    yield _db.session

    transaction.rollback()
    connection.close()
    _db.session.remove()


def test_subscription(session):
    sub1 = Subscription(name=NETFLIX, cost="22.99")
    session.add(sub1)
    result = session.scalar(sa.select(Subscription).where(Subscription.name == NETFLIX))
    assert result.payment_frequency == PaymentFrequency.monthly
    assert result.active_date == current_date
    assert result.inactive_date is None

    sub2 = Subscription(name=PEACOCK, cost="0.00", payment_frequency=PaymentFrequency.yearly, active_date=yesterday, inactive_date=tomorrow)
    session.add(sub2)
    result = session.scalar(sa.select(Subscription).where(Subscription.name == PEACOCK))
    assert result.payment_frequency == PaymentFrequency.yearly
    assert result.active_date == yesterday
    assert result.inactive_date == tomorrow

    assert len(Subscription.query.all()) == 2

    # Subscription names should be unique
    duplicate = Subscription(name=NETFLIX, cost="0.00")
    with pytest.raises(sa.exc.IntegrityError):
        session.add(duplicate)
        session.flush()


def test_subscription_payment(session):
    # Subscription payment frequency is invalid
    bad_payment = Subscription(name="bad payment", cost="0.00", payment_frequency="dne")
    with pytest.raises(sa.exc.StatementError):
        session.add(bad_payment)
        session.flush()


def test_media(session):
    media = Media(title=INSIDE_OUT, type=MediaType.film)
    session.add(media)
    result = session.scalar(sa.select(Media).where(Media.title == INSIDE_OUT))
    assert result.description is None


def test_media_type(session):
    # media type is invalid
    bad_media_type = Media(title="bad media", type="dne")
    with pytest.raises(sa.exc.StatementError):
        session.add(bad_media_type)
        session.flush()


def test_log(session):
    sub = Subscription(name=PEACOCK, cost="0.00")
    media = Media(title=INSIDE_OUT, type=MediaType.film)
    session.add_all((sub, media))

    sub_id = session.scalar(sa.select(Subscription).where(Subscription.name == PEACOCK)).id
    media_id = session.scalar(sa.select(Media).where(Media.title == INSIDE_OUT)).id

    log = Log(subscription_id=sub_id, media_id=media_id)
    session.add(log)

    result = session.scalar(sa.select(Log).where(Log.subscription_id == sub_id, Log.media_id == media_id))
    assert result.date == current_date
    assert result.season is None
    assert result.episode is None
    assert result.notes is None
    assert result.media.id == media_id

    media2 = Media(title=INSIDE_OUT_2, type=MediaType.film)
    session.add(media2)
    media2_id = session.scalar(sa.select(Media).where(Media.title == INSIDE_OUT_2)).id

    log2 = Log(subscription_id=sub_id, media_id=media2_id, date=tomorrow, season=1, episode=1, notes="Amazing!")
    session.add(log2)

    result2 = session.scalar(sa.select(Log).where(Log.subscription_id == sub_id, Log.media_id == media2_id))
    print(result2)
    print(session.scalars(sa.select(Log)).all())
    assert result2.date == tomorrow
    assert result2.season == 1
    assert result2.episode == 1
    assert result2.notes == "Amazing!"

    assert len(Log.query.all()) == 2


def test_log_missing_sub(session):
    # subscription_id does not exist
    media = Media(title=INSIDE_OUT, type=MediaType.film)
    session.add(media)
    media_id = session.scalar(sa.select(Media).where(Media.title == INSIDE_OUT)).id
    log = Log(subscription_id=999, media_id=media_id)
    with pytest.raises(sa.exc.IntegrityError):
        session.add(log)
        session.flush()


def test_log_missing_media(session):
    # media_id does not exist
    sub = Subscription(name=PEACOCK, cost="0.00")
    session.add(sub)
    sub_id = session.scalar(sa.select(Subscription).where(Subscription.name == PEACOCK)).id
    log = Log(subscription_id=sub_id, media_id=999)
    with pytest.raises(sa.exc.IntegrityError):
        session.add(log)
        session.flush()
