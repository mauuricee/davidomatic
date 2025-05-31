# bot.py
import os # Librairie

import random
import pymongo
import string

import discord # Importation de la librairie Discord
from discord import app_commands

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILDE = os.getenv("GUILDE")
MONGO_URL = os.getenv("MONGO-URL", "mongodb://localhost:27017")

botIntents = discord.Intents.default() # Intents = donnees requises pour le bot
botIntents.message_content = True

client = discord.Client(intents=botIntents) # Creer le bot
tree = app_commands.CommandTree(client) # Arbre des commandes

clientMongo = pymongo.MongoClient(MONGO_URL)

dbMongo = clientMongo["davidomatic"] # Recuperer la BDD davidomatic

collGroupes = dbMongo["groupes"] # Recuperer la collection groupes
collEtudiants = dbMongo["etudiants"]
collNiveaux = dbMongo["niveaux"]


@tree.command(
    name="creer-groupe",
    description="Commande pour creer un groupe dans la base de donnees",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    groupe="Le nom du groupe a creer"
)
async def creategroup_command(interaction, groupe: str):
    groupeTrigger = collGroupes.find_one({"nomGroupe": groupe.lower().strip()}) # Requete pour trouver le groupe dans la BDD
    if groupeTrigger: # Si le groupe existe deja
        return await interaction.response.send_message(f"⚠️ Le groupe **{groupe}** existe deja !", ephemeral = True)
    nouvelleDonnee = { # Array contenant le nom du groupe ainsi que le groupe en minuscules (pour eviter la casse)
        "nomGroupe" : groupe.lower().strip()
    }
    try: # Sinon try catch pour l'ajouter dans la BDD
        collGroupes.insert_one(nouvelleDonnee)  # Inserer une donnee
        return await interaction.response.send_message(f"✅ Le groupe **{groupe}** a ete ajoute avec succes !", ephemeral = True)
    except Exception as e:
        return await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral = True)


@tree.command(
    name="reset-all",
    description="Commande pour reinitialiser toutes les commandes du bot",
    guild=discord.Object(id=GUILDE)
)
@app_commands.describe(
    confirmation="Ecrire 'confirmer' pour confirmer l'action"
)
async def reset_all_command(interaction, confirmation: str):
    if confirmation.strip().lower() != 'confirmer' or not confirmation:
        return await interaction.response.send_message("❌ Veuillez valider l'action en ecrivant 'confirmer' dans l'argument de la commande !", ephemeral = True)
    else:
        try:
            collEtudiants.delete_many({})
            collGroupes.delete_many({})
            collNiveaux.delete_many({})
            return await interaction.response.send_message("🗑️ Toutes les donnees de la base de donnees ont ete reinitialisees avec succes", ephemeral = True)
        except Exception as e:
            print(e)

    

@tree.command(
    name="level",
    description="Affiche ton niveau et ton XP",
    guild=discord.Object(id=GUILDE)
)
async def level_command(interaction):
    user_id = str(interaction.user.id)
    data = collNiveaux.find_one({"userID": user_id})
    if not data:
        return await interaction.response.send_message("⚠️ Aucune donnee sur toi n'a ete trouvee. Cela peut etre du au fait que tu n'as envoye aucun message.", ephemeral = True)
    else:
        level = data["level"]
        xp = data["experience"]
        next_xp = level * 100
        return await interaction.response.send_message(
            f"📊 {interaction.user.mention}, tu es au **niveau {level}** avec **{xp} XP**. Prochain niveau à **{next_xp} XP**.",
            ephemeral = True
        )


