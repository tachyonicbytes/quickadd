#!/usr/bin/env python

"""Easy script to wrap up the `quickAdd` method for google calendar, and easily
create events from the command-line.

Learn how to get a google calendar api key: https://docs.simplecalendar.io/google-api-key/
Learn how to use the api key: https://developers.google.com/calendar/api/auth

This script is bootstrapped using the google calendar python quickstart:
https://developers.google.com/calendar/api/quickstart/python


Usage:
Add an event:
    quickadd.py Dinner tomorrow at 10

Read all events:
    quickadd.py

Requirements:

    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib google-cloud google-cloud-vision
"""

import datetime
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events"]


def compose_arguments():
    if sys.argv[1:]:
        return " ".join(sys.argv[1:])
    return ""


class Calendar:

    def __init__(self):
        self.creds = self.get_creds()
        try:
            self.service = build("calendar", "v3", credentials=self.creds)
        except HttpError as error:
            print(f"An error occurred: {error}")


    @staticmethod
    def get_creds():
        creds = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(script_dir, "token.json")
        cred_path = os.path.join(script_dir, "credentials.json")

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        cred_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        return creds


    def quick_add(self, arguments):
        """Wraps the quickAdd method"""
        print("`quickAdd`ing", arguments)

        events_result = self.service.events().quickAdd(calendarId="primary", text=arguments).execute()
        events = events_result.get("items", [])
        print(events)


    def list_events(self):
        """Wraps the list method"""

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"    # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])


def main():
    calendar = Calendar()
    calendar.list_events()

    arguments = compose_arguments()
    if arguments:
        calendar.quick_add(arguments)

if __name__ == "__main__":
    main()
