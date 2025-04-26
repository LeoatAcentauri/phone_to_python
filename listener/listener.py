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

# Keep track of message timestamps we've already printed
# Using timestamps as unique identifiers, assuming they are sufficiently unique
printed_message_timestamps = set()

print(f"Listener started. Polling {api_endpoint} every {POLL_INTERVAL} seconds...")

while True:
    try:
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes

        # Expecting a list of dictionaries now
        current_message_dicts = response.json()

        new_messages_to_print = []
        current_timestamps_in_response = set()

        for msg_dict in current_message_dicts:
            # Use timestamp as the unique identifier
            timestamp = msg_dict.get('timestamp')
            if not timestamp:
                # Skip message if it somehow lacks a timestamp (shouldn't happen)
                print(f"Warning: Received message without timestamp: {msg_dict}")
                continue

            current_timestamps_in_response.add(timestamp)

            if timestamp not in printed_message_timestamps:
                new_messages_to_print.append(msg_dict)
                printed_message_timestamps.add(timestamp) # Mark timestamp as printed

        # Clean up old timestamps from our printed set
        printed_message_timestamps.intersection_update(current_timestamps_in_response)

        if new_messages_to_print:
            print(f"--- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            for msg_data in new_messages_to_print:
                # Format the output nicely
                msg_type = msg_data.get('type', 'N/A').upper()
                msg_text = msg_data.get('text', '')
                location = msg_data.get('location')
                original_timestamp = msg_data.get('timestamp', 'N/A') # Display original post time

                print(f" Type: {msg_type}")
                print(f" Text: {msg_text}")
                if location:
                    lat = location.get('lat', 'N/A')
                    lon = location.get('lon', 'N/A')
                    alt = location.get('alt') # Might be None
                    alt_str = f", Alt: {alt:.2f}m" if alt is not None else ""
                    print(f" Location: Lat {lat:.5f}, Lon {lon:.5f}{alt_str}")
                print(f" Posted At: {original_timestamp}")
                print("-" * 10) # Separator for multiple new messages

    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    time.sleep(POLL_INTERVAL) 