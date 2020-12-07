import hashlib
import time

# Implement a family of hash functions using a closure.
# Hash strings and takes an integer to define the member of the family.
# Return a hash function parametrized by i
def hashFamily(i):
    # how many bytes we want back
    resultSize = 8
    # how long can our i be (in decimal)
    maxLen = 20

    salt = str(i).zfill(maxLen)[-maxLen:]

    def hashMember(x):
        #return hashlib.sha1(x + salt).digest()[-resultSize:]
        return hashlib.sha1( (x + salt).encode("utf-8") ).digest()[-resultSize:]

    return hashMember

# Compute the Jaccard similarity between two sets
def JaccardSimilarity(setA, setB):
    if (setA == None or setB == None):
        return -1

    intersection = setA.intersection(setB)
    union        = setA.union(setB)

    return len(intersection) / len(union)

# Given the shingles of each of the documents,
# find the nearest neighbors by comparing all the shingle sets with each other
def nearestNeighborsShingleSets(sets):
    if (sets == None):
        return None

    nn = []
    size = len(sets)

    # For each set except the last of the list
    for i in range(0, size-1):
        setA = sets[i]

        # For each other set subsequent to the previous one
        for j in range(i+1, size):
            setB = sets[j]
            js = JaccardSimilarity(setA, setB)

            #print("(" + str(i) + "," + str(j) + ") = " + str(js) + "\t js = " + str(js))

            if (js >= 0.8):
                nn.append( (i, j) )

    return nn

def getCurrentMs():
    return int( round(time.time() * 1000) )
