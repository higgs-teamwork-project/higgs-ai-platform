from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, 
                               QScrollArea, 
                               QGridLayout,
                               QLabel,
                               QVBoxLayout,
                               QListWidget)
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
        if isinstance(m["meeting_time"], str):
            meeting_time_dt = datetime.strptime(m["meeting_time"], "%Y-%m-%d %H:%M:%S")
        else:
            meeting_time_dt = m["meeting_time"]
        ngo_schedule[(m["ngo_id"], meeting_time_dt)] = m["donor_id"]
        matches.append((m["donor_id"], m["ngo_id"]))
        donor_schedule[(m["donor_id"], meeting_time_dt)] = (m["ngo_id"], m["ngo_name"])
    return (ngo_schedule, donor_schedule, matches)
    
def get_matches_list(matches: list):
    matches_dict = {}
    for m in matches:
        if m["donor_id"] not in matches_dict:
            matches_dict[m["donor_id"]] = [(m["ngo_id"], m["ngo_name"])]
        else:
            matches_dict[m["donor_id"]].append((m["ngo_id"], m["ngo_name"]))
    return matches_dict 

def update_time_slot(t: datetime, end1: datetime, end2: datetime, start1: datetime, start2: datetime):
    if (t + timedelta(minutes=28)) >= end2: # take into account when the next meeting will end
        return None
    elif (t + timedelta(minutes=28)) >= end1 and t < start2:
        return start2
    else:
        # add breaks at around 4pm and around 5pm
        t_time = t.time()
        if t_time == time(16, 50):
            return t.replace(hour=17, minute=10, second=0, microsecond=0)
        elif t_time == time(15, 45):
            return t.replace(hour=16, minute=5, second=0, microsecond=0)
        else:
            return t + timedelta(minutes=15)

def update_schedule_db(donor_schedule: dict, donor_name: str):
    print("updating db")
    """
    parse tuples - donor schedule has structure (donor id, meeting time) -> ngo id, and 
    schedule db has columns (donor id, ngo id, meeting time)
    """ 
    #    insert_meetings = [[d[0], donor_schedule[d][0], donor_schedule[d][1], d[1].isoformat()] for d in donor_schedule]    
    insert_meetings = []
    for d in donor_schedule:
        clean_name = donor_schedule[d][1].replace('“', '"').replace('”', '"').replace('’', "'")
        if d[1] is None:
            clean_date = None
        else:
            clean_date = d[1].isoformat()
        insert_meetings.append([d[0], donor_schedule[d][0], donor_name, clean_name, clean_date])
    
    payload = {
        "meetings": insert_meetings
    }
    try:
        #print(insert_meetings)
        response = requests.post("http://127.0.0.1:8000/api/schedule/add-many-meetings", json=payload)
        backend_data = response.json()
        
        if response.status_code == 200 and backend_data.get("status") == "success":
            print("added batch of scheduled meetings")
        else:
            print("failed to add meetings")   
            print(response.text) 
    except requests.exceptions.ConnectionError:
        print("Could not connect to the backend server to add meetings.")

def generate_schedule(meetings: list, matches: list, DAY1: datetime, donor_name: str):
    print("GENERATING SCHEDULE")
    """
    generate a schedule of meetings for donor x ngo matches in param matches, according to prexisting meetings from param meetings and on event day param day1. 
    matches is a dictionary of saved_matches rows from db.
    meetings is a dictionary of schedule rows from db.
    If you want to generate meetings for a single donor:
    meetings = all pre-existing meetings
    matches = all elements are from same donor, [{"donor_id": int, "ngo_id": int}
    note that the time slot is the START of the meeting, not the END. Assumr all meetings last for 13 mins.
    2 mins breaks are placed between meetings as per spec.
    """
    START_DAY1 = datetime.combine(DAY1, time(15,0))
    END_DAY1 = datetime.combine(DAY1, time(18,0))

    START_DAY2 = datetime.combine(DAY1 + timedelta(days=1), time(15,0))
    END_DAY2 = datetime.combine(DAY1 + timedelta(days=1), time(18, 0))

    ngo_schedule, donor_schedule, existing_matches = get_schedule_dicts(meetings=meetings)
    donors = get_matches_list(matches=matches)
    #print(donors)
    for donor in donors: 
        match_list = donors[donor] # for readability
        for ngo in match_list:
            # if meeting does not already exist
            if (donor, ngo[0]) not in existing_matches:
                """ 
                Add a meeting if both donor + ngo dont already have a meeting at that time
                there are a max of 6*60 / 13 available slots, 3pm-6pm for 2 days. therefore not a long
                loop to search manually + ensures no gaps that aren't breaks.
                """

                CURRENT_TIME = START_DAY1
                found = False
                while not found:
                   # print(f"Looping: Time={CURRENT_TIME}, InNGO={ (ngo[0], CURRENT_TIME) in ngo_schedule }, InDonor={ (donor, CURRENT_TIME) in donor_schedule }")
                   # print(ngo)
                   # print(ngo_schedule)
                   # print(donor_schedule)
                    if (ngo[0], CURRENT_TIME) not in ngo_schedule and (donor, CURRENT_TIME) not in donor_schedule:
                        # add to schedules.
                        ngo_schedule[(ngo[0], CURRENT_TIME)] = donor
                        donor_schedule[(donor, CURRENT_TIME)] = ngo 
                        found = True
                        existing_matches.append((donor, ngo[0]))
                    else:
                        CURRENT_TIME = update_time_slot(CURRENT_TIME, END_DAY1, END_DAY2, START_DAY1, START_DAY2) ## update according to constraints
                        if CURRENT_TIME == None: ## not possible to find a match.
                            ngo_schedule[(ngo[0], None)] = donor
                            donor_schedule[(donor, None)] = ngo   
                            found = True # stop loop     
                            existing_matches.append((donor, ngo[0]))                      
    ## update db with new meetings
    update_schedule_db(donor_schedule, donor_name)

