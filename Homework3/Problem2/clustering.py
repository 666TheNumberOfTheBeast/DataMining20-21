import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn import metrics

from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt

import time
import os

# Save plot
def savefig(filename, plotType):
    path = "./images/"
    try:
        os.mkdir(path)
        print("Directory " + path + " created")
    except FileExistsError:
        pass
    except:
        print("Error in creating the directory " + path)

    print("Saving the " + plotType + " plot in " + path + " as " + filename)
    plt.savefig(path + filename)


def elbowMethod(X, figTitle):
    # Use distortions and inertias to find the most suitable k
    distortions = []
    inertias    = []
    mapping1 = {}
    mapping2 = {}
    K = range(1, 10)

    for k in K:
    	# Building and fitting the model
    	kmeanModel = KMeans(n_clusters=k).fit(X)
    	kmeanModel.fit(X)

    	# Calculating the values of the distortion and inertia
    	distortion = sum(np.min(cdist(X, kmeanModel.cluster_centers_, "euclidean"), axis=1)) / X.shape[0]
    	inertia    = kmeanModel.inertia_

    	# Append distortion and inertia to the corresponding lists
    	distortions.append(distortion)
    	inertias.append(inertia)

        # Append distortion and inertia to the corresponding mappings
    	mapping1[k] = distortion
    	mapping2[k] = inertia

    # Using the different values of Distortion
    print("\nDistortions:")
    for key,val in mapping1.items():
        print(str(key) + ": " + str(val))

    plt.plot(K, distortions, "bx-")
    plt.xlabel("Values of K")
    plt.ylabel("Distortion")
    plt.title("The Elbow Method using Distortion", fontsize="xx-large")
    #plt.show()

    savefig(figTitle, "elbow method")

    # Using the different values of Inertia
    '''print("\nInertias:")
    for key,val in mapping2.items():
        print(str(key) + ": " + str(val))

    plt.plot(K, inertias, "bx-")
    plt.xlabel("Values of K")
    plt.ylabel("Inertia")
    plt.title("The Elbow Method using Inertia", fontsize="xx-large")
    plt.show()'''


    # To determine the optimal number of clusters, we have to select the value of k at the “elbow”
    # i.e. the point after which the distortion/inertia start decreasing in a linear fashion.

# Return a pandas dataframe appending the clustering vector to the data matrix
def getResult(X, clustering, columns):
    # Create matrix nx1 from clustering
    clustersMatrix = [ [x] for x in clustering ]

    # Add clustering column to the data matrix
    X = np.hstack( (X, clustersMatrix) )

    # Create a Pandas dataframe similar to the initial one
    return pd.DataFrame(X, columns=columns)

# Draw resulting chart with axis longitude and latitude and colored clusters
def drawResult(X, title, colors):
    mappedClusters = X["cluster"].apply( lambda x : colors[x] )
    plt.plot()
    plt.scatter(X["longitude"], X["latitude"], c=mappedClusters)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(label=title, fontsize="xx-large")
    #plt.show()

    filename = title + " scatter.pdf"
    savefig(filename, "clustering scatter")
    plt.clf()

    plt.hist(mappedClusters)
    plt.xlabel("Clusters")
    plt.ylabel("Houses")
    plt.title(title, fontsize="xx-large")
    #plt.show()

    filename = title + " hist.pdf"
    savefig(filename, "clustering hist")
    plt.clf()

'''def printDifferentCharts(X, title):
    plt.hist(X)
    plt.title(title, fontsize="xx-large")
    plt.show()

    # Get a Gaussian distribution using sqrt
    plt.hist( np.sqrt(X) )
    plt.title("sqrt " + title, fontsize="xx-large")
    plt.show()

    # Get a Gaussian distribution using log
    plt.hist( np.log(X) )
    plt.title("log " + title, fontsize="xx-large")
    plt.show()'''

def getCurrentMs():
    return int( round(time.time() * 1000) )


