import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from collections import deque

app = Flask(__name__)
# Using a deque for efficient append and popleft operations
# It automatically keeps only the last 10 items
messages = deque(maxlen=10)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        if message: # Add message if not empty
            messages.append(message)
        # Redirect to the same page via GET to show the updated list
        # and prevent form resubmission on refresh
        return redirect(url_for('index'))

    # Pass the current list of messages (newest first) to the template
    return render_template('index.html', messages=reversed(list(messages)))

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """API endpoint for the listener to fetch messages."""
    # Return messages as a JSON list (newest first is handled by listener)
    return jsonify(list(messages))

if __name__ == '__main__':
    # For local development only - Render uses gunicorn
    # Use port 5000 locally to avoid clash if listener runs locally too
    app.run(debug=True, port=5000) 