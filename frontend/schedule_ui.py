from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, 
                               QWidget, 
                               QScrollArea, 
                               QVBoxLayout, 
                               QSplitter, 
                               QStackedLayout, 
                               QListView, 
                               QPushButton,
                               QMessageBox)
import requests

from datetime import datetime, date, time, timedelta
from pydantic import BaseModel

# generate schedule given a list of donors and matches
# slots is tuples[ngo, datetime slot]

def get_schedule_dicts(meetings: list):
    ngo_schedule = {} # (ngo, time) -> donors
    donor_schedule = {} # (donor, time) -> ngo
    matches = [] # (donor, ngo) meetings that are already set
    for m in meetings:
        ngo_schedule[(m["ngo_id"], m["meeting_time"])] = m["donor_id"]
        matches.append((m["donor_id"], m["ngo_id"]))
        donor_schedule[(m["donor_id"], m["meeting_time"])] = m["ngo_id"]
    return (ngo_schedule, donor_schedule, matches)
    
def get_matches_list(matches: list):
    matches_dict = {}
    for m in list:
        if m["donor_id"] not in matches_dict:
            matches_dict[m["donor_id"]] = [m["ngo_id"]]
        else:
            matches_dict[m["donor_id"]].append(m["ngo_id"])
    return matches_dict 

def update_time_slot(time: datetime, end1: datetime, end2: datetime, start1: datetime, start2: datetime):
    if time > end2:
        return None
    elif time > end1:
        return start2
    else:
        return time + timedelta(minutes=13)

def update_schedule_db(donor_schedule: dict):
    """
    parse tuples - donor schedule has structure (donor id, meeting time) -> ngo id, and 
    schedule db has columns (donor id, ngo id, meeting time)
    """ 
    insert_meetings = [(d[0], donor_schedule[d], d[1]) for d in donor_schedule]    
    payload = {
        "meetings": insert_meetings
    }
    try:
        response = requests.post("http://127.0.0.1:8000/api/schedule/add-many-meetings", json=payload)
        backend_data = response.json()
        
        if response.status_code == 200 and backend_data.get("status") == "success":
            print("added batch of scheduled meetings")
        else:
            print("failed to add meetings")    
    except requests.exceptions.ConnectionError:
        print("Could not connect to the backend server to add meetings.")


def generate_schedule(meetings: list, matches: list, DAY1: datetime):
    """
    generate a schedule of meetings for donor x ngo matches in param matches, according to prexisting meetings from param meetings and on event day param day1. 
    matches is a dictionary of saved_matches rows from db.
    meetings is a dictionary of schedule rows from db.
    If you want to generate meetings for a single donor:
    meetings = all pre-existing meetings
    matches = all elements are from same donor, [{"donor_id": int, "ngo_id": int}
    """
    START_DAY1 = datetime.combine(DAY1, time(15,0))
    END_DAY1 = datetime.combine(DAY1, time(17,0))

    START_DAY2 = datetime.combine(DAY1 + timedelta(days=1), time(15,0))
    END_DAY2 = datetime.combine(DAY1 + timedelta(days=1), time(17, 0))

    ngo_schedule, donor_schedule, existing_matches = get_schedule_dicts(meetings=meetings)
    donors = get_matches_list(matches=matches)

    for donor in donors: 
        match_list = donors[donor] # for readability
        for ngo in match_list:
            # if meeting does not already exist
            if (donor, ngo) not in existing_matches:
                """ 
                Add a meeting if both donor + ngo dont already have a meeting at that time
                there are a max of 4*60 / 13 available slots, 3pm-5pm for 2 days. therefore not a long
                loop to search manually + ensures no gaps that aren't breaks.
                """

                CURRENT_TIME = START_DAY1
                found = False
                while not found:
                    if (ngo, CURRENT_TIME) not in ngo_schedule and (donor, CURRENT_TIME) not in donor_schedule:
                        # add to schedules.
                        ngo_schedule[(ngo, CURRENT_TIME)] = donor
                        donor_schedule[(donor, CURRENT_TIME)] = ngo 
                        found = True
                        existing_matches.append((donor, ngo))
                    else:
                        CURRENT_TIME = update_time_slot(CURRENT_TIME, END_DAY1, END_DAY2, START_DAY1, START_DAY2) ## update according to constraints
                        if CURRENT_TIME == None: ## not possible to find a match.
                            ngo_schedule[(ngo, None)] = donor
                            donor_schedule[(donor, None)] = ngo   
                            found = True # stop loop     
                            existing_matches.append((donor, ngo))                      
        ## update db with new meetings
        update_schedule_db(donor_schedule)

class Schedule(QWidget):
    def __init__(self, data):
        super().__init__()

        # grid -> col 1 label -> col 2 label

    def remake(self, schedule):
        return