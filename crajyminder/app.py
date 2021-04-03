import asyncio
import os
from functools import partial

from dotenv import find_dotenv, load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse, redirect

from crajyminder.utils import render_page

load_dotenv(find_dotenv())

app = Sanic("CrajyMinder")
env = Environment(
    loader=PackageLoader("crajyminder", "templates"),
    autoescape=select_autoescape(["html"]),
    enable_async=True,
)

app.static("/static", "./crajyminder/static")


@app.route("/", methods=["GET"])
async def index(request: Request) -> HTTPResponse:
    output = await render_page(env, file="index.html")
    return HTTPResponse(output, content_type="text/html")
