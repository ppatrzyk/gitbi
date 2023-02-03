"""
Basic Auth for app
https://www.starlette.io/authentication/
"""
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
import base64
import logging
import repo

class BasicAuthBackend(AuthenticationBackend):
    def __init__(self, users):
        self.users = users
    async def authenticate(self, conn):
        try:
            auth = conn.headers.get("Authorization")
            assert auth is not None, "Auth not provided"
            scheme, credentials = auth.split()
            assert scheme.lower() == "basic", "Basic auth required"
            decoded = base64.b64decode(credentials).decode("ascii")
            user, _pass = decoded.split(":")
            assert decoded in self.users, "Bad user"
        except Exception as e:
            raise AuthenticationError(f"Auth error: {str(e)}")
        else:
            return AuthCredentials(["authenticated"]), SimpleUser(user)

def _auth_challenge(request, exception):
    """
    Ask for Basic auth password
    """
    headers = {"WWW-Authenticate": "Basic realm=Gitbi access"}
    return PlainTextResponse(status_code=401, headers=headers, content=str(exception))

try:
    users = repo.get_auth()
    parsed = (entry.split(":") for entry in users)
    user_names = []
    for parsed_entry, raw_entry in zip(parsed, users):
        assert len(parsed_entry) == 2, f"Malformed entry: {raw_entry}"
        user_names.append(parsed_entry[0])
    AUTH = [Middleware(AuthenticationMiddleware, backend=BasicAuthBackend(users), on_error=_auth_challenge), ]
    logging.info(f"{len(user_names)} users: {', '.join(user_names)}")
except Exception as e:
    AUTH = []
    logging.info(f"Auth not defined: {str(e)}")
