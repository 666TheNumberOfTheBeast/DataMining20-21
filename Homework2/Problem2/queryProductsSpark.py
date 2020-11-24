from pyspark.sql import SparkSession
from operator import add
import json
import math
from decimal import Decimal

from preprocessProductsSpark import PreprocessProductsSpark

# Perform a query about Amazon products previously downloaded and preprocessed using Spark

spark = SparkSession.builder.appName("BuildInvertedIndex").getOrCreate()

# Get the query from the user
query = input("Enter your query: ")
if not query:
    print("Invalid input")
    exit()

print("\nProcessing the query...")

# Retrieve the invertedIndex
filename = "./invertedIndexSpark.json"

with open(filename, "r") as file:
    invertedIndex = json.load(file)

# Preprocess the query
pp = PreprocessProductsSpark()

# Get the list of tuples consisting of (token, 1)
preprocessedQuery = pp.preprocessString(query)

# Count occurrences of each token in the list
preprocessedQuery = spark.sparkContext.parallelize(preprocessedQuery) \
                                      .reduceByKey(add)

#print("invertedIndex: " , invertedIndex)
#print("preprocessedQuery: ", preprocessedQuery.collect())
#print("preprocessedQuery: ", preprocessedQuery.collectAsMap())

# 1. Filter to get match tokens between the query tokens and the inverted index tokens
# 2. Map each token to the array retrieved from the invertedIndex composing of line number, number of occurrences in line
#    obtaining tuples as (array, occurrences in query)
# 3. Map each tuple to a different structure of tuple as (line number, (occurrences in line, occurrences in query)) so
#    each array has been decomponed in tuples
# 4. Map each tuple to a tuple consisting of (line number, (contribute to the dot product, contribute to the document sum square))
# 5. Sort the collection by the keys to save computation on the next step
# 6. Reduce by key to get as value a tuple consisting of (dot product, document sum square)
# 7. Map each tuple to a tuple consisting of (line number, cosine similarity)

bestDoc = preprocessedQuery.filter( lambda t : t[0] in invertedIndex )                                             \
                           .map( lambda t : (invertedIndex[t[0]], t[1]) )                                          \
                           .flatMap( lambda t : [(t[0][i], (t[0][i+1], t[1])) for i in range(0, len(t[0])-1, 2)] ) \
                           .mapValues( lambda t : (t[0]*t[1], t[0]*t[0]) )                                         \
                           .sortByKey()                                                                            \
                           .reduceByKey ( lambda t1,t2 : (t1[0]+t2[0], t1[1]+t2[1]) )                              \
                           .mapValues ( lambda t : (t[0]/math.sqrt(t[1])) )                                        \
                           .sortByKey()

#print("bestDoc: ", bestDoc.collect())

# Return the most related product
try:
    # Find the document having the maximum cosine similarity value
    bestDoc = bestDoc.max( lambda t : t[1] )
    #print("max: ", bestDoc)
    bestDocNumber = bestDoc[0]
except:
    print("\nNo related product found")
    exit()

print("\nThe best related product is the following\n")

# Read line in products file
filename = "../Problem1/products.tsv"
i = 1

with open(filename, "r") as file:
    for line in file:
        if i == bestDocNumber:
            s = line.split("\t")
            line = "Title: " + s[0] + "\n\nPrice: " + s[1] + "\n\nPrime product: " + s[2] + "\n\nProduct url: " + s[3] + "\n\nRank: " + s[4]
            print(line)
            break
        i += 1
