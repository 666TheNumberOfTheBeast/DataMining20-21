from nltk.tokenize      import word_tokenize
from nltk.corpus        import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter   import *

# Class for preprocessing Amazon products
class PreprocessProducts():
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

    # Preprocess the file and build an inverted index as a map where the keys are the tokens and the values are a map
    # consisting of key,value pairs where the key is the product line in file and
    # the value the number of occurrences in the product line
    def preprocessFile(self, filename):
        if not filename:
            return None

        invertedIndex = {}

        # Read each line (product) of the file
        with open(filename, "r") as file:
            lineNumber = 1
            for line in file:
                # Try getting the description of the product
                try:
                    description = line.split(sep="\t", maxsplit=1)[0]

                except Exception as e:
                    print(e)
                    continue

                #print("============")
                #print(description)
                #preprocessedDescription = []

                # Tokenize the description of each product using the default tokenizer
                tokens = word_tokenize(description)
                for t in tokens:
                    # Tokenize the token using the custom tokenizer (maybe a token must be splitted into two or more custom tokens)
                    newTokens = self.tokenize(t)

                    # For each custom token continue preprocessing
                    for token in newTokens:
                        # Remove the stopwords and normalize the custom token
                        if token not in self.stopWordsITA and token not in self.stopWordsENG and self.normalize(token):
                            # Stem the custom token
                            stemmedToken = self.stemmer.stem(token)

                            # Check if the stemmedToken is already in the invertedIndex
                            if stemmedToken in invertedIndex:
                                tokenMap = invertedIndex[stemmedToken]

                                # Check if the current lineNumber is already in the stemmedToken map
                                # and increase the number of occurrences in the string
                                if lineNumber in tokenMap:
                                    tokenMap[lineNumber] += 1
                                # Otherwise add the current lineNumber to the map
                                # and init the corresponding number of occurrences in the line
                                else:
                                    tokenMap[lineNumber] = 1

                            # Otherwise add the stemmedToken to the invertedIndex as key and value a map
                            # where the key is the lineNumber while the value the occurrencesInLine
                            else:
                                invertedIndex[stemmedToken] = { lineNumber: 1 }

                            #print(token, " : ", stemmedToken)
                            #preprocessedDescription.append(stemmedToken)

                #print(preprocessedDescription)
                #print("============")
                lineNumber += 1

        return invertedIndex

    # Preprocess the string and return it using a map of key,value pairs where
    # the key is the token and the value the number of occurrences in the string
    def preprocessString(self, string):
        if not string:
            return None

        #print("============")
        #print(string)
        preprocessedString = {}

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
                    #preprocessedString.append(stemmedToken)

                    # Check if the current stemmedToken is already in the preprocessedString map
                    # and increase the number of occurrences in the string
                    if stemmedToken in preprocessedString:
                        preprocessedString[stemmedToken] += 1
                    # Otherwise add the current stemmedToken to the map
                    # and init the corresponding number of occurrences in the string
                    else:
                        preprocessedString[stemmedToken] = 1

        #print(preprocessedString)
        #print("============")
        return preprocessedString
