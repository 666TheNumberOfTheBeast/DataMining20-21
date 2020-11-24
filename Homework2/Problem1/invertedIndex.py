import json

from preprocessProducts import PreprocessProducts

# Build and store an inverted index (about Amazon products previously downloaded) in a file

filenameRead  = "./products.tsv"
filenameWrite = "./invertedIndex.json"

pp = PreprocessProducts()

# Preprocess the products file and build an inverted index
invertedIndex = pp.preprocessFile(filenameRead)

# Store the invertedIndex in a file
with open(filenameWrite, "w") as outputFile:
    json.dump(invertedIndex, outputFile, indent=4)
