import asyncio
import os
import signal
import smtplib
from datetime import datetime
from email.message import EmailMessage

import discord
from dotenv import load_dotenv

from . import polycours
from .logging_config import configure_logging, logger

# Load environment variables from .env file
load_dotenv()

# Configure logging
configure_logging()


def require_env(name):
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def require_int_env(name, *, optional=False):
    value = os.getenv(name)
    if value is None or value == "":
        if optional:
            return 0
        raise RuntimeError(f"Missing environment variable: {name}")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise RuntimeError(
            f"Invalid environment variable: {name}={value!r}. It must be an integer."
        ) from None


def get_int_env(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        raise RuntimeError(
            f"Invalid environment variable: {name}={value!r}. It must be an integer."
        ) from None


def require_course_list(name):
    raw_value = require_env(name)
    courses = [course.strip() for course in raw_value.split(",") if course.strip()]
    if not courses:
        raise RuntimeError(
            f"Invalid environment variable: {name}. No values were provided."
        )
    return courses


def require_bool_env(name, *, default=False):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise RuntimeError(
        f"Invalid environment variable: {name}={value!r}. It must be a boolean."
    )


NORMAL_RETRY_SECONDS = get_int_env("COURSE_POLLING_SECONDS", 10)
if NORMAL_RETRY_SECONDS <= 0:
    raise RuntimeError("COURSE_POLLING_SECONDS must be greater than 0")
SESSION_RETRY_SECONDS = get_int_env("SESSION_RETRY_SECONDS", 3)
if SESSION_RETRY_SECONDS <= 0:
    raise RuntimeError("SESSION_RETRY_SECONDS must be greater than 0")

USE_EMAIL = require_bool_env("USE_EMAIL", default=False)
if USE_EMAIL:
    SENDER_EMAIL = require_env("SENDER_EMAIL")
    SENDER_PASSWORD = require_env("SENDER_PASSWORD")
    RECIPIENT_EMAIL = require_env("RECIPIENT_EMAIL")
    DISCORD_BOT_TOKEN = None
    CHANNEL_ID = None
    LOG_CHANNEL_ID = None
    USER_ID_TO_PING = None
else:
    # Discord Bot Setup, avoir invité le bot au serveur avec https://discord.com/oauth2/authorize?client_id=1318745658936791131&permissions=2048&integration_type=0&scope=bot
    DISCORD_BOT_TOKEN = require_env("DISCORD_BOT_TOKEN")
    CHANNEL_ID = require_int_env(
        "CHANNEL_ID"
    )  # Remplacer avec le ID de la conversation. (Click droit sur le nom de la convo et "Copy Channel ID")
    LOG_CHANNEL_ID = require_int_env(
        "LOG_CHANNEL_ID", optional=True
    )  # Remplacer avec le ID de la conversation pour les logs. (Click droit sur le nom de la convo et "Copy Channel ID")
    USER_ID_TO_PING = require_int_env(
        "USER_ID_TO_PING"
    )  # Remplacer avec le ID du discord pour un ping. (Click droit sur le nom du compte et "Copy User ID")
    SENDER_EMAIL = SENDER_PASSWORD = RECIPIENT_EMAIL = None

logger.info("📣 Notification method selected: %s", "email" if USE_EMAIL else "Discord")

DOSSIER_USER = require_env("DOSSIER_USER")
DOSSIER_PASS = require_env("DOSSIER_PASS")
BIRTH = require_env("BIRTH")  # Format concaténé: 'année+mois+jour'
COURSES = require_course_list(
    "COURSES"
)  # Liste de cours à rechercher. Format [sigle(INF2610) + groupe(01,02,...) + type(T = théorie, L = labo)]. Si le cours affiche -1 place disponible, le sigle est probablement invalide.

if not USE_EMAIL:
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
else:
    client = None
shutdown_event = asyncio.Event()


async def send_discord_message(message, channel_id):
    channel = client.get_channel(channel_id)
    if channel:
        await channel.send(message)


def send_email_message(subject, body):
    if not USE_EMAIL:
        return
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
        raise RuntimeError(
            "Missing email variables: SENDER_EMAIL, SENDER_PASSWORD, or RECIPIENT_EMAIL"
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)

    logger.info(f"Email sent to {RECIPIENT_EMAIL}")


async def wait_for_shutdown_or_timeout(duration):
    try:
        await asyncio.wait_for(shutdown_event.wait(), timeout=duration)
        return True
    except asyncio.TimeoutError:
        return False
    except asyncio.CancelledError:
        shutdown_event.set()
        return True


async def main():
    # Pour l'envoie d'une notification par api. Garder "" si non applicable. Modifier la fonction sendApiNotice() si nécessaire
    api_url = ""

    # Fréquence de réessai en secondes
    frequency = 1

    # Nombre d'essais, -1 pour une boucle infinie
    nombreEssaie = -1

    # autoInscription = False (À implémenter... si très demandé)

    sessionToken = None
    retry_delay = NORMAL_RETRY_SECONDS

    while not shutdown_event.is_set() and COURSES:
        try:
            if not sessionToken:
                sessionToken = polycours.getSessionId(DOSSIER_USER, DOSSIER_PASS, BIRTH)
                retry_delay = 1
            nombreEssaie += 1
            classes = polycours.find_class(sessionToken)
            for cours in COURSES:
                try:
                    nbPlaces = polycours.getNbPlaceDisponible(classes, cours)
                    logger.info(f"{cours} has {nbPlaces} available seats")
                    if LOG_CHANNEL_ID:
                        await send_discord_message(
                            f"{cours} a {nbPlaces} place disponible", LOG_CHANNEL_ID
                        )
                    if nbPlaces > 0:
                        c_datetime = datetime.now().strftime("%I:%M:%S %p")
                        if cours[9] == "T":
                            message = f"🎉 Le cours {cours[0:7]} groupe {cours[8:9]} section Théorie a {nbPlaces} place(s) disponible. {c_datetime}\n⚠️ Ce cours ne sera plus suivi. Redémarrez le bot pour le surveiller à nouveau."
                        else:
                            message = f"🎉 Le cours {cours[0:7]} groupe {cours[8:9]} section Labo a {nbPlaces} place(s) disponible. {c_datetime}\n⚠️ Ce cours ne sera plus suivi. Redémarrez le bot pour le surveiller à nouveau."
                        polycours.sendApiNotice(cours, nbPlaces, api_url, c_datetime)
                        if USE_EMAIL:
                            send_email_message(
                                f"Cours disponible : {cours[0:7]} groupe {cours[8:9]}",
                                message,
                            )
                        else:
                            if USER_ID_TO_PING:
                                message = f"<@{USER_ID_TO_PING}> {message}"
                            await send_discord_message(message, CHANNEL_ID)
                        COURSES.remove(cours)
                except Exception:
                    sessionToken = None
                    retry_delay = SESSION_RETRY_SECONDS
                    logger.error(
                        "Session token error, retrying connection... Please wait a few seconds before restarting the bot if the problem persists."
                    )
                    break
            logger.info(f"Request #{nombreEssaie}")
            if not sessionToken:
                frequency = retry_delay
            else:
                frequency = NORMAL_RETRY_SECONDS
                retry_delay = 1
            logger.info(f"Retrying in {frequency} seconds")
            if LOG_CHANNEL_ID:
                await send_discord_message(f"Requête #{nombreEssaie}", LOG_CHANNEL_ID)
            if await wait_for_shutdown_or_timeout(frequency):
                logger.info("Shutdown requested by user, closing bot.")
                break
        except Exception as e:
            logger.error(f"Error while checking availability: {e}")
            sessionToken = None
            if shutdown_event.is_set():
                logger.info("Shutdown requested by user, closing bot.")
                break
            logger.info(f"Retrying in {retry_delay} seconds")
            if await wait_for_shutdown_or_timeout(retry_delay):
                logger.info("Shutdown requested by user, closing bot.")
                break
    if not COURSES and not shutdown_event.is_set():
        final_message = "✅ Aucun cours restant à surveiller. La vérification est terminée. Veuillez redémarrer le bot si vous souhaitez surveiller d'autres cours."
        if USE_EMAIL:
            send_email_message("Fin de la surveillance", final_message)
        else:
            if USER_ID_TO_PING:
                final_message = f"<@{USER_ID_TO_PING}> {final_message}"
            await send_discord_message(final_message, CHANNEL_ID)
        logger.info("Aucun cours restant")
    if client is not None:
        await client.close()


if not USE_EMAIL:

    @client.event
    async def on_ready():
        logger.info(f"Bot connecté comme {client.user}")
        await main()


async def graceful_shutdown():
    """Gracefully shutdown the bot"""
    shutdown_event.set()
    if client is not None:
        await client.close()


def handle_signal(sig, frame):
    """Handle SIGINT and SIGTERM signals"""
    logger.info("Signal received, shutting down the bot...")
    shutdown_event.set()
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(graceful_shutdown())
    except RuntimeError:
        pass


if not USE_EMAIL:
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    client.run(DISCORD_BOT_TOKEN)
else:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        shutdown_event.set()
        logger.info("Shutdown requested by user, closing bot.")