if __name__ == '__main__':
    # Houses file
    filename  = "./housing.csv"

    # Load data
    dataframe = pd.read_csv(filename, sep=",", header=0)
    print("\nData:\n", dataframe)

    # Common variables for Raw Data and Feature Engineered Data
    seed   = 0
    colors = { 0: "red", 1: "blue", 2: "green", 3: "orange", 4: "yellow" }

    #pd.set_option('display.max_rows', None, 'display.max_columns', None)

    ''' ******** RAW DATA ******** '''
    # Working on raw data, I need to remove categorical columns
    dataframeRaw = dataframe.drop(columns="ocean_proximity")

    # Return a Numpy representation of the DataFrame
    npMatrix = dataframeRaw.values

    print("\nDoes Data contain a missing value?\t", np.any(np.isnan(npMatrix)))
    print("Does Data contain all finite values?\t", np.all(np.isfinite(npMatrix)))

    # Remove missing values (i.e. drop a row if contains a missing value)
    print("\nRemoving rows with missing values...")
    dataframeRaw = dataframeRaw.dropna()

    # Return a Numpy representation of the DataFrame
    npMatrix = dataframeRaw.values
    #print("\nNumpy representation of the data:\n", npMatrix)

    print("\nDoes Data contain a missing value?\t", np.any(np.isnan(npMatrix)))
    print("Does Data contain all finite values?\t", np.all(np.isfinite(npMatrix)))

    # Use the elbow method to find the most suitable number of clusters k
    #elbowMethod(npMatrix, "Elbow method Raw Data.pdf")
    # It seems to be k=5

    print("\nClustering...")
    previous = getCurrentMs()
    kmeans = KMeans(n_clusters=5, random_state=seed).fit(npMatrix)
    elapsedRaw = getCurrentMs() - previous

    print("\nSilhouette Score Raw Data: ", metrics.silhouette_score(npMatrix, kmeans.labels_, metric="euclidean") )

    # Get resulting pandas dataframe with the following columns
    columns = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms", \
               "population", "households", "median_income", "median_house_value", "cluster"]
    res = getResult(npMatrix, kmeans.labels_, columns)
    print("\nResult:\n", res)

    print();
    drawResult(res, "Raw data", colors)


    ''' ******** FEATURE ENGINEERING DATA ******** '''
    #print("\nData types:\n", dataframe.dtypes)

    print("\nImputating rows with missing values")
    # Fill the categorical column with "Other"
    dataframe.ocean_proximity.fillna("Other", inplace=True)

    # Fill missing values with 0
    #dataframe.fillna(0, inplace=True)
    # Fill missing values with medians of the columns
    dataframe.fillna(dataframe.median(), inplace=True)
    # Remove missing values (i.e. drop a row if contains a missing value)
    #dataframe.dropna(inplace=True)
    #print("\nRemoved rows with missing values")


    print("\nEncoding categorical columns...")
    # Encode ocean_proximity values as a one-hot numeric array
    col = pd.get_dummies(dataframe.ocean_proximity, prefix="ocean_proximity")

    # Remove categorical column (will replace it with one-hot encoding)
    dataframe = dataframe.drop(columns="ocean_proximity")

    # Add one-hot encoded column to the dataframe
    dataframe = pd.concat([dataframe, col], axis=1)
    #print("\nEncoded categorical data:\n", dataframe)

    print("\nRemoving outliers...")
    # Drop the outlier rows using standard deviation
    factor = 3
    for col in dataframe:
        # Skip categorical encodings
        if col.startswith("ocean_proximity"):
            break

        mean = dataframe[col].mean()
        std  = dataframe[col].std()

        upperBound = mean + std * factor
        lowerBound = mean - std * factor

        dataframe = dataframe[(dataframe[col] > lowerBound) & (dataframe[col] < upperBound)]
        #print("Removed outliers from " + col + ":\n", dataframe)

    #print("\nRemoved outliers:\n", dataframe)

    print("\nApproximating data distribution to normal...")
    for col in dataframe:
        # Skip longitude and latitude columns
        if col == "longitude" or col == "latitude":
            continue
        # Skip categorical encodings
        if col.startswith("ocean_proximity"):
            break

        #printDifferentCharts(dataframe[col], colName)
        dataframe[col] = dataframe[col].transform(np.log)

    print("\nNormalizing data...")
    for col in dataframe:
        # Skip categorical encodings
        if col.startswith("ocean_proximity"):
            break

        min = dataframe[col].min()
        dataframe[col] = (dataframe[col] - min ) / (dataframe[col].max() - min)

    #print("\nNormalized data:\n", dataframe)

    # Return a Numpy representation of the DataFrame
    npMatrix = dataframe.values

    # Use the elbow method to find the most suitable number of clusters k
    #elbowMethod(npMatrix, "Elbow method Feature Engineered Data.pdf")
    # It seems to be k=4

    print("\nClustering...")
    previous = getCurrentMs()
    kmeans = KMeans(n_clusters=4, random_state=seed).fit(npMatrix)
    elapsedFE = getCurrentMs() - previous

    print("\nSilhouette Score: ", metrics.silhouette_score(npMatrix, kmeans.labels_, metric="euclidean") )

    # Get resulting pandas dataframe with the following columns
    columns = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms", \
               "population", "households", "median_income", "median_house_value", "ocean_proximity_<1H OCEAN", \
               "ocean_proximity_INLAND", "ocean_proximity_ISLAND", "ocean_proximity_NEAR BAY", \
               "ocean_proximity_NEAR OCEAN", "cluster"]
    res = getResult(npMatrix, kmeans.labels_, columns)
    print("\nResult:\n", res)

    print();
    drawResult(res, "Feature engineered data", colors)

    print("\nElapsed time Raw data: " + str(elapsedRaw) + " ms vs Elapsed time feature engineering: " + str(elapsedFE) + " ms")
