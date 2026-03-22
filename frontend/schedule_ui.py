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

class donor_schedule:
    def __init__(self, donor: int):
        self.donor = donor
        self.slots = []

class donor_matches():
    def __init__(self, donor, matches):
        self.donor = donor
        self.matches = matches

# take a list of donors and their matches
def generate_schedule_B(matchmaking: list[donor_matches], day: datetime):
    START_DAY1 = datetime.combine(day, time(15,0))
    END_DAY1 = datetime.combine(day, time(17,0))

    START_DAY2 = datetime.combine(day + timedelta(days=1), time(15,0))
    END_DAY2 = datetime.combine(day + timedelta(days=1), time(17, 0))

    schedule = {}
    no_matches = []
    flipped_schedule = {}

    # runtime = number of matches
    for donor in matchmaking:
        current_slot = START_DAY1 - timedelta(minutes=13) ## so 3pm included. this represents the start of a slot.
        flipped_schedule[donor.donor] = donor_schedule(donor=donor.donor)
        for match in donor.matches:
            found = False
            while (not found):
                if (current_slot > END_DAY2):
                    schedule[(match, None)] = donor.donor # no slot available
                    no_matches.append((donor.donor, match))
                    break
                elif (current_slot > END_DAY1):
                    current_slot = START_DAY2
                else:
                    current_slot = current_slot + timedelta(minutes=13)
                
                if (match, current_slot) not in schedule: # if the ngo is not occupied at this time
                    schedule[(match, current_slot)] = donor.donor # add appointment
                    flip_schedule[donor.donor].slots.append((match, current_slot))
                    found = True
    
    return (schedule, flipped_schedule, no_matches)

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




        


def flip_schedule(schedule: dict[tuple[str, datetime], str]):
    # key: donor as a string, value: donor_schedule
    new_schedule = {} # this will include cases when the donor does not have a slot for an ngo ie has too many ngos
    # go through schedule
    for slot in schedule:
        if schedule[slot] not in new_schedule: # if the donor hasnt been in the new schedule
            # add them to the schedule
            new_schedule[schedule[slot]] = donor_schedule(schedule[slot])
            # add the current slot
            new_schedule[schedule[slot]].slots.append(slot)

    return new_schedule 

def init_donor_matches(window: QWidget):
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/getmatches/all")
        data = response.json() # get list of dictionaries
        print(data)
        if len(data) == 0:
            return []
        else: 
            data_list = []
            


    except:
        QMessageBox.critical(window, "Server Error", "Could not retrieve donors. Please try again later.")
        return None
    
class Schedule(QWidget):
    def __init__(self):
        super().__init__()