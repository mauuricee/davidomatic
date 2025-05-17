# bot.py
import os # Librairie

import random

import discord # Importation de la librairie Discord
from dotenv import load_dotenv # Librairie Dotenv pour les infos d'environnement

load_dotenv() # Recuperation des donnees du fichier dotenv
TOKEN = os.getenv('TOKEN')
GUILDE = os.getenv("GUILDE")

botIntents = discord.Intents.default() # Intents = donnees requises pour le bot
botIntents.message_content = True

client = discord.Client(intents=botIntents) # Creer le bot

@client.event
async def on_ready():
    print(f"{client.user} s'est connecte avec succes")

@client.event
async def on_message(message):
    if message.author == client.user: # Pour eviter que le bot ne reponde a lui meme
        return


    contenu = message.content.upper() # Pour eviter le case-sensitive (tout mettre em CAPS)

    funfacts_david = [
        "David est le prof le plus sympa mine de rien",
        "David adore les aliens",
        "David est fan de Star Wars",
        "David ne sait pas se raser les cheveux tout seul",
    ]
    
    if "MOUNIR" in contenu:
        await message.reply("Mounir... Tu veux dire Maurice ? Ou alors Pierre !")

    elif "DAVID" in contenu:
        reponse = random.choice(funfacts_david)
        await message.reply(reponse)

    else:
        return

client.run(TOKEN)