from bs4 import BeautifulSoup
import requests

players = []

def GetPlayer(name, create=False) :
    for player in players :
        if player.name.lower() == name.lower() :
            return player
    if create :
        return NewPlayer(name)

def UpdateAndGetRankings(minMatches = 15) :
    rankedPlayers = []
    unrankedPlayers = []
    for player in players :
        if player.matches >= minMatches :
            rankedPlayers.append(player)
        else :
            unrankedPlayers.append(player)
    rankedPlayers.sort(key = lambda player : player.elo, reverse=True)
    unrankedPlayers.sort(key = lambda player : player.elo, reverse=True)
    for i, player in enumerate(rankedPlayers) :
        player.rank = i+1
    return rankedPlayers + unrankedPlayers
        

class Player :
    def __init__(self, name, elo, matches, wins, losses, rank=None):
        self.name = name
        self.elo = int(elo)
        self.matches = int(matches)
        self.wins = int(wins)
        self.losses = int(losses)
        self.rank = rank
        players.append(self)

def NewPlayer(name) :    
    return Player(name, 1000, 0, 0, 0)

def Unserialize(line) :
    string = line[0:-1].split(',')
    Player(string[0], string[1], string[2], string[3], string[4], string[5])
    
def Serialize(self) :
    return f"{self.name},{self.elo},{self.matches},{self.wins},{self.losses},{self.rank}"

def Initialize():
    global players
    players = []
    with open('rankings.txt', 'r', encoding='utf-8') as file :
        for i in file.readlines() :
            Unserialize(i)

def Overwrite():
    global players
    players.sort(key=lambda player : player.elo, reverse=True)
    open('rankings.txt', 'w').close()
    with open('rankings.txt', 'w', encoding='utf-8') as file :
        for player in UpdateAndGetRankings() :
            file.writelines(f"{Serialize(player)}\n")
    players = []

class Battle :
    def __init__(self, players, winner):
        self.players = players
        self.winner = winner

def NewElos(battle, k=60) :
    e1 = 1/(1+10**((battle.players[1].elo-battle.players[0].elo)/1000))
    e2 = 1/(1+10**((battle.players[0].elo-battle.players[1].elo)/1000))
    if battle.winner == battle.players[0].name :
        battle.players[0].elo += int(k*(1-e1))
        battle.players[1].elo -= int(k*e2)
    if battle.winner == battle.players[1].name :
        battle.players[0].elo -= int(k*e1)
        battle.players[1].elo += int(k*(1-e2))
    return (battle.players[0].elo, battle.players[1].elo)

def FindPage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage content: {e}")
        Overwrite()
        return None
    
def ExtractText(url):
    url = f'{url}.log'
    page = FindPage(url)
    if page == None :
        return
    soup = BeautifulSoup(page, 'html.parser')
    return soup.get_text().splitlines()

def BattleData(text) :
    if text == None :
        return
    p = []
    for i in text :
        if i[0:3] == '|j|' :
            p.append(GetPlayer(i[4:].lower(), create=True))
        if i[0:5] == '|win|' :
            return Battle(p, i[5:].lower())


def CheckReplays(url) :
    with open('replays.txt', 'r') as file :
        for i in file.readlines() :
            if i.strip() == url[50:] :
                return True
    return False 

def UpdateRating(url):
    global players
    if CheckReplays(url) :
        return "Replay has already been fetched"
    Initialize()
    battle = BattleData(ExtractText(url))
    if battle == None :
        players = []
        return
    oldElos = [battle.players[0].elo, battle.players[1].elo]
    newElos = NewElos(battle)
    for player in players :
        for j in [0,1] :
            if player.name == battle.players[j].name :
                player.matches += 1
                if player.name == battle.winner :
                    player.wins += 1
                else :
                    player.losses += 1
    Overwrite()
    with open('replays.txt', 'a') as file :
        file.write(f"{url[50:]}\n")
    return f"{battle.players[0].name} : {oldElos[0]} -> {newElos[0]}\n{battle.players[1].name} : {oldElos[1]} -> {newElos[1]}"
