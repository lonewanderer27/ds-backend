import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import FastAPI, Query
import uvicorn
from pprint import pprint

# Authorize thyself
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict({
    "type": os.environ["type"],
    "project_id": os.environ["project_id"],
    "private_key_id": os.environ["private_key_id"],
    "private_key": os.environ["private_key"],
    "client_email": os.environ["client_email"],
    "client_id": os.environ["client_id"],
    "auth_uri": os.environ["auth_uri"],
    "token_uri": os.environ["token_uri"],
    "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
    "client_x509_cert_url": os.environ["client_x509_cert_url"]
}, scope)
client = gspread.authorize(creds)

app = FastAPI()

@app.get("/")
async def root(full_data: bool = False):
    sheet = client.open("Developing Stuff").sheet1
    list_of_clients = sheet.get_all_records()

    return {
            "message": "success",
            "clients": list_of_clients if full_data else {},
            "clients_num": len(list_of_clients)
        }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0")