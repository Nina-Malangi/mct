import datetime
import json
import os
import random
import time

from flask import Flask, request, jsonify

from mct import MCT

app = Flask(__name__)

# constant variables
TASK_VALIDATION = "validation"
TASK_CHANGE_REQUEST = "change_request"
TASK_UPLOAD = "upload"
TASK_VERIFICATION = "verification"
TASK_SUCCESS = "success"
TASK_FAILURE = "failure"


@app.get('/mct/welcome')
def helloworld():
    return " Welcome to Python Flask and Render"


@app.post('/mct/createevent')
def createevent():
    # read the JSON request and convert to mct object
    mctinformation = MCT(**request.json)

    # validate the request and make failure
    isvalid_request = validate_request(mctinformation)

    # create uniqueid for document creation
    uniquie_id = createtimestamp()

    # create the event document
    createdocument(mctinformation, uniquie_id)

    if not isvalid_request:

        # update communication
        update_event_doc(uniquie_id,TASK_VALIDATION, TASK_FAILURE)

        # return error response
        return jsonify({"error": "invalid MCT data"})

    if isvalid_request:

        # update validation success
        update_event_doc(uniquie_id, TASK_VALIDATION, TASK_SUCCESS)        

        # create service now change request
        update_event_doc(uniquie_id, TASK_CHANGE_REQUEST, TASK_SUCCESS)

        # upload the info
        update_event_doc(uniquie_id, TASK_UPLOAD, TASK_SUCCESS)

        # verify the service
        update_event_doc(uniquie_id, TASK_VERIFICATION, TASK_SUCCESS)

        # send success response
        return jsonify({"evnt": uniquie_id})

@app.get("/mct/event/<eventid>")
def getevent_details(eventid):
    with open(f"{eventid}.json", "r", encoding= "utf-8") as file:
        eventdetails = json.load(file)
    
    return eventdetails

@app.get("/mct/events")
def get_all_events():
    events = []
    file_path = os.getcwd()

    # iterate the path and get all the file
    for filename in os.listdir(file_path):
        # filter only json file
        if filename.endswith(".json"):
            # open the file and read the final status
            with open(filename, "r") as file:
                eventInfo = json.load(file)
                event = {
                    "eventID": eventInfo["eventID"],
                    "status": eventInfo["status"],
                    "timestamp": eventInfo["timestamp"]
                }
                events.append(event)

    return jsonify(events)

def createdocument(mct, uniquieid):
    """
    method to create the JSON document with timestamp
    :param uniquieid:
    :param mct:
    """
    event_doc = create_event_doc(uniquieid)
    with open(f"{uniquieid}.json","w", encoding="utf-8") as file:
        json.dump(event_doc, file, indent=4)


def createtimestamp():
    """
    method to create the timestamp     :return:  timestamp
    """
    uniquieID = f"{int(time.time() * 1000)}{random.randint(10, 99)}"
    return uniquieID


def create_event_doc(uniquieid):
    """

    :param uniquieid:
    :return: JSON Object
    """
    event_doc = {
        "eventID": uniquieid,
        "status": "",
        "timestamp": datetime.datetime.now().isoformat(),
        "task": [
            {
                "id": TASK_VALIDATION,
                "status": "",
                "timestamp": ""
            },
            {
                "id": TASK_CHANGE_REQUEST,
                "status": "",
                "timestamp": ""
            },
            {
                "id": TASK_UPLOAD,
                "status": "",
                "timestamp": ""
            },
            {
                "id": TASK_VERIFICATION,
                "status": "",
                "timestamp": ""
            }
        ]

    }
    return event_doc


def validate_request(mct):
    """
    method to validate the JSON reqeust
    :param mct: mct information
    :return: True/False
    """
    if len(mct.airport) != 3:
        return False

    if len(mct.origin_carrier) != 2:
        return False

    if len(mct.dest_carrier) != 2:
        return False

    return True

def update_event_doc(evnt_id, task, status):
    """
    method to update the document
    :param evnt_id: document ID
    :param task: task
    :param status: task status
    """
    with open(f"{evnt_id}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        for event in data["task"]:
            if event["id"] == task:
                event["status"] = status
                event["timestamp"] = datetime.datetime.now().isoformat()

        if "verification" == task and status == "success":
            data["status"] = "success"

    with open(f"{evnt_id}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


if __name__ == '__main__':
    app.run(debug=True)
