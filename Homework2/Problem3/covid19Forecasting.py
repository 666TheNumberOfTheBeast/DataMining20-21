from pyspark.sql import SparkSession, functions, Window
from pyspark.ml.feature    import StringIndexer, IndexToString, VectorAssembler, SQLTransformer
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor, RandomForestRegressor, GBTRegressor, IsotonicRegression, FMRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning     import CrossValidator, ParamGridBuilder

import matplotlib.pyplot as plt
import matplotlib.dates  as mdates

import datetime as d


# Select entries from the dataset that have a Country_Region value one among those in the states array
def selectStates(dataset, states):
    if (dataset == None or states == None):
        return None

    return dataset.filter( dataset.Country_Region.isin(states) )

# Encode string columns
def encodeColumns(dataset):
    if (dataset == None):
        return None

    dataset = StringIndexer(inputCol="Country_Region", outputCol="cr") \
                .fit(dataset)                                          \
                .transform(dataset)
    dataset = StringIndexer(inputCol="Date", outputCol="d")            \
                .fit(dataset)                                          \
                .transform(dataset)
    dataset = StringIndexer(inputCol="Target", outputCol="t")          \
                .fit(dataset)                                          \
                .transform(dataset)

    dataset = dataset.withColumn("Population", dataset.Population.cast("int"))
    dataset = dataset.withColumn("Weight", dataset.Weight.cast("double"))

    try:
        dataset = dataset.withColumn("TargetValue", dataset.TargetValue.cast("int"))
    except:
        pass

    return dataset

# Add a column to the dataset containing the yesterday target value
'''def addYesterdayColumn(dataset):
    return training.withColumn( "YesterdayTargetValue",
                                functions.lag("TargetValue", offset=2, default=0).over(Window.partitionBy("Country_Region").orderBy("Date")) )'''

# Group features
def groupFeatures(dataset):
    if (dataset == None):
        return None

    features = ["cr", "Population", "d", "t"]
    #features = ["cr", "Population", "t", "YesterdayTargetValue"]
    dataset = VectorAssembler(inputCols=features, outputCol="features") \
               .transform(dataset)
    return dataset


spark = SparkSession.builder.appName("ML").getOrCreate()

trainFile = "train.csv"
testFile  = "test.csv"

# Prepare training data from a csv file
training = spark.read.format("csv")                          \
                     .options(dropInvalid=True, header=True) \
                     .load(trainFile)

print("======== INITIAL TRAINING SET ========")
training.show(5)

# States for which performing a prediction of coronavirus cases (all with County and Province_State columns null)
states = ["Brazil", "Germany", "Italy", "Japan", "Spain", "Russia"]

# Select only states of interest from the table
training = selectStates(training, states)

# Encode string columns
training = encodeColumns(training)

# Add a column to the dataset containing the yesterday target value
#training = addYesterdayColumn(training)

# Group features
training = groupFeatures(training)

print("======== ENCODED TRAINING SET ========")
training.show(5)
#print(training.dtypes, "\n")


# Regressors
lr  = None
dt  = None
rf  = None
gbt = None
ir  = None
fm  = None

# Create a regression algorithm instance
#lr = LinearRegression(labelCol="TargetValue", weightCol="Weight")
#dt = DecisionTreeRegressor(labelCol="TargetValue", weightCol="Weight")
rf = RandomForestRegressor(labelCol="TargetValue", weightCol="Weight")
#gbt = GBTRegressor(labelCol="TargetValue", weightCol="Weight")
#ir = IsotonicRegression(labelCol="TargetValue", weightCol="Weight")
#fm = FMRegressor(labelCol="TargetValue")

