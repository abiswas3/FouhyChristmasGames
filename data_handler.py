import pandas as pd
import pprint as pp
import random 

df = pd.read_csv('fouhy_connections_school.csv')
tmp = ['hint', 'description', 'word1', 'word2', 'word3', 'word4', 'difficulty', 'group_number'] 
df.columns = tmp + [""]*(len(df.iloc[0])-len(tmp))

df = df.iloc[1:]

GAMES = {int(idx) : game for idx, game in df.groupby("group_number")}
GAMES = dict(sorted(GAMES.items()))

def make_words_short(s, word_size=12):

        return s.strip()
        if len(s) >= word_size and ' ' not in s and '-' not in s:
                return (s[:word_size//2]+"-"+s[word_size//2:]).strip()
        else:
                return s.strip()

def make_game(game):

        # print(game)

        data = {"correct_groups": {}, "descriptions": {}, "hints": {}}

        idx = 1
        for _,  row in game.iterrows():
                data["correct_groups"]["group{}".format(idx)] = [make_words_short(x) for x in row[["word1", "word2", "word3", "word4"]].tolist()]
                data["descriptions"]["group{}".format(idx)] = row["description"]
                data["hints"]["group{}".format(idx)] = row['hint'] 
                idx +=1 

        return data


GAMES = [make_game(game) for _, game in GAMES.items()] 
# pp.pprint(game)