def get_rows_cols_dict(DAY1: datetime):
    START_DAY1 = datetime.combine(DAY1, time(15,0))
    END_DAY1 = datetime.combine(DAY1, time(18,0))

    START_DAY2 = datetime.combine(DAY1 + timedelta(days=1), time(15,0))
    END_DAY2 = datetime.combine(DAY1 + timedelta(days=1), time(18, 0))

    cur = START_DAY1
    result = {} # time -> day, column
    row = 1
    col = 1
    while cur:
        result[cur] = (row, col)
        cur = update_time_slot(cur, end1=END_DAY1, end2=END_DAY2, start1=START_DAY1, start2=START_DAY2)
        if cur == START_DAY2:
            col = 2
            row = 1
        else:
            row = row + 1
    return result


class UnassignedTab(QWidget):
    def __init__(self, names):
        super().__init__()
        self.main_layout = QVBoxLayout()

        self.none_lbl = QLabel("No NGO meetings are unscheduled for this donor.")
        self.main_layout.addWidget(self.none_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        self.names_box = QListWidget()
        self.main_layout.addWidget(self.names_box)

        self.setLayout(self.main_layout)
        self.remake(names=names)

    def remake(self, names):
        if len(names) == 0:
            self.names_box.hide()
            self.none_lbl.show()
        else:
            self.none_lbl.hide()
            self.names_box.show()
            names_str = [m["ngo_name"] for m in names]
            self.names_box.addItems(names_str)

class Schedule(QScrollArea):
    def __init__(self, data, day_1: datetime, unassigned: UnassignedTab):
        super().__init__()
        self.lbl = QLabel("There are no matches for this donor.")

        schedule_content = QWidget()
        self.schedule_grid = QGridLayout()
        self.schedule_grid.setSpacing(5)
        schedule_content.setLayout(self.schedule_grid)
        self.setWidgetResizable(True)
        self.setWidget(schedule_content)
        self.unassigned_tab = unassigned
        self.time_mapping = get_rows_cols_dict(day_1)

        self.schedule_grid.addWidget(self.lbl, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl.hide()

        self.remake(data)

    def remake(self, schedule):
        if len(schedule) == 0:
            self.lbl.show()
            self.unassigned_tab.remake([])
        else:
            self.lbl.hide()
            # make tabs that say day 1 and day 2
            time_heading_lbl = QLabel("MEETING TIME")
            time_heading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_1_lbl = QLabel("DAY 1")
            day_1_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_2_lbl = QLabel("DAY 2")
            day_2_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.schedule_grid.addWidget(time_heading_lbl, 0, 0)
            self.schedule_grid.addWidget(day_1_lbl, 0, 1)
            self.schedule_grid.addWidget(day_2_lbl, 0, 2)

            time_heading_lbl.setProperty("styling", "timeslotheading")
            day_1_lbl.setProperty("styling", "scheduleheading")
            day_2_lbl.setProperty("styling", "scheduleheading")

            # make times in column 0 
            r = 1
            times_set = {t.time() for t in self.time_mapping}
            sorted_times = sorted(list(times_set))
            for t in sorted_times:
                t_dt = datetime.combine(datetime(2026, 1, 1), t)
                t_end = (t_dt + timedelta(minutes=13)).time()
                meeting_time = str(t.strftime("%H:%M") + " - " + t_end.strftime("%H:%M"))
                time_lbl = QLabel(meeting_time)
                time_lbl.setProperty("styling", "timeslotlbl")
                time_lbl.setWordWrap(True)
                self.schedule_grid.addWidget(time_lbl, r, 0)
                r = r + 1


            unassigned_meetings = []
            for meeting in schedule:
                name_lbl = QLabel(meeting["ngo_name"])
                if meeting["meeting_time"] is None:
                    unassigned_meetings.append(meeting)                    
                else:
                    meeting_time_dt = datetime.strptime(meeting["meeting_time"], "%Y-%m-%d %H:%M:%S")
                    row = self.time_mapping[meeting_time_dt][0]
                    col = self.time_mapping[meeting_time_dt][1]
                    name_lbl.setProperty("styling", "nameslotlbl")
                    name_lbl.setWordWrap(True)
                    self.schedule_grid.addWidget(name_lbl, row, col)
            self.unassigned_tab.remake(unassigned_meetings)