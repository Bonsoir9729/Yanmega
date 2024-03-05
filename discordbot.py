import discord
import os
from discord.ext import commands
from main import UpdateRating, getPlayerElo
import rankings

intents = discord.Intents.default()
intents.message_content = True
prefix = '!'
client = commands.Bot(intents=intents, command_prefix=prefix)
replayChannel = 1128031232719073330

@client.event
async def on_ready():
    newGames=[]
    async for i in client.get_channel(replayChannel).history(limit=1000) :
        if i.created_at.year == 2024 and i.created_at.month == 2 :
            if 'https://replay.pokemonshowdown.com/gen9customgame-' in i.content :
                newGames.append(ExtractLink(i.content))
    for i in reversed(newGames) :
        UpdateRating(i)
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message) :
    if message.author == client.user:
        return
    if message.content == f'{prefix}rankings' :
        rankings.Initialize()
        ranks = ['']
        rank = 1
        messages = 0
        for i in rankings.rankList :
            if i[2] < 10 :
                ranks[messages] += f'{i[0]} : {i[1]} ({i[2]} games {i[3]}W {i[2]-i[3]}L) (unranked)\n'
            else :
                ranks[messages] += f'{rank}. {i[0]} : {i[1]} ({i[2]} games {i[3]}W {i[2]-i[3]}L)\n'
                rank += 1
            if len(ranks[messages]) > 1900 :
                messages += 1
                ranks.append('')
        for i in ranks :
            await message.channel.send(i)
        rankings.rankList = []
        return
    if f"{prefix}showrank" == message.content[0:len(prefix)+8] :
        await message.channel.send(getPlayerElo(message.content[len(prefix)+9:], initialised=False)[1])
        return
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