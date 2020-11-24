from threading import Thread
import json

# Write new tweets listened in Rome in a file as they are being collected
class TwitterWriter(Thread):
    def __init__(self, STORAGE_PATH, tweets):
        super().__init__()
        self.STORAGE_PATH = STORAGE_PATH
        self.tweets = tweets

        self.running = False

    def run(self):
        self.running = True

        while self.running:
            with open(self.STORAGE_PATH, 'w+', encoding='utf-8') as outputFile:
                json.dump(self.tweets, outputFile, indent=4)
                outputFile.flush()

    def stop(self):
        self.running = False
