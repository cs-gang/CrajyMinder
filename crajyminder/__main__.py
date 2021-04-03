import dotenv
import os

from crajyminder import app

dotenv.load_dotenv(dotenv.find_dotenv())


HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")

if PORT:
    PORT = int(PORT)

DEBUG = False if os.environ.get("DEBUG") else True

app.app.run(host=HOST, port=PORT, debug=DEBUG)
