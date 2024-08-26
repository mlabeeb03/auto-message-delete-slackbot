from flask import Flask, request, make_response
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
import json
import os

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SIGNING_SECRET = os.environ["SIGNING_SECRET"]

slack_client = WebClient(SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SIGNING_SECRET)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("Invalid request", 400)

    data = request.json

    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type": "application/json"})

    if "event" in data:
        event = data["event"]
        event_type = event["type"]
        if event_type == "reaction_added":
            channel = event["item"]["channel"]
            if channel == "C07ES6K4W3T":
                reaction_count = len(slack_client.reactions_get(channel=channel, timestamp=event["item"]["ts"])["message"]["reactions"])
                if reaction_count == 2:
                    response = slack_client.chat_delete(channel=channel, ts=event["item"]["ts"])
                    return make_response("", response.status_code)
    return make_response("", 200)

@app.route("/slack/pr", methods=["POST"])
def command():
    info = request.form
    response = slack_client.chat_postMessage(
        channel="#{}".format(info["channel_name"]),
        text="(" + request.form.get("user_name") + ") " + request.form.get("text", "nothing"),
    )
    return make_response("", 200)
