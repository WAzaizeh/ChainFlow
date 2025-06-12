from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
from datetime import datetime
from .config import settings
from models.task import Task, Subtask
import uuid

def create_client(authenticated=True) -> Client:
    """Creates an Appwrite client instance with authentication."""
    client = Client()
    client.set_endpoint(settings.APPWRITE_ENDPOINT)
    client.set_project(settings.APPWRITE_PROJECT_ID)
    if authenticated and settings.APPWRITE_API_KEY:
        client.set_key(settings.APPWRITE_API_KEY)
    return client

def get_database():
    client = create_client()
    return Databases(client)

def get_account():
    client = create_client()
    return Account(client)