from os import environ
class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL_SQL')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
