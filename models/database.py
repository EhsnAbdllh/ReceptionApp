from peewee import SqliteDatabase
from config.settings import DB_PATH

db = SqliteDatabase(DB_PATH)

def init_db():
    from models.session import Session
    from models.registrant import Registrant
    db.connect()
    db.create_tables([Session, Registrant], safe=True)