# Print out the parameters, documentation, and any default values
'''if (lr):
    print("======== LinearRegression parameters ========\n" + lr.explainParams() + "\n")
elif (dt):
    print("======== DecisionTreeRegressor parameters ========\n" + dt.explainParams() + "\n")
elif (rf):
    print("======== RandomForestRegressor parameters ========\n" + rf.explainParams() + "\n")
elif (gbt):
    print("======== GBTRegressor parameters ========\n" + gbt.explainParams() + "\n")
elif (ir):
    print("======== IsotonicRegression parameters ========\n" + ir.explainParams() + "\n")
elif (fm):
    print("======== FMRegressor parameters ========\n" + fm.explainParams() + "\n")'''

# Use a ParamGridBuilder to construct a grid of hyper-parameters to search over
paramGrid = ParamGridBuilder()
regressor = None

if (lr):
    # Not suitable for the problem
    regressor = lr
    '''paramGrid.addGrid(lr.aggregationDepth, [2, 10, 20])             \
             .addGrid(lr.elasticNetParam, [0, 0.25, 0.5, 0.75, 1])  \
             .addGrid(lr.fitIntercept, [True, False])               \
             .addGrid(lr.maxIter, [100, 250, 500])                  \
             .addGrid(lr.regParam, [0, 0.2, 0.4])'''

    # Best hyper-parameters
    paramGrid.addGrid(lr.aggregationDepth, [2])  \
             .addGrid(lr.elasticNetParam, [0])   \
             .addGrid(lr.fitIntercept, [True])   \
             .addGrid(lr.maxIter, [100])         \
             .addGrid(lr.regParam, [0])
    # Root Mean Squared Error (RMSE) on test data = 711.396
elif (dt):
    regressor = dt
    '''paramGrid.addGrid(dt.maxBins, [187, 256])               \
             .addGrid(dt.maxDepth, [5, 10, 15, 20, 25, 30]) \
             .addGrid(dt.minInstancesPerNode, [1, 3, 5])'''

    # Best hyper-parameters
    paramGrid.addGrid(dt.maxBins, [187])               \
             .addGrid(dt.maxDepth, [5])                \
             .addGrid(dt.minInstancesPerNode, [3])
    # Root Mean Squared Error (RMSE) on test data = 892.324
    # CV is very fast but not good results
elif (rf):
    regressor = rf
    '''paramGrid.addGrid(rf.maxBins, [187, 256])                    \
             .addGrid(rf.maxDepth, [5, 10, 15, 20, 30])          \
             .addGrid(rf.numTrees, [20, 40, 60, 80, 100, 120])   \
             .addGrid(rf.bootstrap, [True, False])               \
             .addGrid(rf.subsamplingRate, [1, 0.8, 0.7])'''

    # Best hyper-parameters
    paramGrid.addGrid(rf.maxBins, [187])        \
             .addGrid(rf.maxDepth, [5])         \
             .addGrid(rf.numTrees, [100])       \
             .addGrid(rf.bootstrap, [False])    \
             .addGrid(rf.subsamplingRate, [1])

    # Root Mean Squared Error (RMSE) on test data = 515.058
    # CV is very slow and not good results
elif (gbt):
    regressor = gbt
    '''paramGrid.addGrid(gbt.maxBins, [187, 256])            \
             .addGrid(gbt.maxDepth, [5, 10, 15])          \
             .addGrid(gbt.minInstancesPerNode, [1, 3, 5]) \
             .addGrid(gbt.stepSize, [0.1, 0.01, 0.001])   \
             .addGrid(gbt.subsamplingRate, [1, 0.8, 0.7])
             #.addGrid(gbt.maxIter, [20, 30, 40])'''

    # Best hyper-parameters
    paramGrid.addGrid(gbt.maxBins, [187])            \
             .addGrid(gbt.maxDepth, [5])             \
             .addGrid(gbt.minInstancesPerNode, [1])  \
             .addGrid(gbt.stepSize, [0.01])          \
             .addGrid(gbt.subsamplingRate, [1])
    # Root Mean Squared Error (RMSE) on test data = 688.496
    # CV is very slow and not good results
