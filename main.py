# bot.py
import os
import random
import json
import discord
from discord import app_commands
from dotenv import load_dotenv

# --- Données temporaires simulées ---
collection_groupes = {}

# --- Chargement des variables d'environnement ---
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILDE = os.getenv("GUILDE")

# --- Intents du bot ---
botIntents = discord.Intents.default()
botIntents.message_content = True

client = discord.Client(intents=botIntents)
tree = app_commands.CommandTree(client)

# === SYSTÈME D'XP ===

def load_xp_data():
    try:
        with open("xp.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_xp_data(data):
    with open("xp.json", "w") as f:
        json.dump(data, f, indent=4)

# === COMMANDES SLASH ===

@tree.command(
    name="creergroupe",
    description="Créer un groupe",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe à créer"
)
async def creategroup_command(interaction, groupe: str):
    if groupe in collection_groupes:
        await interaction.response.send_message(f"❌ Le groupe **{groupe}** existe déjà.", ephemeral=True)
    else:
        collection_groupes[groupe] = []
        await interaction.response.send_message(f"✅ Groupe **{groupe}** créé avec succès.", ephemeral=True)

@tree.command(
    name="supprimergroupe",
    description="Supprimer un groupe",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe à supprimer"
)
async def removegroup_command(interaction, groupe: str):
    if groupe in collection_groupes:
        del collection_groupes[groupe]
        await interaction.response.send_message(f"🗑️ Groupe **{groupe}** supprimé avec succès.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Le groupe **{groupe}** n'existe pas.", ephemeral=True)

@tree.command(
    name="level",
    description="Afficher ton niveau et ton XP",
    guild=discord.Object(id=GUILDE)
)
async def level_command(interaction):
    user_id = str(interaction.user.id)
    xp_data = load_xp_data()
    
    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1}

    xp = xp_data[user_id]["xp"]
    level = xp_data[user_id]["level"]
    next_level = level * 100

    await interaction.response.send_message(
        f"📊 {interaction.user.mention}, tu es niveau **{level}** avec **{xp} XP**. Prochain niveau à **{next_level} XP**.",
        ephemeral=True
    )

# === ÉVÉNEMENTS DU BOT ===

@client.event
async def on_ready():
    print(f"{client.user} s'est connecté avec succès.")
    try:
        await tree.sync(guild=discord.Object(id=GUILDE))
        print("✅ Commandes slash synchronisées.")
    except Exception as e:
        print(f"Erreur de synchronisation : {e}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # XP automatique à chaque message
    user_id = str(message.author.id)
    xp_data = load_xp_data()

    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1}

    gain = random.randint(5, 10)
    xp_data[user_id]["xp"] += gain

    current_xp = xp_data[user_id]["xp"]
    current_level = xp_data[user_id]["level"]
    xp_needed = current_level * 100

    if current_xp >= xp_needed:
        xp_data[user_id]["level"] += 1
        xp_data[user_id]["xp"] = 0
        await message.channel.send(f"🎉 {message.author.mention} a atteint le niveau **{current_level + 1}** !")

    save_xp_data(xp_data)

    # Réponses fun
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

# === LANCEMENT DU BOT ===
client.run(TOKEN)
