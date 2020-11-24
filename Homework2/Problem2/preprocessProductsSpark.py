from nltk.tokenize      import word_tokenize
from nltk.corpus        import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter   import *

# Class for preprocessing Amazon products for Spark usage
class PreprocessProductsSpark():
    def __init__(self):
        # Set stopwords
        self.stopWordsITA = set( stopwords.words("italian") )
        self.stopWordsENG = set( stopwords.words("english") )

        # Set stemmer
        #self.stemmer = SnowballStemmer("italian")
        self.stemmer = PorterStemmer()

    # Custom additional tokenizer, returns a list
    def tokenize(self, token):
        separators = ["/", "+", ","]

        # Check if a separator is contained in the token
        for sep in separators:
            if sep in token:
                newTokens = token.split(sep=sep, maxsplit=1)

                # Check if a float number has been splitted
                if (newTokens[0].isdigit() and newTokens[1].isdigit()):
                    continue

                return self.tokenize(newTokens[0]) + self.tokenize(newTokens[1])

        return [token]

    # Return True if the token is ok, False otherwise
    def normalize(self, token):
        strings = ["", ".", ",", ";", ":", "-", "(", ")", "[", "]"]

        if token in strings:
            return False

        return True

    # Preprocess the string and return it as a list of tuples (tokens,1)
    def preprocessString(self, string):
        if not string:
            return None

        #print("============")
        #print(string)
        preprocessedString = []

        # Tokenize the string using the default tokenizer
        tokens = word_tokenize(string)
        for t in tokens:
            # Tokenize the token using the custom tokenizer (maybe a token must be splitted into two or more custom tokens)
            newTokens = self.tokenize(t)

            # For each custom token continue preprocessing
            for token in newTokens:
                # Remove the stopwords and normalize the custom token
                if token not in self.stopWordsITA and token not in self.stopWordsENG and self.normalize(token):
                    # Stem the custom token
                    stemmedToken = self.stemmer.stem(token)

                    #print(token, " : ", stemmedToken)
                    preprocessedString.append( (stemmedToken, 1) )

        #print(preprocessedString)
        #print("============")
        return preprocessedString
