import json
import math

from preprocessProducts import PreprocessProducts

# Perform a query about Amazon products previously downloaded and preprocessed


# Get the query from the user
query = input("Enter your query: ")
if not query:
    print("Invalid input")
    exit()

print("\nProcessing the query...")

# Preprocess the query
pp = PreprocessProducts()
preprocessedQuery = pp.preprocessString(query)

#print("preprocessedQuery: ", preprocessedQuery)

# Retrieve the invertedIndex
filename = "./invertedIndex.json"

with open(filename, "r") as file:
    invertedIndex = json.load(file)

# Find matches of the query tokens in the inverted index and store the resulting tokens maps in a map where the key is
# the token and the value a tuple consisting of (iterator of the internal map, current key in the token map)
matchTokens = {}
for queryToken in preprocessedQuery:
    if queryToken in invertedIndex:
        map = invertedIndex[queryToken]
        iterator = iter(map)

        try:
            matchTokens[queryToken] = (iterator, next(iterator))
        except StopIteration:
            continue

#print("matchTokens: ", matchTokens)

# Find the tokens (among the match tokens) having the minimum values of the document number and
# return the map consisting of key,value pairs where token is the key and the number of occurrences in the doc are the values.
# Return also the min document number
def findMin(matchTokens, invertedIndex):
    if not matchTokens:
        return None

    min       = None
    minTokens = {}

    for token in matchTokens:
        # Get the document number and remember to convert to an integer for comparison
        docNumberStr = matchTokens[token][1]
        docNumber    = int(docNumberStr)
        tokenMap     = invertedIndex[token]

        #print("token: ", token, "\tdocNumber: ", docNumber, "\tmin: ", min)

        # If docNumber == min => add the key,value pair in the minTokens map where
        # token is the key and the number of occurrences in the doc is the value
        if min == None or docNumber == min:
            min = docNumber
            minTokens[token] = tokenMap[docNumberStr]

        # If docNumber < min => clear previous minTokens map, init new one and set the minimum
        elif docNumber < min:
            min = docNumber
            minTokens.clear()
            minTokens[token] = tokenMap[docNumberStr]

    return minTokens, min

# Compute vector magnitude
def magnitude(vector):
    if not vector:
        return None

    sum = 0
    for value in vector:
        sum += value * value

    return math.sqrt(sum)

# Compute the cosine similarity between the two maps where:
# - query map keys are tokens while values are the corresponding number of occurrences in the document
# - document map keys are tokens while values are the corresponding number of occurrences in the document
def cosineSimilarity(query, document):
    if not query or not document:
        return None

    sum = 0
    docOccurrencesList = []

    # Scan the query tokens
    for queryToken in query:
        # Check if the queryToken is in the document map
        if queryToken in document:
            #  Contribute to dot product
            docOccurrences   = document[queryToken]
            queryOccurrences = query[queryToken]
            sum += queryOccurrences * docOccurrences

            # Store docOccurrences value after used to compute the magnitude
            docOccurrencesList.append(docOccurrences)

    # Compute document magnitude
    # (I don't need to compute query magnitude since it does not affect cosine similarities because is the same for all documents)
    docMagnitude = magnitude(docOccurrencesList)
    if not docMagnitude:
        return None

    #print("sum: ", sum)
    #print("docMagnitude: ", docMagnitude)

    return sum/docMagnitude

maxSimilarity = -1
bestDocNumber = -1
# Perform the query scanning the lists retrieved from the invertedIndex using the cosine similarity
while matchTokens:
    #print("matchTokens: ", matchTokens)

    # Find the tokens having the minimum document number (line in the tsv file) and the minimum document number
    docMap, docNumber = findMin(matchTokens, invertedIndex)
    #print("docMap: ", docMap)
    #print("docNumber: ", docNumber)

    # Compute cosine similarity between the query and the found document
    similarity = cosineSimilarity(preprocessedQuery, docMap)
    #print("similarity: ", similarity)
    if not similarity:
        print("Error")
        exit()

    # Check if update max cosine similarity and most related document
    if similarity > maxSimilarity:
        maxSimilarity = similarity
        bestDocNumber = docNumber

    # Advance the iterators that are in the docMap
    removeTokens = []
    for token in docMap:
        iterator = matchTokens[token][0]
        try:
            matchTokens[token] = (iterator, next(iterator))
        except StopIteration:
            # Exception happens when iteration is over,
            # so add the token to the tokens to remove from the matchTokens map
            removeTokens.append(token)

    # Remove tokens from the matchTokens map that have iterated all their documents
    for token in removeTokens:
        matchTokens.pop(token)

    #print("=====================")


# Return the most related product
#print("maxSimilarity: ", maxSimilarity)
#print("bestDocNumber: ", bestDocNumber)

if bestDocNumber == -1:
    print("\nNo related product found")
    exit()

print("\nThe best related product is the following\n")

# Read line in products file
filename = "./products.tsv"
i = 1

with open(filename, "r") as file:
    for line in file:
        if i == bestDocNumber:
            s = line.split("\t")
            line = "Title: " + s[0] + "\n\nPrice: " + s[1] + "\n\nPrime product: " + s[2] + "\n\nProduct url: " + s[3] + "\n\nRank: " + s[4]
            print(line)
            break
        i += 1
