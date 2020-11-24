from twython import TwythonStreamer

# Receive data from the Twitter Stream
class Streamer(TwythonStreamer):
    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, tweets):
        super().__init__(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.tweets = tweets

    def on_success(self, data):
        print("============= TWEET RECEIVED =============")
        print(data)
        print("==========================================")

        tweet = {}

        # Add the tweet to the list only if it contains all the fields of interest
        print("============= INFO =============")
        if "user" in data and data["user"]:
            screenName = data["user"]["screen_name"]
            tweet["screen_name"] = screenName
            print("screen_name: " + screenName)
        else:
            return

        if "text" in data:
            text = data["text"]
            tweet["text"] = text
            print("text: " + text)
        else:
            return

        # Check if exact coordinates
        if "coordinates" in data and data["coordinates"]:
            coordinates = data["coordinates"]["coordinates"]
            tweet["coordinates"] = coordinates
            print("coordinates:")
            print(coordinates)
        # Else check if place and put as coordinate the center of Rome since the polygon bounding box is larger than the city
        elif "place" in data:
            tweet["coordinates"] = [12.496418, 41.902621]
            print("place:")
            print(data["place"])
        else:
            return
        print("================================")

        self.tweets.append(tweet)


    def on_error(self, status_code, data):
        print(status_code)
        print(data)
