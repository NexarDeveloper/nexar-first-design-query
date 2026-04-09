"""Resources for making A365 requests."""
import requests, re
import base64
import json
import time
from typing import Callable, Dict, Iterator

import jwt
from a365Token import get_access_token_using_refresh_token

A365_URL =  "https://usw2.dev-365.altium.com/napi/gateway/graphql" # "https://eur.365.altium.com/napi/gateway/graphql"

def decodeJWT(token):
    return json.loads(
        (base64.urlsafe_b64decode(token.split(".")[1] + "==")).decode("utf-8")
    )

class AltiumClient:
    def __init__(self, id, secret, refresh_token, pat, scopes = ['supply.domain']) -> None:
        #scopes = ['supply.domain', 'design.domain', 'user.access', 'offline_access']
        self.id = id
        self.secret = secret
        self.refresh_token = refresh_token
        self.pat = pat
        self.scopes = scopes
        self.api_url = A365_URL
        self.s = requests.session()
        self.s.keep_alive = False

        if pat is not None:
            self.token = pat
        elif all(v is not None for v in (id, secret, refresh_token)):
            self.token = get_access_token_using_refresh_token(id, secret, refresh_token, scopes)
            #self.s.headers.update({"token": self.token.get('access_token')})
            #self.s.headers.update({"Authorization": f"Bearer {self.token.get('access_token')}"})
            self.exp = decodeJWT(self.token.get('access_token')).get('exp')

    def check_exp(self):
        if (self.exp < time.time() + 300):
            self.token = get_access_token_using_refresh_token(self.id, self.secret, self.refresh_token, self.scopes)
            #self.s.headers.update({"token": self.token.get('access_token')})
            #self.s.headers.update({"Authorization": f"Bearer {self.token.get('access_token')}"})
            self.exp = decodeJWT(self.token.get('access_token')).get('exp')
            
    def token_workspace_scope_match(self, workspace_guid):
        # If self.token is a string (e.g. PAT case), convert it to a dictionary (scope in that case will be an array, not str)
        if isinstance(self.token, str):
            token_data = jwt.decode(self.token, options={"verify_signature": False})   
        else:
            token_data = self.token
        
        a365_ws_prefix = "a365:workspace:"
        scopes = token_data.get('scope', [])
        scopes = scopes.split() if isinstance(scopes, str) else list(scopes)
        scopes = [s.lower().removeprefix(a365_ws_prefix) for s in scopes]
        return workspace_guid.lower() in scopes
        

    def get_query(self, query: str, variables: Dict = {}) -> dict:
        """Return A365 response for the query."""
        try:
            if self.pat is not None:
                r = self.s.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers={"Authorization": f"Bearer {self.pat}"}
                )
            else:
                self.check_exp()      
                temp = self.token.get('access_token')
                r = self.s.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers={"Authorization": f"Bearer {temp}"}
                )

        except Exception as e:
            print(e)
            raise Exception("Error while getting A365 response")

        response = r.json()
        if ("errors" in response):
            for error in response["errors"]: print(error["message"])
            raise SystemExit

        return response["data"]

    class Node:
        def __init__(self, client, query: str, variables: Dict, f: Callable) -> None:
            self.client = client
            self.query = query
            self.variables = variables
            self.f = f
            self.name = re.search("after[\s]*:[\s]*\$([\w]*)", query).group(1)

        def __iter__(self) -> Iterator:
            self.pageInfo = {"hasNextPage": True}
            return self
 
        def __next__(self):
            if (not self.pageInfo["hasNextPage"]): raise StopIteration

            data = self.client.get_query(self.query, self.variables)

            self.pageInfo = self.f(data)["pageInfo"]
            self.variables[self.name] = self.pageInfo["endCursor"]
            return self.f(data)["nodes"]

    def NodeIter(self, query: str, variables: dict, f: Callable) -> Iterator:
        return AltiumClient.Node(self, query, variables, f)
