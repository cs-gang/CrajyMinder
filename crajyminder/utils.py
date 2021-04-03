import os
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, List

from async_oauthlib import OAuth2Session
import dotenv
from jinja2 import Environment
import requests
from sanic import Sanic
from sanic.request import Request

dotenv.load_dotenv(dotenv.find_dotenv())


CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8000/discord/callback")

API_BASE_URL = "https://discord.com/api"
TOKEN_URL = API_BASE_URL + "/oauth2/token"

CRAJY_API_URL = os.environ.get("CRAJY_URL")
CRAJY_API_TOKEN = os.environ.get("API_TOKEN")


@dataclass
class DiscordUser:
    """Dataclass representing a User object sent by the Discord API."""

    id: int
    name: str
    discriminator: str
    avatar: str
    flags: int
    premium_type: int
    public_flags: int

    @classmethod
    async def from_discord(cls, app: Sanic, request: Request) -> "DiscordUser":
        """
        Fetches the user's data from the Discord API.

        Arguments ::
            app: Sanic -> The currently running Sanic instance. This is the first argument to any
            method in this class that does an API request.
            request: Request -> The sanic.request.Request instance.
        """
        token = request.ctx.session.get("oauth2_token")
        token = {"Authorization": f"Bearer {token['access_token']}"}
        get = partial(requests.get, headers=token)
        response = await app.loop.run_in_executor(
            None, get, API_BASE_URL + "/users/@me"
        )
        return cls(**response.json())

    @property
    def avatar_url(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"

    async def fetch_notes(self, app: Sanic) -> List[dict]:
        """
        Fetches a `user`s notes from the Crajy database.

        Arguments ::
            app: Sanic -> The currently running Sanic instance. This is the first argument to any
            method in this class that does an API request.
        Returns ::
            List[dict]
        """
        get = partial(
            requests.get,
            json={"token": CRAJY_API_TOKEN},
            headers={"user": str(self.id)},
        )
        response = await app.loop.run_in_executor(None, get, CRAJY_API_URL + "/notes")
        json = response.json()
        return list(json.values())

    async def fetch_reminders(self, app: Sanic) -> List[dict]:
        """
        Fetches a `user`s reminders from the Crajy database.

        Arguments ::
            app: Sanic -> The currently running Sanic instance. This is the first argument to any
            method in this class that does an API request.
        Returns ::
            List[dict]
        """
        # TODO: Fix this after fixing API endpoint.
        raise NotImplementedError

        get = partial(
            requests.get,
            json={"token": CRAJY_API_TOKEN},
            headers={"user": str(self.id)},
        )
        response = await app.loop.run_in_executor(
            None, get, CRAJY_API_URL + "/reminders"
        )
        json = response.json()
        return list(json.values())


async def render_page(environment: Environment, *, file: str, **context: Any) -> str:
    """Helper function to render the template.
    Use to give final output in the route functions."""
    template = environment.get_template(file)
    return await template.render_async(**context)


def make_session(
    *, token: dict = None, state: dict = None, token_updater: Callable = None
) -> OAuth2Session:
    """
    Makes an `async_oauthlib.OAuth2Session` session with the arguments that are passed in.
    All arguments are keyword-only and optional.

    Arguments ::
        token: dict -> the OAuth2 token for a session.
        state: dict -> OAuth2 state.
        token_updater -> Callable
            This should be a function that takes a single argument - a new `token`.
    Returns ::
        async_oauthlib.OAuth2Session
    """
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
