import os
import secrets

class Config:
    # Secure session configuration
    SECRET_KEY = secrets.token_hex(32)  # Use env variable or generate a random key

    # OAuth2 configuration
    CLIENT_SECRETS_FILE = "client_secret.json"
    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
