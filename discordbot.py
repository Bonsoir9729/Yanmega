import discord
import os
from discord.ext import commands
from main import Initialize, UpdateAndGetRankings, GetPlayer, UpdateRating, players

intents = discord.Intents.default()
intents.message_content = True
prefix = '!'
client = commands.Bot(intents=intents, command_prefix=prefix)
replayChannel = 1128031232719073330

@client.event
async def on_ready():
    newGames=[]
    async for i in client.get_channel(replayChannel).history(limit=500) :
        if i.created_at.year == 2024 and i.created_at.month == 3 :
            if 'https://replay.pokemonshowdown.com/gen9customgame-' in i.content :
                newGames.append(ExtractLink(i.content))
    for i in reversed(newGames) :
        UpdateRating(i)
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message) :
    global players
    if message.author == client.user :
        return
    content = message.content.split()
    match content[0] :
        case '!rankings' :
            Initialize()
            rankings = UpdateAndGetRankings()
            ranks = ''
            for i in range(20) :
                ranks += f"{rankings[i].rank}. {rankings[i].name} : {rankings[i].elo} ({rankings[i].matches}P {rankings[i].wins}W {rankings[i].losses}L)\n"
            await message.channel.send(ranks)
            players = []
        case "!rank" :
            Initialize()
            name = ""
            for i in content[1:] :
                name += i
            player = GetPlayer(name)
            try :
                await message.channel.send(f"{player.name} : {player.elo}\nrank : {player.rank}")
            except AttributeError :
                await message.channel.send("Player not found")
            finally :
                players = []
    if message.channel.id != replayChannel :
        return
    if 'https://replay.pokemonshowdown.com/gen9customgame-' in message.content :
        print('New replay shared')
        await message.channel.send(UpdateRating(ExtractLink(message.content)))
        return
    print('Last message was not a replay')

def ExtractLink(message) :
    for i in range(len(message)) :
        if message[i:i+50] == 'https://replay.pokemonshowdown.com/gen9customgame-' :
            return message[i:i+60]

TOKEN = os.getenv('DISCORD_TOKEN')
client.run(TOKEN)