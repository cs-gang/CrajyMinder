import os
from functools import partial

from dotenv import find_dotenv, load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse, redirect
from sanic_session import Session, InMemorySessionInterface

from crajyminder.utils import DiscordUser, render_page, make_session

load_dotenv(find_dotenv())

API_BASE_URL = "https://discordapp.com/api"
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

app = Sanic("CrajyMinder")
env = Environment(
    loader=PackageLoader("crajyminder", "templates"),
    autoescape=select_autoescape(["html"]),
    enable_async=True,
)
session = Session(app, interface=InMemorySessionInterface())

app.static("/static", "./crajyminder/static")


def token_updater(request: Request, token: dict) -> None:
    # updates the token in the session
    request.ctx.session["oauth2_token"] = token


# Routes
@app.route("/", methods=["GET"])
async def index(request: Request) -> HTTPResponse:
    output = await render_page(env, file="index.html")
    return HTTPResponse(output, content_type="text/html")


@app.route("/discord", methods=["GET"])
async def discord_login(request: Request) -> HTTPResponse:
    discord = make_session(token_updater=partial(token_updater, request))
    url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    request.ctx.session["oauth2_state"] = state
    return redirect(url)


@app.route("/discord/callback")
async def discord_login_callback(request: Request) -> HTTPResponse:
    # after user has logged in with discord, this route will be used to redirect back to our site
    if request.args.get("error"):
        return request.args.get("error")

    discord = make_session(
        state=request.ctx.session.get("oauth2_state"),
        token_updater=partial(token_updater, request),
    )
    token = await discord.fetch_token(
        TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url
    )
    request.ctx.session["oauth2_token"] = token
    url = app.url_for("index")
    print(url)
    return redirect(url)


@app.route("/notes", methods=["GET", "POST"])
async def notes(request: Request) -> HTTPResponse:
    # TODO: Finish this
    raise NotImplementedError

    token = request.ctx.session.get("oauth2_token")

    if not token:
        return HTTPResponse(status=403, body="You're not signed in.")

    user = await DiscordUser.from_discord(app, request)
    notes = await user.fetch_notes(app)
    reminders = await user.fetch_reminders(app)

    output = await render_page(
        env,
        file="notes.html",
        username=user.name,
        avatar_url=user.avatar_url,
        notes=notes,
        reminders=reminders,
    )
    return HTTPResponse(output, content_type="text/html")
