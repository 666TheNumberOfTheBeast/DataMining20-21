from pyspark.sql import SparkSession
from operator import add
import json

from preprocessProductsSpark import PreprocessProductsSpark

# Build and store an inverted index (about Amazon products previously downloaded) in a file using Spark

def getDescription(line):
    try:
        description = line.split(sep="\t", maxsplit=1)[0]

    except Exception as e:
        print(e)
        return None

    return description

spark = SparkSession.builder.appName("BuildInvertedIndex").getOrCreate()
filenameRead  = "../Problem1/products.tsv"
filenameWrite = "./invertedIndexSpark.json"

lines = spark.sparkContext.textFile(filenameRead)
pp = PreprocessProductsSpark()

# 1. Get line number of each line via zipWithIndex obtaining for each line a tuple (line, index)
# 2. Then for each tuple map each line to the corresponding description and each index to index+1 = line number
# 3. Preprocess each product description mapping each tuple to a tuple consisting of
#    (list of tuples (tokens in description, 1), line number)
# 4. For counting occurrences of each token in each list of tokens, restructure each tuple as ((token, line number), 1)
# 5. Count occurrences of each token in each list of tokens using reduceByKey
#    obtaining each tuple as ((token, line number), occurrences in line)
# 6. Restructure each tuple replacing the token in the inner tuple with the occurrences in line and viceversa
#    obtaining each tuple as (token, (line number, occurrences in line))
# 7. Sort each tuple according the token and the line number
# 8. Reduce the collection to group the tokens

invertedIndex = spark.sparkContext.parallelize( lines.zipWithIndex().collect() )                 \
                                  .map( lambda t : (getDescription(t[0]), t[1]+1) )              \
                                  .map( lambda t : (pp.preprocessString(t[0]), t[1]) )           \
                                  .flatMap( lambda t : [((tp[0], t[1]), tp[1]) for tp in t[0]] ) \
                                  .reduceByKey( add )                                            \
                                  .map( lambda t : (t[0][0], (t[0][1], t[1])) )                  \
                                  .sortBy( lambda t : (t[0], t[1][0]) )                          \
                                  .reduceByKey( add )

#print( invertedIndex.collect() )
#print( invertedIndex.collectAsMap() )

# Store the invertedIndex in a file
with open(filenameWrite, "w") as outputFile:
    json.dump(invertedIndex.collectAsMap(), outputFile, indent=4)
