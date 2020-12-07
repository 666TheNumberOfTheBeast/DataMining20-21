from shingling                import Shingling
from minwiseHashing           import MinwiseHashing
from localitySensitiveHashing import LocalitySensitiveHashing

from utils import nearestNeighborsShingleSets, getCurrentMs


if __name__ == '__main__':
    '''docs = [ "The results of the American elections have not yet been determined", \
             "The quick brown fox jumps over the lazy dog",                        \
             "The results of the American elections have not yet been determined", \
             "The results of the american elections have not yet been determined" ]'''

    '''docs = [ "a", \
             "ab", \
             "abc", \
             "abcd", \
             "abcde", \
             "abcdef", \
             "abcdefg", \
             "abcdefgh", \
             "abcdefghi", \
             "abcdefghij", \
             "abcdefghijk", \
             "abcdefghijkl", \
             "abcdefghijklm", \
             "abcdefghijklmn", \
             "abcdefghijklmno", \
             "abcdefghijklmnop", \
             "abcdefghijklmnopq", \
             "abcdefghijklmnopqr", \
             "abcdefghijklmnopqrs", ]'''


    # Products file
    filename  = "./../../Homework2/Problem1/products.tsv"

    # Read the file
    with open(filename, "r") as file:
        docs = []
        for line in file:
            # Try getting the description of the product
            try:
                description = line.split(sep="\t", maxsplit=1)[0]

            except Exception as e:
                print(e)
                continue

            docs.append(description)

    #print("docs:\n", docs)

    # Shingle length
    k = 10
    # Signature length
    n = 12
    # Shingle sets
    sets = []

    s = Shingling()

    # Create a shingle set for each doc
    for i in range(0, len(docs)):
        #print("\nDoc" + str(i) + " is:\n", docs[i])
        shingles = s.shingling(docs[i], k)
        sets.append(shingles)
        #print("\nDoc" + str(i) + " set is:\n", shingles)

    # Create a signature for each shingle set
    mh = MinwiseHashing()
    signatures = mh.minHash(sets, n)
    #print("\nSets signatures are:\n", signatures)

    previous = getCurrentMs()

    # Create buckets where inserting similar signatures
    lsh = LocalitySensitiveHashing()
    # Since n = b*r and threshold about 0.8 => 0.8 = (1/b)^(1/r)
    b = 2 #4
    r = 6 #3
    nnLSH = lsh.LSH(signatures, b, r)

    now = getCurrentMs()
    epsLSH = now - previous

    nnLSH = set(sorted(nnLSH))
    print("\nNearest neighbors LSH are:\n", nnLSH)

    previous = getCurrentMs()

    # Compute nearest neighbors from shingle sets
    nnSS = nearestNeighborsShingleSets(sets)

    now = getCurrentMs()
    epsSS = now - previous

    nnSS = set(nnSS)
    print("\nNearest neighbors by comparing all the shingle sets with each other are:\n", nnSS)

    # Stats
    intersection = nnLSH.intersection(nnSS)
    fp = nnLSH.difference(nnSS)
    fn = nnSS.difference(nnLSH)

    print("\nNearest neighbors LSH and SS intersection:\n", intersection)
    print("\nNearest neighbors LSH false positives:\n", fp)
    print("\nNearest neighbors LSH false negatives:\n", fn)

    print("\nNearest neighbors LSH size: ", len(nnLSH))
    print("Nearest neighbors SS size: ", len(nnSS))
    print("Nearest neighbors LSH and SS intersection size: ", len(intersection))
    print("Nearest neighbors LSH false positives size: ", len(fp))
    print("Nearest neighbors LSH false negatives size: ", len(fn))

    print("\nElapsed time LSH: " + str(epsLSH) + " ms vs Elapsed time SS: " + str(epsSS) + " ms")
