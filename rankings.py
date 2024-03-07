rankList = []

def Initialize():
    with open('rankings.txt', 'r', encoding='utf-8') as file :
        for i in file.readlines() :
            #Player, elo, Games played, wins
            rankList.append([i.split(',')[0].lower(), int(i.split(',')[1]), int(i.split(',')[2]), int(i.split(',')[3])])

def Overwrite():
    rankList.sort(key=lambda player: player[1], reverse=True)
    open('rankings.txt', 'w').close()
    with open('rankings.txt', 'w', encoding='utf-8') as file :
        for i in rankList :
            file.write(f"{i[0].lower()},{int(i[1])},{i[2]},{i[3]}")
            if not rankList.index(i) == len(rankList)-1 :
                file.writelines("\n")