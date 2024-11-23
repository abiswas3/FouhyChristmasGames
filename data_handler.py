import pandas as pd
import pprint as pp

df = pd.read_csv('fouhy_connections_main.csv')
df.columns = ['hint', 'description', 'word1', 'word2', 'word3', 'word4', 'difficulty', 'group_number']

df = df.iloc[1:]

GAMES = {int(idx) : game for idx, game in df.groupby("group_number")}
GAMES = dict(sorted(GAMES.items()))

def make_game(game):

	# print(game)

	data = {"correct_groups": {}, "descriptions": {}, "hints": {}}

	for idx,  row in game.iterrows():
		data["correct_groups"]["group{}".format(idx)] = [x.strip() for x in row[["word1", "word2", "word3", "word4"]].tolist()]
		data["descriptions"]["group{}".format(idx)] = row["description"]
		data["hints"]["group{}".format(idx)] = row['hint'] 
	
	return data

game = make_game(GAMES[1])
# pp.pprint(game)
