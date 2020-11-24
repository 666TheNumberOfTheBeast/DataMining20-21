from threading import Thread
import Streamer

# Listen for new tweets in Rome
class TwitterListener(Thread):
    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, tweets):
        super().__init__()
        self.APP_KEY            = APP_KEY
        self.APP_SECRET         = APP_SECRET
        self.OAUTH_TOKEN        = OAUTH_TOKEN
        self.OAUTH_TOKEN_SECRET = OAUTH_TOKEN_SECRET
        self.tweets = tweets

        self.running = False

    def run(self):
        self.streamer = Streamer.Streamer(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET, self.tweets)
        self.running = True

        while self.running:
            try:
                # Define a Rome bounding box as a pair of longitude and latitude pairs,
                # with the southwest corner of the bounding box coming first
                boundingBox = "12.382068, 41.806861, 12.592227, 41.990710"

                # Filter new tweets according to locations:
                    # a comma-separated list of longitude, latitude pairs specifying a set of bounding boxes to filter Tweets by.
                    # Only geolocated Tweets falling within the requested bounding boxes will be included—unlike the Search API,
                    # the user’s location field is not used to filter Tweets.

                # Tweet falls within a bounding box:
                # - If the coordinates field is populated, the values there will be tested against the bounding box.
                #   Note that this field uses geoJSON order (longitude, latitude).
                # - If coordinates is empty but place is populated, the region defined in place is checked for intersection
                #   against the locations bounding box. Any overlap will match.
                self.streamer.statuses.filter(locations=boundingBox)

                # A comma-separated list of phrases which will be used to determine what Tweets will be delivered on the stream.
                #self.streamer.statuses.filter(track="provo,roma")
            except Exception as e:
                print(e)

    def stop(self):
        self.running = False
        if self.streamer:
            print("Disconnecting the streamer...")
            self.streamer.disconnect()
