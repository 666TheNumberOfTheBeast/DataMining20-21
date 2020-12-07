from utils import hashFamily

class Shingling:
    # Init the class retrieving a hash function
    def __init__(self):
        self.hashFunction = hashFamily(13)

    # Given a document, create its set of character shingles of some length k
    def shingling(self, document, k):
        if (not document or k < 1):
            return None

        # Set of shingles of the document to avoid duplicates
        shingles = set()

        # Aux function
        def hashAndAdd(shingle):
            # Hash the shingle
            hash = self.hashFunction(shingle)

            # Add the hash to the set of shingles
            shingles.add(hash)

        # Compute max index for the subsequent loop
        maxIndex = len(document) - k

        # Check if the document length is less or equal the length of a shingle
        if(maxIndex <= 0):
            hashAndAdd(document)
            return shingles

        # Scan document characters
        for i in range(0, maxIndex+1):
            # Get slice of the text of length k (last slice can be less than k)
            shingle = document[i : i+k]
            hashAndAdd(shingle)

        return shingles
