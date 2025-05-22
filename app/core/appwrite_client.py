from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
import datetime
from .config import settings

def make_client(authenticated=True):
    """Creates an Appwrite client instance."""
    client = (
        Client()
        .set_endpoint(settings.APPWRITE_ENDPOINT)
        .set_project(settings.APPWRITE_PROJECT_ID)
    )
    
    if authenticated and settings.APPWRITE_API_KEY:
        client.set_key(settings.APPWRITE_API_KEY)
    
    return client

# Initialize default clients
client = make_client()
account = Account(client)
db = Databases(client)

def get_tasks():
    """Fetch all tasks from Appwrite database"""
    return db.list_documents(
        settings.DATABASE_ID, 
        settings.TASKS_COLLECTION_ID
    )["documents"]

def get_today_checkins(uid: str):
    """Get today's checkins for a specific user"""
    today = datetime.date.today().isoformat()
    q = [
        Query.equal("user_id", uid), 
        Query.equal("date", today)
    ]
    res = db.list_documents(
        settings.DATABASE_ID, 
        settings.CHECKINS_COLLECTION_ID, 
        queries=q
    )
    return {d["task_id"]: d for d in res["documents"]}

def save_checkin(uid: str, tid: str, done: bool, note: str):
    """Save or update a checkin"""
    today = datetime.date.today().isoformat()
    q = [
        Query.equal("user_id", uid),
        Query.equal("task_id", tid),
        Query.equal("date", today)
    ]
    found = db.list_documents(settings.DATABASE_ID, settings.CHECKINS_COLLECTION_ID, queries=q)
    data = dict(task_id=tid, user_id=uid, date=today, done=done, note=note)
    
    if found["total"]:
        db.update_document(
            settings.DATABASE_ID,
            settings.CHECKINS_COLLECTION_ID,
            found["documents"][0]["$id"],
            data=data
        )
    else:
        db.create_document(
            settings.DATABASE_ID,
            settings.CHECKINS_COLLECTION_ID,
            ID.unique(),
            data=data
        )