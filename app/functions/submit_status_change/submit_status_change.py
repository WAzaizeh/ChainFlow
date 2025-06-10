from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import os, json
from datetime import datetime

def main(context):
    client = (
        Client()
        .set_endpoint(os.environ["APPWRITE_FUNCTION_ENDPOINT"])
        .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
        .set_key(os.environ["APPWRITE_API_KEY"])
    )

    database = Databases(client)

    taskHistory = json.dumps(context.req.body_json)

    # add not history entry
    try:
        database.create_document(
            database_id=os.environ["APPWRITE_DATABASE_ID"],
            collection_id='task_history',
            document_id=ID.unique(),
            data=taskHistory
        )
        context.log(f"{datetime.now().isoformat()} | History entry added successfully")
        context.log(f"History entry: {taskHistory}")
        return True
    except Exception:
        context.log(f"{datetime.now().isoformat()} | Failed to add history entry")
        context.log(f"Error: {str(Exception)}")
        context.log(f"History entry: {taskHistory}")
        return False
