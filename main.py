# bot.py
import os
import random
import json
import discord
from discord import app_commands
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILDE = os.getenv("GUILDE")

# Activer les intents nécessaires
botIntents = discord.Intents.default()
botIntents.message_content = True

# Création du client Discord
client = discord.Client(intents=botIntents)
tree = app_commands.CommandTree(client)

# === Fonctions de gestion du XP ===

def load_xp_data():
    try:
        with open("xp.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_xp_data(data):
    with open("xp.json", "w") as f:
        json.dump(data, f, indent=4)

# === Commande GIF d'Em ===

@tree.command(
    name="gifem",
    description="Le gif préféré d'Em",
    guild=discord.Object(id=GUILDE)
)
async def gif_command(interaction):
    await interaction.response.send_message(
        "https://images-ext-1.discordapp.net/external/gOkUGrzBAn--ds93B_NkxFb2zmhpTE_-c16t908A5P4/https/media.tenor.com/uClJjYhcGQAAAAPo/anteater-drinking-water.mp4"
    )

# === Commande pour envoyer un message personnalisé ===

@tree.command(
    name="sendmsg",
    description="Envoyer un message via le bot",
    guild=discord.Object(id=GUILDE)
)
async def sendmsg_command(interaction, message: str):
    await interaction.response.send_message(message, ephemeral=True)

# === Commande pour afficher son niveau ===

@tree.command(
    name="level",
    description="Affiche ton niveau",
    guild=discord.Object(id=GUILDE)
)
async def level_command(interaction):
    xp_data = load_xp_data()
    user_id = str(interaction.user.id)

    if user_id not in xp_data:
        await interaction.response.send_message("Tu n’as pas encore de niveau. Envoie un message pour commencer !", ephemeral=True)
        return

    level = xp_data[user_id]["level"]
    xp = xp_data[user_id]["xp"]
    next_level_xp = level * 100
    await interaction.response.send_message(f"🧪 Niveau : {level}\n🔋 XP : {xp}/{next_level_xp}")

# === Événement lorsque le bot est prêt ===

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILDE))
    print(f"{client.user} s'est connecté avec succès")

# === Événement lorsqu'un message est envoyé ===

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Gestion du XP
    xp_data = load_xp_data()
    user_id = str(message.author.id)

    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1}

    gain = random.randint(5, 10)
    xp_data[user_id]["xp"] += gain

    xp = xp_data[user_id]["xp"]
    level = xp_data[user_id]["level"]
    next_level_xp = level * 100

    if xp >= next_level_xp:
        xp_data[user_id]["level"] += 1
        await message.channel.send(f"🎉 {message.author.mention} a atteint le niveau {level + 1} !")

    save_xp_data(xp_data)

    # Réactions personnalisées
    contenu = message.content.upper()

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

# Lancer le bot
client.run(TOKEN)
