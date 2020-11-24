import Auth
import TwitterListener
import TwitterWriter

def readConfigFile():
    auth = Auth.Auth()
    return auth.readConfigFile("twitter-config.json")

# Perform OAuth 1
def oauth1():
    auth = Auth.Auth()
    APP_KEY, APP_SECRET, BEARER_TOKEN = auth.readConfigFile("twitter-config.json")
    oauth_url, OAUTH_TOKEN, OAUTH_TOKEN_SECRET = auth.getAuthUrl(APP_KEY, APP_SECRET)

    print("Authorize the app to access your account by clicking the following link:\n" + oauth_url)

    pin = input("\nInsert the pin: ")
    auth.authWithPin(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, pin)
    return APP_KEY, APP_SECRET, BEARER_TOKEN, OAUTH_TOKEN, OAUTH_TOKEN_SECRET


if __name__ == "__main__":
    print("\n" +
    " ___  __  __ __ ___  __ _____ ___ ___  __  __ __ _____ _   _  ___ ___ _____  __" + "\n"
    "| _ \/__\|  V  | __/' _/_   _| _ \ __|/  \|  V  |_   _| | | || __| __|_   _/' _/" + "\n"
    "| v / \/ | \_/ | _|`._`. | | | v / _|| /\ | \_/ | | | | 'V' || _|| _|  | | `._`." + "\n"
    "|_|_\\\\__/|_| |_|___|___/ |_| |_|_\___|_||_|_| |_| |_| !_/ \_!|___|___| |_| |___/" + "\n\n")


    # The Streaming API requires that you have OAuth 1 authentication credentials
    #APP_KEY, APP_SECRET, BEARER_TOKEN, OAUTH_TOKEN, OAUTH_TOKEN_SECRET = oauth1()
    APP_KEY, APP_SECRET, BEARER_TOKEN, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, STORAGE_PATH = readConfigFile()

    # When OAuth 1 is succeed, prepare threads for listening and writing new tweets
    tweets = []
    listener = TwitterListener.TwitterListener(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, tweets)
    writer   = TwitterWriter.TwitterWriter(STORAGE_PATH, tweets)

    print("Start listening...")
    listener.start()
    writer.start()

    # Loop to receive tweets and intercept Ctrl+c to stop listening in a correct way
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStop listening...")
        listener.stop()
        writer.stop()

        writer.join()
        listener.join()
