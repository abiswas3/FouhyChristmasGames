from flask import Flask, render_template, request, jsonify, session
import logging

# Configure logging to write to a file
logging.basicConfig(
    # filename='file.log',  # Log file name
    level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

import random
import json
import os
from datetime import datetime  # Import datetime to generate the current timestamp
from data_handler import GAMES

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secret key for sessions

# Path to the leaderboard file
LEADERBOARD_FILE = 'leaderboard.json'
players_so_far = {}
# Correct groups (hardcoded data)
# correct_groups = {
#     "group1": ["apple is a hero", "banana", "cherry", "grape"],  # Fruits
#     "group2": ["carrot", "broccoli", "spinach", "lettuce"],  # Vegetables
#     "group3": ["dog", "cat", "rabbit", "hamster"],  # Pets
#     "group4": ["earth", "mars", "jupiter", "saturn"]  # Planets
# }

# game = get_random_game(GAMES)
# correct_groups = game["correct_groups"]

# print(correct_groups)

@app.route('/get-options', methods=['GET'])
def get_options():

    # TODO: Change to the ones in the data.
    # Example options to populate the dropdown
    options = [
        {"value": "Christmas Connections", "label": "Fouhy Christmas"},
        # {"value": "sports", "label": "Sports"},
        # {"value": "science", "label": "Science"},
        # {"value": "history", "label": "History"},
    ]
    return jsonify(options)

@app.route('/process-selection', methods=['POST'])
def process_selection():
    data = request.get_json()
    selection = data.get('selection')
    
    # Do something with the selection
    response_message = f"You selected: {selection}"
    logging.debug('{}'.format(response_message))
    return jsonify({"message": response_message})

def clean_string(name):
    return name.strip().lower()

# Load leaderboard from the file
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

# Save leaderboard to the file
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f)

# Initialize game state
def initialize_game(username, selectedCategory):
    
    # Use persistent store
    leaderboard = load_leaderboard()
    # TODO: use selected category to filter games.

    game_idx = 0
    for row in leaderboard:
        if clean_string(row['username']) == clean_string(username):
            game_idx = int(row['last']) % len(GAMES)
            break

    logging.debug(' username {} starting game :{}'.format(username, game_idx))
    game = GAMES[game_idx]

    correct_groups = game["correct_groups"]
    items = sum(correct_groups.values(), [])    
    # random.shuffle(items)

    game_state = {
        "board": items,  # The shuffled 16 items
        "groups": correct_groups,  # Correct groupings
        "completed_groups": [],  # List of successfully completed groups
        "tries": 0,  # Number of tries
        "status": False,
        "descriptions": game["descriptions"],
        "hints": game["hints"]
    }
    return game_state

# Route for starting the game
@app.route('/')
def index():
    return render_template('connections_gen.html')

# Initialize game state for a player
@app.route('/start_game', methods=['POST'])
def start_game():
    username = request.get_json().get('username')
    selectedCategory = request.get_json().get('selectedCategory')
    session['username'] = clean_string(username)
    session['selectedCategory'] = selectedCategory
    session['game_state'] = initialize_game(username, selectedCategory)
    return jsonify({"game_state": session['game_state']})

# Submit the group and check if it is valid
@app.route('/submit_group', methods=['POST'])
def submit_group():
    
    group_key = ""
    selected_items = request.get_json().get("selected_items")
    game_state = session['game_state']

    # Check if the selected items form a valid group
    valid_group = False
    group_description = ""
    group_in_full = ""
    
    # make this better
    for group_name, group in game_state["groups"].items():
        if sorted(selected_items) == sorted(group):
            valid_group = True
            group_description = session['game_state']['descriptions'][group_name]
            group_in_full = session['game_state']['hints'][group_name]
            group_key = group_name
            break

    if valid_group:
        # Remove the selected items from the board and add to completed groups
        game_state["completed_groups"].append(selected_items)
        game_state["board"] = [item for item in game_state["board"] if item not in selected_items]
        
    else:        
        # Increment the try counter
        game_state["tries"] += 1

    session['game_state'] = game_state

    if len(game_state["board"]) == 0:
        game_state["status"] = True

    return jsonify({
        "valid_group": valid_group,
        "game_state": game_state,
        "description": group_description,
        "hint": group_in_full,
        "group_key": group_key
    })

# Submit the score to the leaderboard
@app.route('/submit_score', methods=['POST'])
def submit_score():
    
    username = clean_string(session.get('username'))
    selectedCategory = clean_string(session['selectedCategory'])
    game_state = session['game_state']

    last_played = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as 'YYYY-MM-DD HH:MM:SS'

    # Add the score (tries) to the leaderboard
    leaderboard = load_leaderboard()
    first = True
    for row in leaderboard:
        if clean_string(row['username']) == username:
            first = False
            break

    if not first:
        row["score"] = int(row["score"]) + game_state["tries"]
        row["last"] = int(row["last"]) + 1
    else:
        leaderboard.append({"username": username, "score": game_state["tries"], "last": 1})

    leaderboard.sort(key=lambda x: x['score'])  # Sort by tries (ascending)

    # Save the updated leaderboard to the file
    save_leaderboard(leaderboard)

    # Reset game state for a new game
    session['game_state'] = initialize_game(username, selectedCategory)
    
    return jsonify({"leaderboard": leaderboard,
                    "message": "Score submitted successfully!"})

@app.route('/get_leaderboard')
def get_leaderboard():
    leaderboard = load_leaderboard()
    # print("loading leaderboard", leaderboard)
    return jsonify(leaderboard)

@app.route('/get_game_state')
def get_game_state():
    return jsonify(session['game_state'])

if __name__ == '__main__':

    app.run(debug=True)
    # app.run(host="0.0.0.0")

