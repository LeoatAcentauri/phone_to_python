import requests
import time
import os
import datetime

# Get the URL of the deployed webapp from environment variable
# Example: https://your-app-name.onrender.com
WEBAPP_URL = os.environ.get("WEBAPP_URL")
POLL_INTERVAL = 5 # seconds

if not WEBAPP_URL:
    print("Error: WEBAPP_URL environment variable not set.")
    print("Please set it to the URL of your deployed web application.")
    exit(1)

# Ensure the URL ends with the correct endpoint
api_endpoint = f"{WEBAPP_URL.rstrip('/')}/api/messages"

# Keep track of messages we've already printed
printed_messages = set()
# Store the messages fetched in the last poll to compare with the new poll
last_fetched_messages = []

print(f"Listener started. Polling {api_endpoint} every {POLL_INTERVAL} seconds...")

while True:
    try:
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes

        current_messages = response.json() # Messages are sent oldest to newest

        # Find messages that are new since the last poll
        # This simple logic assumes message order is consistent and messages aren't deleted mid-list
        new_messages_to_print = []
        for msg in current_messages:
            if msg not in printed_messages:
                 new_messages_to_print.append(msg)
                 printed_messages.add(msg) # Mark as printed

        # Since the deque on the server has a maxlen, old messages disappear.
        # We need to clean up our `printed_messages` set to avoid it growing indefinitely
        # Keep only the messages that are currently present in the fetched list
        current_messages_set = set(current_messages)
        printed_messages.intersection_update(current_messages_set)


        if new_messages_to_print:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"--- {timestamp} ---")
            for msg in new_messages_to_print:
                 print(f"  New: {msg}")
        # else:
            # Optional: print a message if no new messages are found
            # print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] No new messages.")

        last_fetched_messages = current_messages

    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    time.sleep(POLL_INTERVAL) 