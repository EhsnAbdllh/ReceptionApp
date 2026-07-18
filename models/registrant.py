import uuid
from peewee import Model, CharField, ForeignKeyField, UUIDField
from models.database import db
from models.session import Session

class Registrant(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    full_name = CharField()
    phone_number = CharField()
    registration_time = CharField() # Format: YYYY/MM/DD HH:MM
    session = ForeignKeyField(Session, backref='registrants')

    class Meta:
        database = db
