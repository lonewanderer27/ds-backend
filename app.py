import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, jsonify, request
from flask_cors import CORS
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

app = Flask(__name__)
CORS(app)


@app.get("/")
def fetch_clients():
    full_data = request.args.get("full_data", False)    # get arg

    sheet = client.open("Developing Stuff").sheet1      
    list_of_clients = sheet.get_all_records()        
    return jsonify({
            "success": True,
            "error": False,
            "clients": list_of_clients if full_data else {},
            "clientsNum": len(list_of_clients)
        })


@app.post("/")
def add_clients():
    sheet = client.open("Developing Stuff").sheet1
    list_of_clients = sheet.get_all_records()
    clientsNum = len(list_of_clients)        

    if clientsNum >= 2:
        return jsonify({
            "success": False,
            "error": True,
            "message": "Maximum number of clients have been reached: 2",
            "clientsNum": clientsNum
        })

    else: 
        sent_payload = request.get_json(silent=True)
        try:
            row = list(sent_payload["row"])
            pprint(row)

            if len(row) != 8:
                return jsonify({
                    "success": False,
                    "error": True,
                    "message": "Malformed request. Row should be a list that contains 8 items."
                })
            
            else:
                index = len(list_of_clients) + 2

                # insert the new data onto last row
                sheet.insert_row(row, index)

                # get the new data so we can count if were over the limit of clients
                list_of_clients = sheet.get_all_records()
                clientsNum = len(list_of_clients)     
                remaining_clients = 2 - clientsNum

                if remaining_clients >= 1:
                    second_message = f"{remaining_clients} more client to go."
                else:
                    second_message = "That's the last client." 

                return jsonify({
                    "success": True,
                    "error": False,
                    "message": f"Client has been registered. " + second_message,
                    "clientsNum": clientsNum
                })

        except Exception as e:
            print(e)
            return jsonify({
                "success": False,
                "error": True,
                "message": 'Malformed request. Request must include row key that contains new client details'
            })
        


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)