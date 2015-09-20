from flask import url_for, session
from oauth2client.client import OAuth2WebServerFlow
from dropbox.client import DropboxClient, DropboxOAuth2Flow

DROPBOX_APP_KEY = '1szh06pzua9nm1a'
DROPBOX_APP_SECRET = '4pqoe16cl3jtctf'

GDRIVE_CLIENT_ID='384706005510-hbbdfl1tef8g06artuuft5ubc7a9fllp.apps.googleusercontent.com'
GDRIVE_CLIENT_SECRET='RyYaHJkGL_Q9rYeqcjIylbHO'
GDRIVE_REDIRECT_URI = 'http://127.0.0.1:5000/google-auth-finish'
GDRIVE_SCOPE="https://www.googleapis.com/auth/drive"

def get_auth_flow():
    redirect_uri = url_for('dropbox_auth_finish', _external=True)
    return DropboxOAuth2Flow(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, redirect_uri,
                                       session, 'dropbox-auth-csrf-token')

def get_gd_auth_flow():
    redirect_uri = url_for('google_auth_finish', _external = True)
    return OAuth2WebServerFlow(client_id=GDRIVE_CLIENT_ID,
                           client_secret=GDRIVE_CLIENT_SECRET,
                           scope = GDRIVE_SCOPE,
                           redirect_uri=GDRIVE_REDIRECT_URI,
                           access_type = 'offline')