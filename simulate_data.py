import sys
import os
import random
import uuid
import jdatetime

# Adjust python path to allow importing models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from models.session import Session
from models.registrant import Registrant

# We will initialize a separate simulation database
sim_db_path = "simulation_reception.db"
if os.path.exists(sim_db_path):
    os.remove(sim_db_path)

print(f"Creating database: {sim_db_path}...")
db.init(sim_db_path)

db.connect()
db.create_tables([Session, Registrant], safe=True)

print("Generating 60 sessions...")
start_date = jdatetime.datetime(1405, 5, 1, 8, 0)
sessions = []
for i in range(1, 61):
    current_start = start_date + jdatetime.timedelta(minutes=(i-1)*45)
    current_end = current_start + jdatetime.timedelta(minutes=30)
    
    start_str = current_start.strftime("%Y/%m/%d %H:%M")
    end_str = current_end.strftime("%Y/%m/%d %H:%M")
    
    session = Session.create(
        session_number=i,
        start_time=start_str,
        end_time=end_str,
        total_capacity=100
    )
    sessions.append(session)

print("Generating 4000 registrants...")
names = ["محمد", "علی", "فاطمه", "زهرا", "حسین", "حسن", "رضا", "سارا", "مریم", "امیر", "مهدی", "علیرضا", "زینب", "ابوالفضل", "عرفان", "سجاد"]
family_names = ["احمدی", "حسینی", "رضایی", "محمدی", "کریمی", "موسوی", "جعفری", "قاسمی", "طهماسبی", "امیری", "صادقی", "علیپور"]

registrants = []
for i in range(4000):
    full_name = f"{random.choice(names)} {random.choice(family_names)}"
    phone_number = f"0912{random.randint(1000000, 9999999)}"
    session = random.choice(sessions)
    reg_time = session.start_time
    
    registrants.append({
        'id': uuid.uuid4(),
        'full_name': full_name,
        'phone_number': phone_number,
        'registration_time': reg_time,
        'session': session.id
    })
    
    if (i + 1) % 1000 == 0:
        print(f"  Prepared {i + 1} records...")

print("Inserting records into database...")
with db.atomic():
    Registrant.insert_many(registrants).execute()

print("\nSimulation database created successfully!")
print(f"Database path: {os.path.abspath(sim_db_path)}")
print("60 sessions and 4000 registrants populated.")