@tree.command(
    name="supprimer-groupe",
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
        return await interaction.response.send_message(f"⚠️ Le groupe **{groupe}** n'existe pas ou plus.", ephemeral = True)
    elif etudiantTrigger:
        return await interaction.response.send_message(f"⚠️ Le groupe **{groupe}** n'est pas vide. Veuillez le vider avant de continuer.", ephemeral = True)
    else:
        collGroupes.delete_one({"nomGroupe": groupe.lower().strip()})
        return await interaction.response.send_message(f"✅ Le groupe **{groupe}** a ete supprime avec succes.", ephemeral = True)


@tree.command(
    name="supprimer-etudiant",
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
        return await interaction.response.send_message(f"⚠️ L'etudiant avec le nom / ID **{argument}** n'a pas ete trouve dans la base de donnees.", ephemeral = True)
    else:
        try:
            collEtudiants.delete_one({"$or": [{"nomEtudiant": argument.lower()}, {"idEtudiant": argument.upper()} ] } )
            return await interaction.response.send_message(f"🗑️ L'etudiant **{etudiantTrigger["nomEtudiant"]}** a ete supprime de la base de donnees avec succes !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"❌ Une erreur est survenue lors de la suppression : {e}", ephemeral = True)


@tree.command(
    name="vider-groupe",
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
        return await interaction.response.send_message("⚠️ L'action n'a pas pu etre confirmee. Verifiez que vous avez rentre correctement le nom du groupe 2 fois.", ephemeral = True)
    elif not groupeTrigger:
        return await interaction.response.send_message(f"⚠️ Le groupe **{argumentGroupe}** n'existe pas.", ephemeral = True)
    else:
        try:
            collEtudiants.delete_many({"groupeEtudiant": argumentGroupe})
            return await interaction.response.send_message(f"🗑️ Le groupe **{argumentGroupe}** a ete vide avec succes !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral = True)



@tree.command(
    name="afficher-groupe",
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
        return await interaction.response.send_message(f"⚠️ Le groupe **{argumentGroupe}** n'existe pas.")
    elif not etudiantsTrigger:
        return await interaction.response.send_message(f"⚠️ Le groupe **{argumentGroupe}** ne contient aucun etudiant.")
    else:
        etudiantsData = collEtudiants.find({"groupeEtudiant": argumentGroupe})
        listeString = ""
        for etudiant in etudiantsData:
            listeString += f"*({etudiant["idEtudiant"]})* {etudiant["nomEtudiant"]}" + "\n"
        
        if len(listeString) >= 4096:
            fichierTexte = open("liste.txt", "a")
            fichierTexte.write(listeString)
            await interaction.response.send_message(f"ℹ️ La liste etant trop longue pour Discord, celle-ci a ete mise dans un fichier texte joint a ce message", ephemeral = True, file = discord.File("liste.txt"))
            return os.remove("liste.txt")
        else:
            listeEmbed = discord.Embed(title = f"Etudiants dans le groupe {groupe}", description = listeString, color=0xff8040)
            listeEmbed.set_footer(text="ℹ️ Les donnees sont affichees sont la forme (ID) nom")
            return await interaction.response.send_message(embed = listeEmbed, ephemeral = True)


@tree.command(
    name="lister-groupes",
    description="Commande pour lister les groupes",
    guild=discord.Object(id=GUILDE)
)
async def listGroups_command(interaction):
    groupesTrigger = collGroupes.count_documents({})
    if not groupesTrigger:
        return await interaction.response.send_message("⚠️ Il n'y a aucun groupe enregistre dans la base de donnees", ephemeral = True)
    else:
        groupesData = collGroupes.find({})
        groupesNames = []
        for groupe in groupesData:
            nombreMembres = collEtudiants.count_documents({"groupeEtudiant": groupe["nomGroupe"]})
            groupesNames.append(f"**{groupe["nomGroupe"]}** - ({nombreMembres} etudiants)")
        stringData = "\n".join(groupesNames)
        listeEmbed = discord.Embed(title = "Liste des groupes enregistres dans la base de donnees", description = stringData, color = 0xff7e40)
        return await interaction.response.send_message(embed = listeEmbed, ephemeral = True)

@tree.command(
    name="ajouter-etudiant",
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
        return await interaction.response.send_message(f"⚠️ L'etudiant **{nom}** existe deja dans le groupe !", ephemeral = True)
    elif not groupeTrigger:
        return await interaction.response.send_message(f"❌ Le groupe **{groupe}** n'existe pas.", ephemeral = True)
    else:
        nouvelleDonnee = {
            "idEtudiant": ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
            "groupeEtudiant": groupe.lower().strip(),
            "nomEtudiant": nom.lower().strip()
        }
        try:
            collEtudiants.insert_one(nouvelleDonnee)
            return await interaction.response.send_message(f"✅ L'etudiant **{nom}** membre du groupe **{groupe}** a ete ajoute a la base de donnees avec succes !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"❌ Une erreur est survenue avec la commande : {e}", ephemeral = True)


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
    groupeTrigger = collGroupes.find_one({"nomGroupe": argumentGroupe})
    etudiantsTrigger = collEtudiants.count_documents({ "groupeEtudiant": argumentGroupe })
    if not groupeTrigger:
        return await interaction.response.send_message(f"❌ Le groupe **{argumentGroupe}** n'existe pas.", ephemeral = True)
    elif not etudiantsTrigger:
        return await interaction.response.send_message(f"⚠️ Le groupe **{argumentGroupe}** ne contient pas d'etudiants.", ephemeral = True)
    elif etudiantsTrigger < nombre:
        return await interaction.response.send_message(f"⚠️ Il n'y a pas assez d'etudiants dans le groupe **{argumentGroupe}** pour former des groupes de **{nombre}** personnes", ephemeral = True)
    else:
        etudiantsData = collEtudiants.find({"groupeEtudiant": argumentGroupe})
        groupeEtudiantsNoms = []
        for etudiant in etudiantsData:
            groupeEtudiantsNoms.append(etudiant["nomEtudiant"])
        
        groupe_melange = random.sample(groupeEtudiantsNoms, len(groupeEtudiantsNoms))

        groupesEmbed=discord.Embed(title=f"Groupes de travail de {nombre} personnes du groupe {argumentGroupe}", color=0xff8040)

        sous_groupes = []

        for i in range(0, len(groupe_melange), nombre):
            sous_groupes.append(groupe_melange[i:i + nombre])

        numeroGroupe = 0

        for groupe in sous_groupes:
            numeroGroupe += 1
            listeGroupeString = ", ".join(groupe)
            groupesEmbed.add_field(name=f"Groupe {numeroGroupe}", value = listeGroupeString, inline=False)

        return await interaction.response.send_message(embed = groupesEmbed, ephemeral = True)



@tree.command(
    name="renommer-groupe",
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
        return await interaction.response.send_message(f"❌ Le groupe **{groupe}** n'existe pas.", ephemeral = True)
    elif groupe.lower().strip() == nouveaunom.lower().strip():
        return await interaction.response.send_message("❌ Le nouveau et l'ancien nom **ne peuvent pas etre les memes** !", ephemeral = True)
    elif nameTrigger:
        return await interaction.response.send_message(f"⚠️ Un groupe ayant le nom **{nouveaunom}** existe deja !")
    else:
        nouvelleDonnee = { "$set": { "nomGroupe": nouveaunom.lower().strip() } }
        try:
            collGroupes.update_one({"nomGroupe": groupe.lower().strip()}, nouvelleDonnee)
            membresExistants = collEtudiants.find({"groupeEtudiant": groupe.lower().strip()})
            for etudiant in membresExistants:
                collEtudiants.update_one({"idEtudiant": etudiant["idEtudiant"]}, { "$set": {"groupeEtudiant": nouveaunom.lower().strip()} } )
            return await interaction.response.send_message(f"✅ Le groupe **{groupe}** a ete renomme en **{nouveaunom}** avec succes et les etudiants de ce groupe ont ete mis a jour !", ephemeral = True)
        except Exception as e:
            return await interaction.response.send_message(f"❌ Une erreur est survenue : {e}")


@tree.command(
    name="8ball",
    description="Pose une question, et reçois une réponse magique ",
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

    if "DAVID" in contenu:
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
        user_id = str(message.author.id)

        gain = random.randint(5, 10)
        
        niveauxTrigger = collNiveaux.find_one({"userID": user_id})

        if not niveauxTrigger:
            nouvelleDonnee = {
                "userID": user_id,
                "experience": gain,
                "level": 1
            }
            try:
                collNiveaux.insert_one(nouvelleDonnee)
            except Exception as e:
                print(e)

        else:
            userXP = niveauxTrigger["experience"]
            userLevel = niveauxTrigger["level"]
            
            userXP += gain
            userNextLevel = userLevel * 100

            if userXP >= userNextLevel:
                userLevel += 1
                await message.reply(f"🎉 Felicitations {message.author.mention} ! Tu as atteint le niveau **{userLevel}** !")

            donneeAJour = {
                "experience": userXP,
                "level": userLevel
            }

            try:
                collNiveaux.update_one({"userID": user_id}, { "$set": donneeAJour })
            except Exception as e:
                print(e)

            return
        
        


client.run(TOKEN)
