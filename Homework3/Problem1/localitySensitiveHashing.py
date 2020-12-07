from utils import hashFamily

class LocalitySensitiveHashing:
    # Init the class retrieving a hash function
    def __init__(self):
        self.hashFunction = hashFamily(31)

    # Given a collection of minwise hash signatures of a set of documents,
    # find all the documents pairs that are near each other
    def LSH(self, signatures, bands, rows):
        if (not signatures or bands*rows != len(signatures[0])):
            return None

        buckets = []
        bLen = 0

        # Nearest neighbors set of pairs
        nn = set()

        # Document index
        i = 0

        # For each signature in signatures
        for signature in signatures:
            #print("Signature[" + str(i) + "] is\n", signature)

            # For each band in bands
            for b in range(0, bands):
                # If buckets[b] doesn't exists
                if (b == bLen):
                    # Add an empty dictionary to the buckets
                    buckets.append({})
                    bLen += 1

                # Row vector to be hashed when populated
                vector = []

                # For each row in rows
                for r in range(0, rows):
                    #print("b: " + str(b) + "\tr: " + str(r) + "\tb*rows + r: " + str(b*rows + r))
                    vector.append( signature[b*rows + r] )

                # Compute the hash of the vector
                hash = self.hashFunction( str(vector) )

                # Check if the hash is already in the dictionary of the current band
                if (hash in buckets[b]):
                    # Add pairs to the nearest neighbors
                    for doc in buckets[b][hash]:
                        nn.add( (doc, i) if doc <= i else (i, doc) )

                    # Add the current document to the list indexed by the hash
                    buckets[b][hash].append(i)

                # Otherwise init an entry with key=hash and value=list with the current document
                else:
                    buckets[b][hash] = [i]

            i += 1

        return nn
