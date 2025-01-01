import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'temp-password')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(basedir, 'app.db')}")

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use an in-memory database
    SECRET_KEY = 'test_secret'  # A different secret key for testing
