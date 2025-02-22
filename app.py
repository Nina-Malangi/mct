import datetime
import json
import os
import random
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request, jsonify
from mct import MCT

app = Flask(__name__)

# constant variables
TASK_VALIDATION = "validation"
TASK_CHANGE_REQUEST = "change_request"
TASK_UPLOAD = "upload"
TASK_VERIFICATION = "verification"
TASK_SEND_NOTIFICATION = "mail_notification"
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
        update_event_doc(uniquie_id, TASK_VALIDATION, TASK_FAILURE, mctinformation.sender_mail_id)

        # return error response
        return jsonify({"error": "invalid MCT data"})

    if isvalid_request:
        # update validation success
        update_event_doc(uniquie_id, TASK_VALIDATION, TASK_SUCCESS, mctinformation.sender_mail_id)

        # create service now change request
        update_event_doc(uniquie_id, TASK_CHANGE_REQUEST, TASK_SUCCESS, mctinformation.sender_mail_id)

        # upload the info
        update_event_doc(uniquie_id, TASK_UPLOAD, TASK_SUCCESS, mctinformation.sender_mail_id)

        # verify the service
        update_event_doc(uniquie_id, TASK_VERIFICATION, TASK_SUCCESS, mctinformation.sender_mail_id)

        # send success response
        return jsonify({"evnt": uniquie_id})


@app.get("/mct/event/<eventid>")
def getevent_details(eventid):
    try:
        with open(f"{eventid}.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        return jsonify({"error": "File Not found"})


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
    event_doc = create_event_doc(uniquieid,mct.sender_mail_id)
    with open(f"{uniquieid}.json", "w", encoding="utf-8") as file:
        json.dump(event_doc, file, indent=4)


def createtimestamp():
    """
    method to create the timestamp     :return:  timestamp
    """
    uniquieID = f"{int(time.time() * 1000)}{random.randint(10, 99)}"
    return uniquieID


def create_event_doc(uniquieid,sender_mail_id):
    """

    :param uniquieid:
    :return: JSON Object
    """
    event_doc = {
        "eventID": uniquieid,
        "status": "",
        "timestamp": datetime.datetime.now().isoformat(),
        "agent": sender_mail_id,
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


def update_event_doc(evnt_id, task, status, sender_mail_id):
    """
    method to update the document
    :param sender_mail_id:
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

        if "verification" == task and status == TASK_SUCCESS:
            data["status"] = TASK_SUCCESS
            send_notification(data, sender_mail_id, status)

        if status == TASK_FAILURE:
            data["status"] = TASK_FAILURE
            send_notification(data, sender_mail_id, status)

    with open(f"{evnt_id}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def send_notification(data, receiver_mail_id, status):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "naveenmalangi496@gmail.com"
    PASSWORD = "ipko xekb pczz fmji"

    # iterate the data and get status of each task
    task_status = {}
    for event in data["task"]:
        task_status[event["id"]] = event["status"]

    to_email = [receiver_mail_id]
    if status == TASK_FAILURE:
        subject = f' Job {data["eventID"]} has {status}'
    else:
        subject = f' Job {data["eventID"]} completed successfully'

    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <style>
                table {
                  font-family: arial, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }
                
                td, th {
                  border: 1px solid #dddddd;
                  text-align: left;
                  padding: 8px;
                }
                
                tr:nth-child(even) {
                  background-color: #dddddd;
                }
            </style>
        </head>
        <body>

        <h2>MCT Update Task</h2>
        """ + f'''
        <table>
              <tr>
                <th>Task</th>
                <th>Status</th>
              </tr>
              <tr>
                <td>{TASK_VALIDATION}</td>
                <td>{task_status[TASK_VALIDATION]}</td>
              </tr>
              <tr>
                <td>{TASK_CHANGE_REQUEST}</td>
                <td>{task_status[TASK_CHANGE_REQUEST]}</td>
              </tr>
              <tr>
                <td>{TASK_UPLOAD}</td>
                <td>{task_status[TASK_UPLOAD]}</td>
              </tr>
              <tr>
                <td>{TASK_VERIFICATION}</td>
                <td>{task_status[TASK_VERIFICATION]}</td>
              </tr>
        </table>

        </body>
    </html>
    '''

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_mail_id
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(SENDER_EMAIL,PASSWORD)

        smtp.sendmail(SENDER_EMAIL,receiver_mail_id,msg.as_string())
        smtp.quit()
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"SMTP error : {e}")


if __name__ == '__main__':
    app.run(debug=True)
