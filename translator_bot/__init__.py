from os import environ
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"),
              logging.StreamHandler()],
    level=logging.DEBUG,
)

LOGGER = logging.getLogger(__name__)

TOKEN: str = environ.get("TOKEN", "None")
HEROKU: str = environ.get("HEROKU", "None")
if HEROKU != "None":
    HEROKU = f"https://{HEROKU}.herokuapp.com/"
    LOGGER.debug(f"HEROKU: {HEROKU}")
PORT: int = int(environ.get('PORT', 5000))
DB_URI: str = environ.get("DATABASE_URL", "None")
if DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)
