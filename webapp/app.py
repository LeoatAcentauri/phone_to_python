import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from collections import deque
import datetime # Optional: for timestamping messages

app = Flask(__name__)
# Store dictionaries now: {'type': 'comment', 'text': '...', 'location': {...}, 'timestamp': ...}
messages = deque(maxlen=10)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg_type = request.form.get('message_type', 'comment') # Default to comment
        msg_text = request.form.get('message')
        include_geo = request.form.get('include_geolocation') == 'true'
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        altitude = request.form.get('altitude')

        if msg_text: # Only add if message text is not empty
            message_data = {
                'type': msg_type,
                'text': msg_text,
                'location': None,
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z' # Store timestamp
            }

            if include_geo and latitude and longitude:
                try:
                    # Convert coordinates to float, handle altitude being potentially empty/null
                    loc = {
                        'lat': float(latitude),
                        'lon': float(longitude),
                        'alt': float(altitude) if altitude else None
                    }
                    message_data['location'] = loc
                except (ValueError, TypeError):
                    # Handle cases where coordinates are not valid numbers (shouldn't happen with JS validation)
                    print(f"Warning: Could not parse coordinates: lat={latitude}, lon={longitude}, alt={altitude}")
                    pass # Store message without location if parsing fails

            messages.append(message_data)

        # Redirect to GET to show updated list and prevent resubmission
        return redirect(url_for('index'))

    # Pass the current list of messages (newest first) to the template
    # The list contains dictionaries now
    return render_template('index.html', messages=reversed(list(messages)))

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """API endpoint for the listener to fetch messages."""
    # Return the list of message dictionaries
    return jsonify(list(messages))

if __name__ == '__main__':
    # For local development only - Render uses gunicorn
    # Use port 5000 locally to avoid clash if listener runs locally too
    app.run(debug=True, port=5000) 