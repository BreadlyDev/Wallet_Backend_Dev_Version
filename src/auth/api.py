import os

from httpx_oauth.clients.google import GoogleOAuth2

from src.config import GOOGLE_CLIENT_SECRET, GOOGLE_CLIENT_ID

client_id: str = GOOGLE_CLIENT_ID
client_secret: str = GOOGLE_CLIENT_SECRET

google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", client_id),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", client_secret),
    scopes=["openid", "profile", 'email']
)
