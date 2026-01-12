import random
import polycours
from datetime import datetime
import discord
import asyncio

# Discord Bot Setup, avoir invité le bot au serveur avec https://discord.com/oauth2/authorize?client_id=1318745658936791131&permissions=2048&integration_type=0&scope=bot
DISCORD_BOT_TOKEN = ""  # Jeton bot pour PolyCours#4894
CHANNEL_ID = int()       # Remplacer avec le ID de la conversation. (Click droit sur le nom de la convo et "Copy Channel ID")
LOG_CHANNEL_ID = int()
USER_ID_TO_PING = int()   # Remplacer avec le ID du discord pour un ping. (Click droit sur le nom du compte et "Copy User ID")
DOSSIER_USER = ""
DOSSIER_PASS = ""
BIRTH = "" # Format concatenation: 'annee+mois+jour'
COURSES = [""] # Liste de cours a rechercher. Format [sigle(INF2610) + groupe(01,02,...) + type(T = théorie, L = labo)]. Si le cours affiche -1 place disponible, mauvais sigle.

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_discord_message(message, channel_id):
    channel = client.get_channel(channel_id)
    if channel:
        await channel.send(message)

async def main():
    # Pour l'envoie d'une notification par api. Garder "" si non applicable. Modifier la fonction sendApiNotice() si nécessaire
    api_url = ""

    # Fréquence de ressaie en seconde
    frequency = 1

    # Nombre essaie, -1 pour une boucle infini
    nombreEssaie = 1955

    # autoInscription = False (À implémenter... si très demandé)

    sessionToken = None

    while True and COURSES:
        try:
            if not sessionToken:
                sessionToken = polycours.getSessionId(DOSSIER_USER, DOSSIER_PASS, BIRTH)
            nombreEssaie += 1
            classes = polycours.find_class(sessionToken)
            for cours in COURSES:
                try:
                    nbPlaces = polycours.getNbPlaceDisponible(classes, cours)
                    print(f"{cours} a {nbPlaces} place disponible")
                    await send_discord_message(f"{cours} a {nbPlaces} place disponible", LOG_CHANNEL_ID)
                    if nbPlaces > 0:
                        c_datetime = datetime.now().strftime("%I:%M:%S %p")
                        if(cours[9] == "T"):
                            message = f"🎉 Le cours {cours[0:7]} groupe {cours[8:9]} section Théorie a {nbPlaces} place(s) disponible. {c_datetime}"
                        else:
                            message = f"🎉 Le cours {cours[0:7]} groupe {cours[8:9]} section Labo a {nbPlaces} place(s) disponible. {c_datetime}"
                        polycours.sendApiNotice(cours, nbPlaces, api_url, c_datetime)
                        if USER_ID_TO_PING:
                            message = f"<@{USER_ID_TO_PING}> {message}"
                        await send_discord_message(message, CHANNEL_ID)
                        COURSES.remove(cours)
                except:
                    sessionToken = None
                    print("Erreur de jeton, retentative de connection")
                    break
            print(f"Requete #{nombreEssaie}")
            if not sessionToken:
                frequency = 1
            else:
                frequency = random.randint(10, 30)
            print(f"Recommence dans {frequency} secondes")
            await send_discord_message(f"Requete #{nombreEssaie}", LOG_CHANNEL_ID)
            await asyncio.sleep(frequency)
        except:
            sessionToken = None
    print("Aucun cours restant")
    await client.close()

@client.event
async def on_ready():
    print(f"Bot connecté comme {client.user}")
    await main()

client.run(DISCORD_BOT_TOKEN)

main()