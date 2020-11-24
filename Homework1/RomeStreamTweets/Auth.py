from twython import Twython
import json

# Authentication class for Twitter using Twython
class Auth:
    def readConfigFile(self, filename):
        with open(filename, "r") as file:
            f = file.read()

        dict = json.loads(f)
        APP_KEY             = dict["API key"]
        APP_SECRET          = dict["API secret key"]
        BEARER_TOKEN        = dict["Bearer token"]
        ACCESS_TOKEN        = dict["Access token"]
        ACCESS_TOKEN_SECRET = dict["Access token secret"]
        STORAGE_PATH        = dict["Storage path"]

        return APP_KEY, APP_SECRET, BEARER_TOKEN, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, STORAGE_PATH

    # First phase of OAuth 1 (User Authentication) - get authentication url
    def getAuthUrl(self, APP_KEY, APP_SECRET):
        twitter = Twython(APP_KEY, APP_SECRET)
        auth = twitter.get_authentication_tokens()

        OAUTH_TOKEN        = auth['oauth_token']
        OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
        oauth_url          = auth['auth_url']

        return oauth_url, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

    # Second phase of OAuth 1 (User Authentication) -
    # after user authorizes the application to access some of his/her account details
    def authWithPin(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, pin):
        twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        auth = twitter.get_authorized_tokens(pin)

        OAUTH_TOKEN        = auth['oauth_token']
        OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

        return OAUTH_TOKEN, OAUTH_TOKEN_SECRET

    # OAuth 2 (App Authentication)
    def oauth2(self, APP_KEY, APP_SECRET):
        twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
        ACCESS_TOKEN = twitter.obtain_access_token()

        twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
        return
