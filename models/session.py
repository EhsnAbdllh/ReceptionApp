from peewee import Model, IntegerField, CharField
from models.database import db

class Session(Model):
    session_number = IntegerField(unique=True)
    start_time = CharField() # Format: YYYY/MM/DD HH:MM
    end_time = CharField()   # Format: YYYY/MM/DD HH:MM
    total_capacity = IntegerField()

    class Meta:
        database = db