elif (ir):
    # Not suitable for the problem
    regressor = ir
    '''paramGrid.addGrid(ir.featureIndex, [0, 1, 2, 3]) \
             .addGrid(ir.isotonic, [True, False])'''

    # Best hyper-parameters
    paramGrid.addGrid(ir.featureIndex, [3]) \
             .addGrid(ir.isotonic, [False])
    # Root Mean Squared Error (RMSE) on test data = 703.897
elif (fm):
    # Not suitable for the problem
    regressor = fm
    paramGrid.addGrid(fm.factorSize, [8, 12, 16])   \
             .addGrid(fm.fitLinear, [True, False])  \
             .addGrid(fm.fitLinear, [True, False])  \
             .addGrid(fm.regParam, [0, 0.1, 0.01])  \
             .addGrid(fm.stepSize, [1, 3, 5])

    ''' Best model params:
        - factorSize: 8 = def
        - fitLinear: False
        - regParam: 0.1
        - stepSize: 1 = def
    '''


paramGrid = paramGrid.build()
crossval = CrossValidator(estimator=regressor,
                          estimatorParamMaps=paramGrid,
                          evaluator=RegressionEvaluator(labelCol="TargetValue", predictionCol="prediction"),
                          numFolds=3)

# Run cross-validation and choose the best set of hyper-parameters
model = crossval.fit(training)

# Choose the best model
model = model.bestModel

# Print out the parameters, documentation, and any default values
print("\n======== Best Model parameters ========\n" + model.explainParams() + "\n")


# Prepare test data from a csv file
test = spark.read.format("csv")                          \
                 .options(dropInvalid=True, header=True) \
                 .load(testFile)
                 #.load(trainFile)
print("======== INITIAL TEST SET ========")
test.show(5)

# Select only states of interest from the table
training = selectStates(training, states)

# Encode string columns
test = encodeColumns(test)

# Group features
test = groupFeatures(test)

print("======== ENCODED TEST SET ========")
test.show(5)
#print(test.dtypes, "\n")

# Make predictions on test data using the Transformer.transform() method
predictions = model.transform(test)

# Compute test error
'''evaluator = RegressionEvaluator(labelCol="TargetValue", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print("Root Mean Squared Error (RMSE) on test data = %g\n" % rmse)'''

# Round prediction values before to display them
predictions = predictions.withColumn("prediction", functions.round("prediction", 0).cast("int"))

# Remove encoded columns
predictions = predictions.drop("cr", "d", "t", "features")
#predictions.show(5)


# Output selected states predictions
for state in states:
    # Show state table
    predictions.filter(predictions.Country_Region == state) \
               .show(200)

    # Plot charts
    statePredictions = predictions.filter(predictions.Country_Region == state)
    for i in range(0,2):
        if i == 0:
            dataset = statePredictions.filter(statePredictions.Target == "ConfirmedCases")
            target = " Confirmed Cases"
        else:
            dataset = statePredictions.filter(statePredictions.Target == "Fatalities")
            target = " Fatalities"

        title = state + target.replace(" ", "")

        dates  = dataset.select("Date").collect()
        values = dataset.select("prediction").collect()

        dates  = spark.sparkContext.parallelize(dates)                                               \
                                   .map( lambda r : d.datetime.strptime(r.Date,"%Y-%m-%d").date() ) \
                                   .collect()
        values = spark.sparkContext.parallelize(values)            \
                                   .map( lambda r : r.prediction ) \
                                   .collect()
        #print(dates)
        #print(values)

        plt.figure()

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.plot(dates, values)
        plt.gcf().autofmt_xdate()

        plt.xlabel("Dates")
        plt.ylabel(target)
        plt.title(label=title, fontsize="xx-large")
        #plt.show()

        filename = title + ".pdf"
        print("Saving the predictions plot in ./images as " + filename)
        plt.savefig("./images/" + filename)
