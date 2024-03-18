"""Resources for making Nexar requests."""
import base64
import json
import logging
import os
import re
import time
from typing import Callable, Dict, Iterator

import requests
from requests_toolbelt import MultipartEncoder

from .nexarToken import get_token
from .errors import NexarClientBadRequestError, NexarClientUploadError

NEXAR_URL = "https://api.nexar.com/graphql"
NEXAR_FILE_URL = "https://files.nexar.com/Upload/WorkflowAttachment"

logger = logging.getLogger('NexarClient')

def decodeJWT(token):
    return json.loads(
        (base64.urlsafe_b64decode(token.split(".")[1] + "==")).decode("utf-8")
    )

class NexarClient:
    def __init__(self, id, secret, scopes = ['supply.domain'], refresh_token=None) -> None:
        #scopes = ['supply.domain', 'design.domain', 'user.access', 'offline_access']
        self.id = id
        self.secret = secret
        self.scopes = scopes
        self.api_url = NEXAR_URL
        self.s = requests.session()
        self.s.keep_alive = False

        self.token = get_token(id, secret, scopes, refresh_token)
        self.s.headers.update({"token": self.token.get('access_token')})
        self.exp = decodeJWT(self.token.get('access_token')).get('exp')

    def check_exp(self):
        if (self.exp < time.time() + 300):
            self.token = get_token(self.id, self.secret, self.scopes, self.token.get('refresh_token'))
            self.s.headers.update({"token": self.token.get('access_token')})
            self.exp = decodeJWT(self.token.get('access_token')).get('exp')

    def get_query(self, query: str, variables: Dict = {}) -> dict:
        """Return Nexar response for the query."""
        logger.info(f"POST - {self.api_url}")
        logger.debug(f"POST - {self.api_url}:\n{query}{variables}")
        self.check_exp()
        r = self.s.post(
            self.api_url,
            json={"query": query, "variables": variables},
        )

        response = r.json()
        if ("errors" in response):
            logger.error(response)
            raise NexarClientBadRequestError
        logger.debug(f'POST - {self.api_url} - 200: {response}')

        return response["data"]

    def upload_file(self, workspaceUrl: str, path: str, container: str) -> str:
        """Return Nexar response for the file upload."""
        try:
            multipart_data = MultipartEncoder(
                fields = {
                    'file': (os.path.basename(path), open(path, 'rb'), 'text/plain'),
                    'workspaceUrl': workspaceUrl,
                    'container': container,
                }
            )

            r = self.s.post(
                NEXAR_FILE_URL,
                data = multipart_data,
                headers = {
                    'Content-Type': multipart_data.content_type,
                }
            )

        except Exception as e:
            logger.exception(e)
            raise NexarClientUploadError

        return r.text

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
        return NexarClient.Node(self, query, variables, f)
