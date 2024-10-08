"""Resources for generating Nexar tokens."""
import base64
import getpass
import hashlib
import http.server
import json
import os
import re
import webbrowser
from functools import wraps
from pathlib import Path
from typing import Sequence

import requests
from requests_oauthlib import OAuth2Session


from .localService import handlerFactory
from .errors import NexarClientUnauthenticatedError

HOST_NAME = "localhost"
PORT = 3000
REDIRECT_URI = f"http://{HOST_NAME}:{PORT}/login"
AUTHORITY_URL = "https://identity.nexar.com/connect/authorize"
PROD_TOKEN_URL = "https://identity.nexar.com/connect/token"
ALTIUM_CONFIG_DIR = (Path.home() / '.altium')


def store_token(enabled = True):
    def wrapped(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = f(*args, **kwargs)
            ALTIUM_CONFIG_DIR.mkdir(exist_ok = True, parents=True)
            if enabled:
                (ALTIUM_CONFIG_DIR / '.token.json').write_text(json.dumps(token))
            return token
        return wrapper
    return wrapped

@store_token(enabled=True)
def get_token(client_id: str, client_secret: str, scopes: Sequence[str] = [], refresh_token: str | None = None):
    """Return the Nexar token from the client_id and client_secret provided."""

    if refresh_token is None:
        try:
            refresh_token = json.loads(Path(ALTIUM_CONFIG_DIR / '.token.json').read_text())['refresh_token']
        except:
            pass

    if client_id is None:
        raise NexarClientUnauthenticatedError("'client_id' must be set")
    if client_secret is None:
        raise NexarClientUnauthenticatedError("'client_secret' must be set")
    if scopes is None:
        raise NexarClientUnauthenticatedError("'scope' must not be empty")

    if refresh_token:
        return get_refresh_token(client_id, client_secret, scopes, refresh_token)

    scopes = list(scopes)
    if (scopes != ["supply.domain"]):
        return get_token_with_login(client_id, client_secret, scopes)

    token = {}
    token_response = requests.post(
        url=PROD_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": " ".join(scopes)
        },
        allow_redirects=False,
    )
    token_response.raise_for_status()
    token = token_response.json()


    return token

def get_refresh_token(client_id: str, client_secret: str, scopes: Sequence[str], refresh_token: str | None):
    """Return the Nexar token from a refresh token."""

    token = {}
    token_response = requests.post(
        url=PROD_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": " ".join(scopes)
        },
    )

    token_response.raise_for_status()
    token = token_response.json()


    return token

def get_token_with_login(client_id, client_secret, scopes):
    """Open the Nexar authorization url from the client_id and scope provided."""

    token = {}
    scope_list = ["openid", "profile", "email"] + scopes

    # PCKE code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    oauth = OAuth2Session(client_id, redirect_uri=REDIRECT_URI, scope=scope_list)
    authorization_url, state = oauth.authorization_url(
        url=AUTHORITY_URL,
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )

    # Start the local service
    code = []
    httpd = http.server.HTTPServer((HOST_NAME, PORT), handlerFactory(code, state))

    # Request login page and look for code response
    webbrowser.open_new(authorization_url.replace("+", "%20"))

    while (len(code) == 0):
        httpd.handle_request()
    httpd.server_close()

    if (len(code) == 2):
        raise Exception(code[1])

    # Exchange code for token
    token_response = requests.post(
        url=PROD_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "code": code[0],
            "code_verifier": code_verifier,
        },
        allow_redirects=False,
    )
    token_response.raise_for_status()
    token = token_response.json()


    return token

def get_token_with_resource_password(client_id, client_secret):
    """This is a reserved feature that must be authorized by Altium before use."""
    if not client_id or not client_secret:
        raise Exception("client_id and/or client_secret are empty")

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    token = {}
    token_response = requests.post(
        url=PROD_TOKEN_URL,
        data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        },
    )
    token_response.raise_for_status()
    token = token_response.json()


    return token
