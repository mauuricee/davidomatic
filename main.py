# bot.py
import os # Librairie

import random
import pymongo
import string

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
collEtudiants = dbMongo["etudiants"]


@tree.command(
    name="creergroupe",
    description="Commande pour creer un groupe dans la base de donnees",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe a creer"
)
async def creategroup_command(interaction, groupe: str):
    groupeTrigger = collGroupes.find_one({"nomGroupe": groupe.lower().strip()}) # Requete pour trouver le groupe dans la BDD
    if groupeTrigger: # Si le groupe existe deja
        return await interaction.response.send_message(f"Le groupe **{groupe}** existe deja !", ephemeral = True)
    nouvelleDonnee = { # Array contenant le nom du groupe ainsi que le groupe en minuscules (pour eviter la casse)
        "nomGroupe" : groupe.lower().strip()
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
    groupeTrigger = collGroupes.find_one({"nomGroupe": groupe.lower().strip()})
    etudiantTrigger = collEtudiants.find({"groupeEtudiant": groupe.lower().strip()})
    if not groupeTrigger:
        return await interaction.response.send_message(f"Le groupe **{groupe}** n'existe pas ou plus.", ephemeral = True)
    elif etudiantTrigger:
        return await interaction.response.send_message(f"Le groupe **{groupe}** n'est pas vide. Veuillez le vider avant de continuer.", ephemeral = True)
    else:
        collGroupes.delete_one({"nomGroupe": groupe.lower().strip()})
        return await interaction.response.send_message(f"Le groupe **{groupe}** a ete supprime avec succes.", ephemeral = True)


@tree.command(
    name="supprimeretudiant",
    description="Commande pour supprimer un etudiant dans la base de donnees",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    etudiant="Le nom / ID de l'etudiant a supprimer"
)
async def removestudent_command(interaction, etudiant: str):
    argument = etudiant.strip()
    etudiantTrigger = collEtudiants.find_one({"$or": [{"nomEtudiant": argument.lower()}, {"idEtudiant": argument.upper()} ] } )
    if not etudiantTrigger:
        return await interaction.response.send_message(f"L'etudiant avec le nom / ID **{argument}** n'a pas ete trouve dans la base de donnees.", ephemeral = True)
    else:
        try:
            collEtudiants.delete_one({"$or": [{"nomEtudiant": argument.lower()}, {"idEtudiant": argument.upper()} ] } )
            return await interaction.response.send_message(f"L'etudiant **{etudiantTrigger["nomEtudiant"]}** a ete supprime de la base de donnees avec succes !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"Une erreur est survenue lors de la suppression : {e}", ephemeral = True)


@tree.command(
    name="vidergroupe",
    description="Commande pour vider un groupe de tous ses membres",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe a vider",
    confirmation="Ecrire le nom du groupe a nouveau pour confirmer l'action"
)
async def cleanGroup_command(interaction, groupe: str, confirmation: str):
    argumentGroupe = groupe.strip().lower()
    argumentConfirmation = confirmation.strip().lower()
    groupeTrigger = collGroupes.find_one({"nomGroupe": groupe.lower().strip()})
    if argumentGroupe != argumentConfirmation:
        return await interaction.response.send_message("L'action n'a pas pu etre confirmee. Verifiez que vous avez rentre correctement le nom du groupe 2 fois.", ephemeral = True)
    elif not groupeTrigger:
        return await interaction.response.send_message(f"Le groupe **{argumentGroupe}** n'existe pas.", ephemeral = True)
    else:
        try:
            collEtudiants.delete_many({"groupeEtudiant": argumentGroupe})
            return await interaction.response.send_message(f"Le groupe **{argumentGroupe}** a ete vide avec succes !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"Une erreur est survenue : {e}", ephemeral = True)



@tree.command(
    name="affichergroupe",
    description="Commande pour lister les etudiants d'un groupe",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Groupe dont on doit afficher la liste"
)
async def showGroup_command(interaction, groupe: str):
    argumentGroupe = groupe.lower().strip()
    groupeTrigger = collGroupes.find_one({"nomGroupe": argumentGroupe})
    etudiantsTrigger = collEtudiants.count_documents({"groupeEtudiant": argumentGroupe})
    if not groupeTrigger:
        return await interaction.response.send_message(f"Le groupe **{argumentGroupe}** n'existe pas.")
    elif not etudiantsTrigger:
        return await interaction.response.send_message(f"Le groupe **{argumentGroupe}** ne contient aucun etudiant.")
    else:
        etudiantsData = collEtudiants.find({"groupeEtudiant": argumentGroupe})
        listeString = ""
        for etudiant in etudiantsData:
            listeString += f"*({etudiant["idEtudiant"]})* {etudiant["nomEtudiant"]}" + "\n"
        
        if len(listeString) >= 4096:
            fichierTexte = open("liste.txt", "a")
            fichierTexte.write(listeString)
            await interaction.response.send_message(f"La liste etant trop longue pour Discord, celle-ci a ete mise dans un fichier texte joint a ce message", ephemeral = True, file = discord.File("liste.txt"))
            return os.remove("liste.txt")
        else:
            listeEmbed = discord.Embed(title = f"Etudiants dans le groupe {groupe}", description = listeString, color=0xff8040)
            listeEmbed.set_footer(text="Les donnees sont affichees sont la forme (ID) nom")
            return await interaction.response.send_message(embed = listeEmbed, ephemeral = True)



@tree.command(
    name="ajouteretudiant",
    description="Commande pour ajouter un etudiant a la base de donnees",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Nom du groupe dans lequel est membre l'etudiant",
    nom="Nom de l'etudiant"
)
async def addUserToGroup_command(interaction, groupe: str, nom: str):
    groupeTrigger = collGroupes.find_one({"nomGroupe": groupe.lower().strip()})
    etudiantTrigger = collEtudiants.find_one({"nomEtudiant": nom.lower().strip()})
    if etudiantTrigger:
        return await interaction.response.send_message(f"L'etudiant **{nom}** existe deja dans le groupe !", ephemeral = True)
    if not groupeTrigger:
        return await interaction.response.send_message(f"Le groupe **{groupe}** n'existe pas.", ephemeral = True)
    else:
        nouvelleDonnee = {
            "idEtudiant": ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
            "groupeEtudiant": groupe.lower().strip(),
            "nomEtudiant": nom.lower().strip()
        }
        try:
            collEtudiants.insert_one(nouvelleDonnee)
            return await interaction.response.send_message(f"L'etudiant **{nom}** membre du groupe **{groupe}** a ete ajoute a la base de donnees avec succes !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"Une erreur est survenue avec la commande : {e}", ephemeral = True)

@tree.command(
    name="groupes",
    description="Commande pour creer des sous-groupes de X etudiants d'un groupe deja existant",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Nom du groupe",
    nombre="Nombre de membres par groupe"
)
async def createSubGroup_command(interaction, groupe: str, nombre: int):
    argumentGroupe = groupe.lower().strip()
    groupeTrigger = collGroupes.find_one({"nomGroupe": argumentGroupe.lower().strip()})
    etudiantsTrigger = collEtudiants.find({ "groupeEtudiant": argumentGroupe })
    if not groupeTrigger:
        return await interaction.response.send_message(f"Le groupe **{argumentGroupe}** n'existe pas.", ephemeral = True)
    elif not etudiantsTrigger:
        return await interaction.response.send_message(f"Le groupe **{argumentGroupe}** ne contient pas d'etudiants.", ephemeral = True)
    elif etudiantsTrigger.len() < nombre:
        return await interaction.response.send_message(f"Il n'y a pas assez d'etudiants dans le groupe **{argumentGroupe}** pour former des groupes de **{nombre}** personnes", ephemeral = True)
    else:
        nombreGroupesComplets = int(etudiantsTrigger.len() / nombre)
        personnesSansGroupes = etudiantsTrigger.len() % nombre
        groupeEtudiantsNoms = []
        for etudiant in etudiantsTrigger:
            groupeEtudiantsNoms.append(etudiant["nomEtudiant"])
        groupe_melange = random.sample(groupeEtudiantsNoms, len(groupeEtudiantsNoms))

        groupesEmbed=discord.Embed(title=f"Groupes de travail de {nombre} personnes du groupe {argumentGroupe}", color=0xff8040)

        sous_groupes = []

        for i in range(0, len(groupe_melange), nombre):
            sous_groupe = groupe_melange[i:i + nombre]
            fieldString = ""
            for eleve in sous_groupe:
                fieldString += eleve["nomEtudiant"] + ", "
            else:
                fieldString += eleve["nomEtudiant"]

            groupesEmbed.add_field(name=f"Groupe {i + 1}", value = fieldString, inline=True)

        return await interaction.response.send_message(embed = groupesEmbed, ephemeral = True)



@tree.command(
    name="renommergroupe",
    description="Commande pour renommer un groupe",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Nom du groupe a renommer",
    nouveaunom="Nouveau nom du groupe"
)
async def renameGroup_command(interaction, groupe: str, nouveaunom: str):
    groupeTrigger = collGroupes.find_one({"nomGroupe": groupe.lower().strip()})
    nameTrigger = collGroupes.find_one({"nomGroupe": nouveaunom.lower().strip()})
    if not groupeTrigger:
        return await interaction.response.send_message(f"Le groupe **{groupe}** n'existe pas.", ephemeral = True)
    elif groupe.lower().strip() == nouveaunom.lower().strip():
        return await interaction.response.send_message("Le nouveau et l'ancien nom **ne peuvent pas etre les memes** !", ephemeral = True)
    elif nameTrigger:
        return await interaction.response.send_message(f"Un groupe ayant le nom **{nouveaunom}** existe deja !")
    else:
        nouvelleDonnee = { "$set": { "nomGroupe": nouveaunom.lower().strip() } }
        try:
            collGroupes.update_one({"nomGroupe": groupe.lower().strip()}, nouvelleDonnee)
            membresExistants = collEtudiants.find({"groupeEtudiant": groupe.lower().strip()})
            for etudiant in membresExistants:
                collEtudiants.update_one({"idEtudiant": etudiant["idEtudiant"]}, { "$set": {"groupeEtudiant": nouveaunom.lower().strip()} } )
            return await interaction.response.send_message(f"Le groupe **{groupe}** a ete renomme en **{nouveaunom}** avec succes et les etudiants de ce groupe ont ete mis a jour !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"Une erreur est survenue : {e}")

@client.event
async def on_ready():
    print(f"{client.user} s'est connecte avec succes")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="David faire du cafe"))
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


    contenu = message.content.upper().strip() # Pour eviter le case-sensitive (tout mettre em CAPS)

    funfacts_david = [
        "David est le prof le plus sympa mine de rien",
        "David adore les aliens",
        "David est fan de Star Wars",
        "David ne sait pas se raser les cheveux tout seul",
        "David peut tres bien dessiner Marc-Andre",
    ]

    funfacts_joel = [
        "Joel parle tres vite, mais vraiment tres tres vite",
        "Joel porte toujours du Hollister",
    ]

    funfacts_paul = [
        "Personne ne sait pourquoi Paul nous a enseigne le cours de Access",
        "Paul enseigne le meilleur cours (d'apres Em)",
    ]

    funfacts_ghislain = [
        "Ghislain voit tout",
        "Ghislain VEUT les commentaires d'entete",
        "Ghislain vient des memes contrees lointaines que Marc-Andre",
        "Ghislain a choisi de vivre a Allardville (juste, pourquoi ????)",
    ]
    
    if "MOUNIR" in contenu:
        await message.reply("Mounir... Tu veux dire Maurice ? Ou alors Pierre !")

    elif "DAVID" in contenu:
        reponse = random.choice(funfacts_david)
        await message.reply(reponse)

    elif "JOEL" in contenu:
        reponse = random.choice(funfacts_joel)
        await message.reply(reponse)

    elif "PAUL" in contenu:
        reponse = random.choice(funfacts_paul)
        await message.reply(reponse)

    elif "GHISLAIN" in contenu:
        reponse = random.choice(funfacts_ghislain)
        await message.reply(reponse)

    else:
        return

client.run(TOKEN)