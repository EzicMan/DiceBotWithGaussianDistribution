import os

import discord
import settings
import numpy as np
from scipy.integrate import quad
from math import sqrt
import random
import re

TOKEN = settings.TOKEN

client = discord.Client()

def parseStr(diceStr, daemonMode):
    diceStr = diceStr.split(" ")
    repeats = 1
    if len(diceStr) > 1:
        repeats = int(diceStr[0])
    diceStr = diceStr[len(diceStr) - 1]
    diceStr = ' ' + diceStr
    ans = ''
    for i in range(0,repeats):
        tempDiceStr = diceStr
        cubesStr = ''
        x = re.findall('[ \+\-\*\/][\+\-]d(?:\([\+\-]?[0-9]+\))?[0-9]+',tempDiceStr)
        for current in x:
            stat = 0
            foundStat = re.search('(\([\+\-]?[0-9]+\))',current)
            newCur = current
            if foundStat != None:
                stat = int(current[foundStat.start()+1:foundStat.end()-1])
                newCur = current[:foundStat.start()] + current[foundStat.end():]
            newCur = newCur[1:]
            replaceBy = 0
            rolling = newCur[1:].split('d')
            a,cubesStr = rollDice(int(rolling[1]),2,cubesStr,stat, daemonMode)
            if newCur[0] == '+':
                replaceBy = max(a)
            else:
                replaceBy = min(a)
            tempDiceStr = tempDiceStr.replace(current, str(replaceBy), 1)
        x = re.findall('[0-9]*d(?:\([\+\-]?[0-9]+\))?[0-9]+',tempDiceStr)
        for current in x:
            stat = 0
            foundStat = re.search('(\([\+\-]?[0-9]+\))',current)
            newCur = current
            if foundStat != None:
                stat = int(current[foundStat.start()+1:foundStat.end()-1])
                newCur = current[:foundStat.start()] + current[foundStat.end():]
            replaceBy = 0
            rolling = newCur.split('d')
            if(rolling[0] == ''):
                rolling[0] = '1'
            delim = '+'
            diceRes,cubesStr = rollDice(int(rolling[1]),int(rolling[0]),cubesStr,stat,daemonMode)
            replaceBy = delim.join(map(str,diceRes))
            replaceBy = '(' + replaceBy + ')'
            tempDiceStr = tempDiceStr.replace(current, replaceBy, 1)
        ans += '`' + cubesStr + '` Result: `' + str(eval(tempDiceStr)) + '`\n'
    return ans

def rollDice(num, k, cubesStr, stat, daemonMode):
    val = [0] * num
    realP = 0
    mu = (num + 1) / 2
    sig = mu / 3
    mu += stat
    for n in range(1,num+1):
        val[n-1],_ = quad(lambda x : 1/(sqrt(2*np.pi) * sig) * np.e**(-(x-mu)**2/(2*sig**2)), n-0.5, n+0.5)
        realP += val[n-1]
    realP = 1 - realP
    realP /= num
    for n in range(0,num):
        val[n] += realP
    retVal = random.choices(list(range(1,num+1)),list(range(1,num+1)) if daemonMode else val,k=k)
    cubesStr += str(retVal)
    return retVal, cubesStr


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!roll '):
        diceStr = message.content[6:]
        try:
            roll = parseStr(diceStr, False)
            await message.channel.send(f'USING MY DICᵉ ON {message.author.nick if message.author.nick != None else message.author.name}:\n{roll}')
        except Exception as e:
            await message.channel.send(f"Expression down! There's a spy 'round 'ere: `{e}`")
    if message.content.startswith('!roII '):
        diceStr = message.content[6:]
        try:
            roll = parseStr(diceStr,True)
            await message.channel.send(f'USING MY DICᵉ ON {message.author.nick if message.author.nick != None else message.author.name}:\n{roll}')
        except Exception as e:
            await message.channel.send(f"Expression down! There's a spy 'round 'ere: `{e}`")
        

client.run(TOKEN)
