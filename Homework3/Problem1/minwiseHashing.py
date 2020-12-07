from utils  import hashFamily
from random import getrandbits

class MinwiseHashing:
    # Given a collection of sets of objects (e.g. strings or numbers),
    # create a minwise hashing based signature for each set.
    # Returns a list of signatures
    def minHash(self, sets, n):
        if (not sets):
            return None

        # Signatures of the sets
        signatures = []

        # Pick n random hash functions
        hashFunctions = []
        for i in range(0, n):
            hashFunctions.append( hashFamily(i) )

        # For each set in sets
        for set in sets:
            # Signature for the current set
            signature = []
            # Signature index and length
            i = 0
            sLen = 0

            # For each hash function previously picked
            for hf in hashFunctions:

                # For each object in the set
                for obj in set:
                    # Hash the object with the current hash function
                    hash = hf( str(obj) )

                    # If signature[i] doesn't exists
                    if (i == sLen):
                        # Add the hash to the set of shingles
                        signature.append(hash)
                        sLen += 1

                    # Else compare the hashes
                    elif (hash < signature[i]):
                        # Update the min hash value
                        signature[i] = hash

                i += 1

            signatures.append(signature)

        return signatures
