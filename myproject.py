from flask import Flask, render_template, request, jsonify, session
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
def initialize_game(username):
    # Flatten the groups into a list of items
    
    if username not in players_so_far:
        players_so_far[username] = 0
    else:
        players_so_far[username] = (players_so_far[username] + 1) % len(GAMES)

    game_idx = players_so_far[username]
    print("GAME IDX", game_idx)
    game = GAMES[game_idx]

    correct_groups = game["correct_groups"]
    items = sum(correct_groups.values(), [])    
    random.shuffle(items)

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
    session['username'] = username
    session['game_state'] = initialize_game(username)
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
    username = session.get('username')
    game_state = session['game_state']

    last_played = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as 'YYYY-MM-DD HH:MM:SS'

    # Add the score (tries) to the leaderboard
    leaderboard = load_leaderboard()

    first = True
    for row in leaderboard:
        if (row['username'].strip()).lower() == username.strip().lower():
            first = False
            break

    if not first:
        row["score"] = int(row["score"]) + game_state["tries"]
    else:
        leaderboard.append({"username": username, "score": game_state["tries"], "last": last_played})

    leaderboard.sort(key=lambda x: x['score'])  # Sort by tries (ascending)

    # Trim leaderboard to top 10
    # leaderboard = leaderboard[:10]

    # Save the updated leaderboard to the file
    save_leaderboard(leaderboard)

    # Reset game state for a new game
    session['game_state'] = initialize_game()

    return jsonify({"leaderboard": leaderboard, "message": "Score submitted successfully!"})

@app.route('/get_leaderboard')
def get_leaderboard():
    leaderboard = load_leaderboard()
    print("loading leaderboard", leaderboard)
    return jsonify(leaderboard)

@app.route('/get_game_state')
def get_game_state():
    return jsonify(session['game_state'])

if __name__ == '__main__':

    app.run(host='0.0.0.0')
