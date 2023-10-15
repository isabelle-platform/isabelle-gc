#!/usr/bin/env python3
"""
Isabelle Google Calendar Connector
"""
import argparse
import sys
import pickle
import os.path
import os
from typing import List

from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


sys.path.insert(0, "/Users/mmenshikov/src/isabelle/isabelle-core/isabelle-gc/google-calendar-simple-api")

from gcsa.google_calendar import GoogleCalendar
from gcsa.calendar import Calendar
from gcsa.event import Event
from datetime import *
from gcsa.recurrence import Recurrence

# days of the week
from gcsa.recurrence import SU, MO, TU, WE, TH, FR, SA

# possible repetition frequencies
from gcsa.recurrence import SECONDLY, MINUTELY, HOURLY, \
                            DAILY, WEEKLY, MONTHLY, YEARLY

def prepare_parser():
    """
    Parse common benchmark arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email",
                        help="Target email",
                        default="")
    parser.add_argument("-creds", "--credentials",
                        help="Path to credenetials",
                        default="credentials.json")
    parser.add_argument("-pickle", "--pickle",
                        help="Path to pickle",
                        default="token.pickle")

    parser.add_argument("-c", "--calendar",
                        help="Calendar name",
                        default="Isabelle events")
    parser.add_argument("-d", "--calendar-desc",
                        help="Calendar description",
                        default="Container for Isabelle events")

    # Start/end flow
    parser.add_argument("-flow-start", "--flow-start",
                        help="Start OAuth flow",
                        action='store_true')
    parser.add_argument("-flow-end", "--flow-end",
                        help="End OAuth flow",
                        action='store_true')
    parser.add_argument("-flow-url", "--flow-url",
                        help="OAuth flow url",
                        default="flow.url")
    parser.add_argument("-flow-backlink", "--flow-backlink",
                        help="OAuth flow backlink",
                        default="http://localhost:8081/setting/gcal_auth")
    parser.add_argument("-flow-token", "--flow-token",
                        help="OAuth flow token",
                        default="")

    # Initialize calendar
    parser.add_argument("-init", "--init",
                        help="Initialize calendar",
                        action='store_true')
    # Deinit calendar
    parser.add_argument("-deinit", "--deinit",
                        help="Deinitialize calendar",
                        action='store_true')

    # Add/del event
    parser.add_argument("-add", "--add",
                        help="Add new event",
                        action='store_true')
    parser.add_argument("-delete", "--delete",
                        help="Delete event",
                        action='store_true')
    parser.add_argument("-add-name", "--add-name",
                        help="New event name",
                        default="Event name")
    parser.add_argument("-add-date-time", "--add-date-time",
                        help="New event time",
                        default="2023-10-10 19:00")
    return parser

parser = prepare_parser();
args = parser.parse_args()

if args.flow_start:
    if os.path.exists(args.flow_url):
        os.remove(args.flow_url)
    scopes = [ 'https://www.googleapis.com/auth/calendar' ]
    flow = InstalledAppFlow.from_client_secrets_file(
        args.credentials,
        scopes)
    f = open(args.flow_url, "w")
    auth_url, _ = flow.authorization_url(prompt='consent');
    print(auth_url + "&redirect_uri=" + args.flow_backlink, file=f)
    f.close()

    #credentials = flow.run_local_server(host="localhost", port=8086, open_browser=False)
    with open(args.pickle, 'wb') as token_file:
        pickle.dump(credentials, token_file)
    sys.exit(0)

if args.flow_end:
    if os.path.exists(args.flow_url):
        os.remove(args.flow_url)
    scopes = [ 'https://www.googleapis.com/auth/calendar' ]
    flow = InstalledAppFlow.from_client_secrets_file(
        args.credentials,
        scopes)
    flow.fetch_token(authorization_response=args.flow_token)
    with open(args.pickle, 'wb') as token_file:
        pickle.dump(flow.credentials, token_file)
    sys.exit(0)

gc = GoogleCalendar(args.email, credentials_path=args.credentials)

calendar_id = None
event_id = None
for cal in gc.get_calendar_list():
    if cal.summary == args.calendar:
        print("Found calendar")
        calendar_id = cal.calendar_id
        if args.add or args.delete:
            for event in gc.get_events(calendar_id=calendar_id):
                if event.summary != None:
                    print("Event summary: " + event.summary + " vs " + args.add_name)
                    print("Event start: " + str(event.start) + " vs " + str(datetime.fromisoformat(args.add_date_time)))
                    if event.summary == args.add_name and \
                       str(event.start).startswith(str(datetime.fromisoformat(args.add_date_time))):
                        event_id = event.id

calendar = Calendar(
    args.calendar,
    description=args.calendar_desc
)

if args.init and calendar_id == None:
    calendar = gc.add_calendar(calendar)
if args.deinit and calendar_id != None:
    calendar = gc.delete_calendar(calendar_id)
elif args.add or args.delete:
    if calendar_id == None:
        print("Can't add entry to non-existing calendar");
        sys.exit(1);
    event = Event(
        args.add_name,
        start=datetime.fromisoformat(args.add_date_time),
        recurrence=[
            Recurrence.rule(freq=WEEKLY),
        ],
        destination_calendar_id=calendar_id,
        minutes_before_popup_reminder=15
    )
    if args.add:
        event = gc.add_event(event)
        gc.move_event(event, destination_calendar_id=calendar_id)
        print("Added event to calendar")
    elif event_id != None:
        event = gc.get_event(event_id, calendar_id=calendar_id)
        gc.delete_event(event, calendar_id=calendar_id)
        print("Deleted event from calendar")
    else:
        print("Nothing to delete")
        sys.exit(2)
else:
    sys.exit(3)
sys.exit(0)

