import os
import random
import polycours
from datetime import datetime
import discord
import asyncio
import logging
import signal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Discord Bot Setup, avoir invité le bot au serveur avec https://discord.com/oauth2/authorize?client_id=1318745658936791131&permissions=2048&integration_type=0&scope=bot
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))       # Remplacer avec le ID de la conversation. (Click droit sur le nom de la convo et "Copy Channel ID")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID")) if os.getenv("LOG_CHANNEL_ID") else 0  # Remplacer avec le ID de la conversation pour les logs. (Click droit sur le nom de la convo et "Copy Channel ID")
USER_ID_TO_PING = int(os.getenv("USER_ID_TO_PING"))   # Remplacer avec le ID du discord pour un ping. (Click droit sur le nom du compte et "Copy User ID")
DOSSIER_USER = os.getenv("DOSSIER_USER")
DOSSIER_PASS = os.getenv("DOSSIER_PASS")
BIRTH = os.getenv("BIRTH") # Format concatenation: 'annee+mois+jour'
COURSES = os.getenv("COURSES", "INF840201T").split(",") # Liste de cours à rechercher. Format [sigle(INF2610) + groupe(01,02,...) + type(T = théorie, L = labo)]. Si le cours affiche -1 place disponible, mauvais sigle.

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
    nombreEssaie = -1

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
                    logger.info(f"{cours} a {nbPlaces} place disponible")
                    if LOG_CHANNEL_ID:
                        await send_discord_message(f"{cours} a {nbPlaces} place disponible", LOG_CHANNEL_ID)
                    if nbPlaces > 0:
                        c_datetime = datetime.now().strftime("%I:%M:%S %p")
                        if(cours[9] == "T"):
                            message = f"🎉 Le cours {cours[0:7]} groupe {cours[8:9]} section Théorie a {nbPlaces} place(s) disponible. {c_datetime}\n⚠️ Ce cours ne sera plus suivi. Redémarrez le bot pour le surveiller à nouveau."
                        else:
                            message = f"🎉 Le cours {cours[0:7]} groupe {cours[8:9]} section Labo a {nbPlaces} place(s) disponible. {c_datetime}\n⚠️ Ce cours ne sera plus suivi. Redémarrez le bot pour le surveiller à nouveau."
                        polycours.sendApiNotice(cours, nbPlaces, api_url, c_datetime)
                        if USER_ID_TO_PING:
                            message = f"<@{USER_ID_TO_PING}> {message}"
                        await send_discord_message(message, CHANNEL_ID)
                        COURSES.remove(cours)
                except Exception as e:
                    sessionToken = None
                    logger.error(f"Erreur de jeton, retentative de connection: {e}")
                    break
            logger.info(f"Requete #{nombreEssaie}")
            if not sessionToken:
                frequency = 1
            else:
                frequency = random.randint(10, 30)
            logger.info(f"Recommence dans {frequency} secondes")
            if LOG_CHANNEL_ID:
                await send_discord_message(f"Requete #{nombreEssaie}", LOG_CHANNEL_ID)
            await asyncio.sleep(frequency)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification: {e}")
            sessionToken = None
    logger.info("Aucun cours restant")
    await client.close()

@client.event
async def on_ready():
    logger.info(f"Bot connecté comme {client.user}")
    await main()

async def graceful_shutdown():
    """Gracefully shutdown the bot"""
    logger.info("Shutting down bot gracefully...")
    await client.close()

def handle_signal(sig, frame):
    """Handle SIGINT and SIGTERM signals"""
    logger.info("Received shutdown signal")
    asyncio.create_task(graceful_shutdown())

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

client.run(DISCORD_BOT_TOKEN)