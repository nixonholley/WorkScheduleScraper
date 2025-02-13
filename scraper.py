from utils import parse_csv, convert_to_start_end_time, create_ics
from pprint import pprint
from dotenv import load_dotenv
import os

def scraper():
    load_dotenv()
    filepath = os.getenv('FILEPATH')

    # Parse csv into {'2/10': [{'time': '3:30- 4:30'}, ...],...}
    schedule_raw = parse_csv(filepath)
    pprint(schedule_raw)

    # convert schedule to datetime and merge {'2/10': {'start': '2025-02-10 03:30:00', 'end': '2025-02-10 07:30:00'}, ...}
    schedule = convert_to_start_end_time(schedule_raw)
    pprint(schedule)

    # create ics
    create_ics(schedule)



