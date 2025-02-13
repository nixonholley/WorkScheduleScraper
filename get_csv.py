import os
from dotenv import load_dotenv
import requests

def get_csv():
    # Load environment variables from .env file
    load_dotenv()

    # Get the Google Sheets URL from the environment variable
    google_sheet_url = os.getenv('GOOGLE_SHEET_URL')

    if google_sheet_url:
        # Send GET request to download the CSV
        response = requests.get(google_sheet_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the CSV to a file
            with open('schedule.csv', 'wb') as file:
                file.write(response.content)
            print("CSV downloaded successfully!")
        else:
            print(f"Failed to download CSV. Status code: {response.status_code}")
    else:
        print("Google Sheets URL not found in .env file.")
