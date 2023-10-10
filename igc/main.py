#!/usr/bin/env python3
"""
Isabelle Google Calendar Connector
"""
import argparse
import sys
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

    parser.add_argument("-c", "--calendar",
                        help="Calendar name",
                        default="Isabelle events")
    parser.add_argument("-d", "--calendar-desc",
                        help="Calendar description",
                        default="Container for Isabelle events")

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

gc = GoogleCalendar(args.email, credentials_path=args.credentials)

calendar_id = None
event_id = None
for cal in gc.get_calendar_list():
    if cal.summary == args.calendar:
        calendar_id = cal.calendar_id
        if args.add or args.delete:
            for event in gc.get_events(calendar_id=calendar_id):
                if event.summary == args.add_name && \
                   event.start == datetime.fromisoformat(args.add_date_time):
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

