# bot.py
import os
import random
import discord
from discord import app_commands
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILDE = os.getenv("GUILDE")

# Initialiser les intentions
botIntents = discord.Intents.default()
botIntents.message_content = True

# Créer le client Discord
client = discord.Client(intents=botIntents)
tree = app_commands.CommandTree(client)

# Dictionnaire pour stocker les groupes (temporaire)
collection_groupes = {}

# Dictionnaire pour stocker l'XP et le niveau des utilisateurs
user_xp_data = {}  # Format : {user_id: {"xp": int, "level": int}}

# Commande /creergroupe
@tree.command(
    name="creergroupe",
    description="Commande pour créer un groupe (temporaire)",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe à créer"
)
async def creategroup_command(interaction, groupe: str):
    collection_groupes[groupe] = []
    await interaction.response.send_message(f"✅ Groupe **{groupe}** créé avec succès !")

# Commande /supprimergroupe
@tree.command(
    name="supprimergroupe",
    description="Commande pour supprimer un groupe (temporaire)",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe à supprimer"
)
async def removegroup_command(interaction, groupe: str):
    if groupe in collection_groupes:
        del collection_groupes[groupe]
        await interaction.response.send_message(f"🗑️ Groupe **{groupe}** supprimé.")
    else:
        await interaction.response.send_message(f"⚠️ Groupe **{groupe}** introuvable.")

# Commande /level
@tree.command(
    name="level",
    description="Affiche ton niveau et ton XP",
    guild=discord.Object(id=GUILDE)
)
async def level_command(interaction):
    user_id = str(interaction.user.id)
    data = user_xp_data.get(user_id, {"xp": 0, "level": 1})
    xp = data["xp"]
    level = data["level"]
    next_xp = level * 100
    await interaction.response.send_message(
        f"📊 {interaction.user.mention}, tu es au **niveau {level}** avec **{xp} XP**. Prochain niveau à **{next_xp} XP**."
    )

# Commande /presentation
@tree.command(
    name="presentation",
    description="Présentation du bot",
    guild=discord.Object(id=GUILDE)
)
async def presentation_command(interaction):
    await interaction.response.send_message(
        "👋 Salut ! Je suis un bot Discord créé pour t'accompagner dans le serveur.\n"
        "Je propose : des commandes fun (/magicresponse, /coinflip), un système de niveaux, des groupes, et plus encore !\n"
        "Tape `/` pour voir toutes mes commandes disponibles 😎"
    )

# Commande /magicresponse (anciennement /8ball)
@tree.command(
    name="magicresponse",
    description="Pose une question, et reçois une réponse magique 🎱",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    question="Ta question pour la boule magique"
)
async def magicresponse_command(interaction, question: str):
    reponses = [
        "Oui.", "Non.", "Peut-être.", "Absolument !", "Je ne pense pas.",
        "Demande plus tard.", "C'est sûr.", "Tu plaisantes, j'espère ?", "Sans aucun doute.", "Hmm... douteux."
    ]
    await interaction.response.send_message(f"🎱 Question : *{question}*\nRéponse : **{random.choice(reponses)}**")

# Événement quand le bot est prêt
@client.event
async def on_ready():
    print(f"{client.user} s'est connecté avec succès")
    try:
        await tree.sync(guild=discord.Object(id=GUILDE))
        print("✅ Commandes synchronisées avec succès.")
    except Exception as e:
        print(f"Erreur de synchronisation : {e}")

# Événement pour gérer les messages et l'XP
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)

    # Ajouter de l'XP
    if user_id not in user_xp_data:
        user_xp_data[user_id] = {"xp": 0, "level": 1}

    gain = random.randint(5, 10)
    user_xp_data[user_id]["xp"] += gain
    xp = user_xp_data[user_id]["xp"]
    level = user_xp_data[user_id]["level"]
    next_level_xp = level * 100

    if xp >= next_level_xp:
        user_xp_data[user_id]["level"] += 1
        await message.channel.send(f"🎉 {message.author.mention} a atteint le niveau {level + 1} !")

# Lancer le bot
client.run(TOKEN)

