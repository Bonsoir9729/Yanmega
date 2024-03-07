from bs4 import BeautifulSoup
import requests
import rankings

def FindPage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage content: {e}")
        return None
    
def ExtractText(url):
    url = f'{url}.log'
    print(url)
    soup = BeautifulSoup(FindPage(url), 'html.parser')
    return soup.get_text().splitlines()

def BattleData(text) :
    player1 = text[0][4:].lower()
    player2 = text[1][4:].lower()
    for i in text :
        if i[0:5] == '|win|' :
            winner = i[5:].lower()
    return (player1, player2, winner)

def addNewPlayer(name):
    rankings.rankList.append([name.lower(), 1000, 0, 0])

def getPlayerElo(name, initialised = True):
    if not initialised :
        rankings.Initialize()
    for i in rankings.rankList:
        if i[0] == name :
            if not initialised :
                rankings.rankList = []
            return [name, i[1], i[2]]
    addNewPlayer(name)
    if not initialised :
        rankings.rankList = []
        return [None, "User not found"]
    return [name, 1000, 0]

def eloDiff(player1, player2, winner):
    with open('log.txt', 'a', encoding='utf-8') as log :
        log.write(f"{player1[0]},{player1[1]},{player1[2]},{player2[0]},{player2[1]},{player2[2]},")
    e1 = 1/(1+10**((player2[1]-player1[1])/1000))
    e2 = 1/(1+10**((player1[1]-player2[1])/1000))
    k = 60
    if winner == player1[0] :
        player1[1] += int(k*(1-e1))
        player2[1] -= int(k*e2)
    else :
        player1[1] -= int(k*e1)
        player2[1] += int(k*(1-e2))
    if player1[1] < 100 :
        player1[1] = 100
    if player2[1] < 100 :
        player2[1] = 100
    with open('log.txt', 'a') as log :
        log.write(f"{player1[1]},{player2[1]}\n")
    return (player1[1], player2[1])

def CheckReplays(url) :
    with open('replays.txt', 'r') as file :
        for i in file.readlines() :
            if i.strip() == url[50:] :
                return True
    return False 

def UpdateRating(url):
    if CheckReplays(url) :
        print("Replay has already been updated")
        return
    rankings.Initialize()
    data = BattleData(ExtractText(url))
    player1 = getPlayerElo(data[0])
    player2 = getPlayerElo(data[1])
    newElos = eloDiff(getPlayerElo(data[0]), getPlayerElo(data[1]), data[2])
    for i in rankings.rankList :
        if i[0] == data[0] :
            i[1] = newElos[0]
            i[2] += 1
            if data[0] == data[2] :
                i[3] += 1
        if i[0] == data[1] :
            i[1] = newElos[1]
            i[2] += 1
            if data[1] == data[2] :
                i[3] += 1
    rankings.Overwrite()
    with open('replays.txt', 'a') as file :
        file.write(f"{url[50:]}\n")
    rankings.rankList = []
    return f"{data[0]} : {player1[1]} -> {newElos[0]}\n{data[1]} : {player2[1]} -> {newElos[1]}"
