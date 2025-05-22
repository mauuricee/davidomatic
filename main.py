# bot.py
import os # Librairie

import random
import pymongo

import discord # Importation de la librairie Discord
from discord import app_commands
from dotenv import load_dotenv # Librairie Dotenv pour les infos d'environnement

collection_groupes = {

}

load_dotenv() # Recuperation des donnees du fichier dotenv
TOKEN = os.getenv('TOKEN')
GUILDE = os.getenv("GUILDE")
MDP_MONGO = os.getenv("MONGO-DB-PASS")

botIntents = discord.Intents.default() # Intents = donnees requises pour le bot
botIntents.message_content = True

client = discord.Client(intents=botIntents) # Creer le bot
tree = app_commands.CommandTree(client) # Arbre des commandes

clientMongo = pymongo.MongoClient(f"mongodb+srv://davidomatic:{MDP_MONGO}@cluster-ccnb.rn6e0ob.mongodb.net/?retryWrites=true&w=majority&appName=cluster-ccnb")

dbMongo = clientMongo["davidomatic"] # Recuperer la BDD davidomatic

collGroupes = dbMongo["groupes"] # Recuperer la collection groupes
collEtudiants = dbMongo["etudiants"] # Recuperer la collection etudiants

@tree.command(
    name="creergroupe",
    description="Commande pour creer un groupe dans la base de donnees",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe a creer"
)
async def creategroup_command(interaction, groupe: str):
    groupeTrigger = collGroupes.find_one({"nomGroupe": f"{groupe.lower()}"}) # Requete pour trouver le groupe dans la BDD
    if groupeTrigger: # Si le groupe existe deja
        return await interaction.response.send_message(f"Le groupe **{groupe}** existe deja !", ephemeral = True)
    nouvelleDonnee = { # Array contenant le nom du groupe ainsi que le groupe en minuscules (pour eviter la casse)
        "nomGroupe" : groupe.lower()
    }
    try: # Sinon try catch pour l'ajouter dans la BDD
        collGroupes.insert_one(nouvelleDonnee)  # Inserer une donnee
        return await interaction.response.send_message(f"Le groupe **{groupe}** a ete ajoute avec succes !", ephemeral = True)
    except Exception as e:
        return await interaction.response.send_message(f"Une erreur est survenue : {e}", ephemeral = True)


@tree.command(
    name="supprimergroupe",
    description="Commande pour supprimer un groupe dans la base de donnees",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe a supprimer"
)
async def removegroup_command(interaction, groupe: str):
    print("test")
    

@client.event
async def on_ready():
    print(f"{client.user} s'est connecte avec succes")
    try:
        await tree.sync(guild=discord.Object(id=GUILDE))
        print("Commandes synchronisees avec succes")
        clientMongo.davidomatic.command('ping')
        print("Connexion a la base de donnees etablie avec succes")
    except Exception as e:
        print(e)
        
    

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
