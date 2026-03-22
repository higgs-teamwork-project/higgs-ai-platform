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
def generate_schedule(matchmaking: list[donor_matches], day: datetime):
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