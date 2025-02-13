import pandas as pd
from datetime import datetime
from ics import Calendar, Event
import pytz

def parse_csv(filepath : str) -> dict:
    # Load the CSV file into a DataFrame (ensure header is None as we don't want it to interpret the first row as header)
    df = pd.read_csv(filepath, header=None)

    # Step 1: Extract the first row (which contains the dates) and find the indexes where dates appear
    date_columns = {}
    for idx, value in enumerate(df.iloc[0]):
        if isinstance(value, str) and '/' in value:  # Assuming date format is like '2/10'
            date_columns[idx] = value

    # Step 2: Find the rows that contain the time slots (we'll assume times are in column 0)
    time_rows = []
    for idx, value in enumerate(df.iloc[:, 0]):
        if isinstance(value, str) and '-' in value:  # We assume time range contains a hyphen ('-')
            time_rows.append(idx)  # Store the index of the row with time slot

    # Step 3: Create a dictionary to store the results
    schedule = {}

    # Step 4: Iterate through the DataFrame starting from the second row (excluding header)
    for index, row in df.iloc[1:].iterrows():
        time_slot = None
        
        # Check if this row is a time row (from our time_rows list)
        if index in time_rows:
            time_slot = df.iloc[index, 0]  # Get the time slot for the row
            
        # Look for any names (like 'Nixon') in the row
        for col_idx, cell in enumerate(row):
            if isinstance(cell, str) and 'Nixon' in cell:  # Adjust based on the name you're searching for
                # Find the closest column to the left with a date
                for prev_col in range(col_idx, -1, -1):
                    if prev_col in date_columns:
                        date = date_columns[prev_col]
                        
                        # Add to the dictionary: If date already exists, append, otherwise create a new list
                        if date not in schedule:
                            schedule[date] = []
                        schedule[date].append({'time': time_slot})
    return schedule

def convert_to_start_end_time(schedule : dict) -> dict:
    # Function to convert local time to UTC
    def local_to_utc(local_time):
        local_tz = pytz.timezone('US/Eastern')  # Adjust to your local timezone (e.g., EST)
        
        # Localize the datetime object to your local timezone (only if it's not already localized)
        if local_time.tzinfo is None:
            local_time = local_tz.localize(local_time) 
        
        # Convert to UTC
        utc_time = local_time.astimezone(pytz.utc)  # Convert to UTC
        return utc_time
    
    # Function to convert to datetime (in the desired format)
    def convert_to_datetime(date_str, time_str):
        # Strip unnecessary spaces and combine date and time
        time_str = time_str.strip().replace(' ', '')
        
        # Extract the start time of the time range
        start_time = time_str.split('-')[0]
        
        # Add the year to the date (defaults to 2025 for this example)
        date_str = f"2025-{date_str}"
        
        # Combine date with start time and convert to datetime
        full_datetime_str = f"{date_str} {start_time}"
        
        # Parse the full datetime string to get a datetime object
        date_obj = datetime.strptime(full_datetime_str, '%Y-%m/%d %I:%M')
        
        # Return the datetime object in the format you want
        date_obj = local_to_utc(date_obj)
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')

    # Function to get start and end times for the day
    def get_start_and_end_times(date, time_slots):
        # Get the start time (first time slot)
        start_time = convert_to_datetime(date, time_slots[0]['time'])
        
        # Get the end time (last time slot) - extract the end time from the last time range
        end_time_str = time_slots[-1]['time'].strip().replace(' ', '').split('-')[1]
        end_time = convert_to_datetime(date, end_time_str)
        
        return start_time, end_time

    # Dictionary to store start and end times for each date
    date_times = {}

    # Get start and end datetime for each date
    for date, time_slots in schedule.items():
        start_time, end_time = get_start_and_end_times(date, time_slots)
        
        # Store the start and end times in the dictionary
        date_times[date] = {'start': start_time, 'end': end_time}

    return date_times

def create_ics(schedule : dict) -> None:
    c = Calendar()
    for date in schedule:
        e = Event()
        e.name = 'Work @ Mathnasium'
        e.begin = schedule[date]['start']
        e.end = schedule[date]['end']
        c.events.add(e)

    print(c.serialize())
    with open('mathnasium.ics', 'w') as f:
        f.writelines(c.serialize_iter())