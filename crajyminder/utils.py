import os
from typing import Any, Callable

from async_oauthlib import OAuth2Session
import dotenv
from jinja2 import Environment

dotenv.load_dotenv(dotenv.find_dotenv())


CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8000/discord/callback")

API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"


async def render_page(environment: Environment, *, file: str, **context: Any) -> str:
    """Helper function to render the template.
    Use to give final output in the route functions."""
    template = environment.get_template(file)
    return await template.render_async(**context)


def make_session(
    *, token: dict = None, state: dict = None, token_updater: Callable = None
) -> OAuth2Session:
    # token_updater should be a function which will update the token in the session
    return OAuth2Session(
        client_id=CLIENT_ID,
        token=token,
        state=state,
        redirect_uri=REDIRECT_URI,
        scope=["identify"],
        auto_refresh_kwargs={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        token_updater=token_updater,
        auto_refresh_url=TOKEN_URL,
    )
