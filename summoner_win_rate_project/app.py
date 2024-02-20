from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime, timedelta

# Insert the provided API key directly
RIOT_API_KEY = "RGAPI-4eeaf8c1-98be-4f00-85f3-b37f91be9970"

app = Flask(__name__)

# Util function to convert timestamp to datetime
def from_timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp / 1000)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summoner/<summoner_name>', methods=['GET'])
def get_summoner_winrate(summoner_name):
    # Replace with the appropriate region
    region = 'na1'
    summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
    summoner_response = requests.get(summoner_url)
    if summoner_response.status_code != 200:
        return jsonify({'error': 'Summoner not found'}), 404

    summoner_data = summoner_response.json()
    puuid = summoner_data['puuid']

    # Get matches from the last 20 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=100)
    start_time_timestamp = int(start_time.timestamp() * 1000)
    end_time_timestamp = int(end_time.timestamp() * 1000)

    matches_url = (f"https://americas.api.riotgames.com/lol/match/v5/matches"
                   f"/by-puuid/{puuid}/ids?"
                   f"start=0&count=20&api_key={RIOT_API_KEY}")
    matches_response = requests.get(matches_url)
    if matches_response.status_code != 200:
        return jsonify({'error': 'Error fetching matches'}), 500

    matches = matches_response.json()
    print(matches)

    # Calculate win rate
    wins = 0
    for match_id in matches:
        match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
        match_response = requests.get(match_url)
        if match_response.status_code == 200:
            match_data = match_response.json()
            for participant in match_data['info']['participants']:
                if participant['puuid'] == puuid:
                    if participant['win']:
                        wins += 1
                    break
    
    win_rate = (wins / len(matches)) * 100 if matches else 0

    return jsonify({'summoner_name': summoner_name, 'win_rate': win_rate, 'matches_analyzed': len(matches)})

if __name__ == '__main__':
    app.run(debug=True)