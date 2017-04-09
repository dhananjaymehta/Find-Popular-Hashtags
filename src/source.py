import json
import time
import sys
import networkx as nx
from MyGraph import MyGraph
import matplotlib.pyplot as plt
"""
    Author: Dhananjay Mehta (mehta.dhananjay28@gmail.com)
    Version: v1.0

    -----------------------------------------------------
        	TWITTER ANALYSIS FOR HASHTAG POPULARITY 
    -----------------------------------------------------

    Problem Description:
    -----------------------
    Twitter hashtag graph is a graph connecting all the hashtags that have been mentioned together in a single tweet.
    As there are several tweets with a similar hastag, generting a hashtag graph help to understand following things:
    1. How connected are hashtags in a tweet.
    2. Popularity of a hashtag based on it vertex value.
    3. Top trending topics at a given time.

    Therefore, hashtag graph is super important when it comes to real-time analytics or analysis of real-time events.
    This solution can be extended to other real-time analytics problems.
    Internet of things is the best use case for this.

    CHALLENGE:
    -----------
    Calculate average degree of a vertex in a Twitter hashtag graph for the last 60 seconds, and update this each time
    a new tweet appears. We need to calculate average degree over a 60-second sliding window.

    CORE FEATURES:
    ---------------
    1. Need to analyse the hottest trends in last 60 seconds.
    2. Read the tweets from the input file.
    3. Calculate the degree of a node during the period. Higher degree of a node indicates it is more related to other
    nodes i.e. hashtags and hence more popular.
    4. Top-K topic that constantly appear in the window are selected as top trending topics.

    RESULT -
    ---------
    1. Degree of connectedness in a tweet.
    2. Top trending hashtag every minute.
    3. Top-K trending hashtags in past thirty minutes.
"""


# --------------------------------------------------------
# visualizeHashtagGraph: Visualize hastag graph.
# --------------------------------------------------------
def visualizeHashtagGraph(tweetGraph):
    """
    Visualize hastag graph generated after every 500 tweets.

    :param tweetGraph: dictionary tweetGraph
    :return:
        visualized graph
    """
    hashTagGraph = {}   # graph to be visualized, excluding value of connections
    for tag in tweetGraph:
        hashTagGraph[tag] = [i for i in tweetGraph[tag]]
    
    HashTagGraph = nx.Graph(hashTagGraph)
    nx.draw_spring(HashTagGraph, node_size=300, with_labels=True)    
    plt.show()


# --------------------------------------------------------
# calculateAverageDegree: Check avergae degree of graph.
# --------------------------------------------------------
def calculateAverageDegree(tweetGraph):
    """
    check average degree of graph on each iteration

    :param tweetGraph: dictionary of hashtags and edges connecting to other hastags in 60 seconds window
    :return:
     averageDegree - average degree of hashtags graph.
    """
    try:
        averageDegree = sum(len(tweetGraph[i]) for i in tweetGraph)/float(len(tweetGraph))
    except ZeroDivisionError:
        averageDegree = 0

    return averageDegree


# ---------------------------------------------
# addGraphEdge: add edges to a hashtag graph.
# ---------------------------------------------
def addGraphEdge(hashTags, tweetGraph):
    """
    This function adds edges to the hashtag graph.

    :param hashTags: These hashtags will form edge in the graph
    :param tweetGraph: dictionary of hashtags and number of tweets that formed the edges between hashtags
    :return:
        tweetGraph  - updated graph with edges from hashTags added to current graph
    """
    # for all the Tags in hasTags list
    for Tag in hashTags:    # Node 1
        for tag in hashTags:    # Node 2
            if tag != Tag:
                # if node 1 exist for Tag in current graph
                if Tag in tweetGraph:
                    # check if Node 2 is connected to Node 1
                    if tag in tweetGraph[Tag]:
                        # increase number of tweets that connect Node 1 to Node 2
                        tweetGraph[Tag][tag] += 1
                    # if node 1 does not exist for Tag in current graph
                    else:
                        tweetGraph[Tag][tag] = 1
                # if node 1 do not exist for Tag in current graph
                # Add new Node to graph
                else:
                    tweetGraph[Tag] = {tag: 1}
    return tweetGraph


# ---------------------------------------------------------
# deleteGraphEdge: delete edges from graph for old tweets
# ---------------------------------------------------------
def deleteGraphEdge(hashTags, tweetGraph, timeStampIn60Sec,tweetsIn60Sec):
    """
    This function deletes edges from hashtag graph for tweets older than 60 seconds.

    :param hashTags: Edges from these hashtags will be removed from tweetGraph.
    :param tweetGraph: dictionary of hashtags and number of tweets that formed the edges between hashtags
    :param timeStampIn60Sec: timestamps in last 60 seconds
    :param tweetsIn60Sec: tweets in last 60 seconds
    :return:
        tweetGraph  - updated graph with edges removed for hashTags from tweets older than 60 seconds
    """
    # traverse each node in tweetGraph:
    for tags in tweetsIn60Sec[timeStampIn60Sec[0]]:
        # check if tag is connected to existing tag
        for tag1 in tags:
            for tag2 in tags:
                if tag1 != tag2:
                    tweetGraph[tag1][tag2] -= 1
                    if tweetGraph[tag1][tag2] == 0:
                        tweetGraph[tag1].pop(tag2)
                        if tweetGraph[tag1]=={}:
                            tweetGraph.pop(tag1)
    return tweetGraph


# ---------------------------------------------------------
# extractParsedTweet: Extract hashtags from a file read.
# ---------------------------------------------------------
def extractParsedTweet(parsedTweet):
    """
    This function reads a tweet parsed from input file and extract hastags and created_at field from the tweet.

    :param parsedTweet: tweet parsed from input file.
    :return:
        hashtags - list of hashtags from parsed tweet.
        timestamp - convert extracted created_at field to seconds.
    """
    # Extract hastags:
    hashtags = [tweet['text'] for tweet in parsedTweet['entities']['hashtags']]

    # Extract created_at and convert it to seconds
    # created_at: e.g. : Thu Jun 06 01:15:57 +0000 2013(Date)
    # timestamp: seconds(Integer).
    timeStamp = int(time.mktime(
        time.strptime(parsedTweet['created_at'][0:20] + parsedTweet['created_at'][26:], '%a %b %d %H:%M:%S %Y')))
    return timeStamp, hashtags


# ----------------------------------------------
# updateHashtagGraph: Update the Hashtag Graph
# ----------------------------------------------
def updateHashtagGraph(timeStamp, hashTags, tweetGraph, tweetsIn60Sec, timeStampIn60Sec, maxTimeStamp):
    """
    This function updates hashtag graph with new tweets.
    A hashtag graph contains hashtags from tweets within last 60 seconds.
    Any tweet before 60 seconds is purged.
    There are following conditions that need to be checked before the graph is updated:
        1. If incoming tweet appears in order of time.
        2. If incoming tweet is out of order of time.

    :param timeStamp: timestamp of incoming tweet
    :param hashTags: list of hashtags in incoming tweet
    :param tweetGraph: dictionary of hashtags and number of tweets that formed the edges between hashtags
    :param tweetsIn60Sec: dictionary of tweets in 60 seconds window with timestamp as key
    :param timeStampIn60Sec: list of timestamps in 60 seconds window
    :param maxTimeStamp: timestamp of latest tweet
    :return:
            tweetGraph          -  updated graph with edges representing tweets within 60seconds
            tweetsIn60Sec       -  updated dictionary of tweets in 60 seconds window
            timeStampIn60Sec    -  updated list of timestamps in 60 seconds window
            maxTimeStamp        -  timestamp of latest tweet.
    """
    graph = MyGraph(tweetGraph)  # create Graph object

    # Step 1: check incoming tweet:
    # ------------------------------
    # Condition 1: If tweet arrives in Order
    if timeStamp >= maxTimeStamp:
        # Check if new timeStamp is already in list - timeStampIn60Sec
        if timeStamp != maxTimeStamp:
            # append if not in 60 second list
            timeStampIn60Sec.append(timeStamp)
            # update maxTimeStamp
            maxTimeStamp = timeStamp

        # If timestamp already in tweets60Sec.
        if timeStamp in tweetsIn60Sec:
            # append incoming hashtags at given time
            tweetsIn60Sec[timeStamp].append(hashTags)
        else:
            # add the new hashtag at given time
            tweetsIn60Sec[timeStamp] = [hashTags]

        # Update the Hashtag graph:
        # Step 2: Add edge to tweetGraph only if there are 2 or more hashtags
        # -----------------------------------------------------------------------
        if len(hashTags) > 2:
            tweetGraph = addGraphEdge(hashTags, tweetGraph)

        # Step 3: Delete edge from tweetGraph for tweets that are more than 60 seconds old.
        # -------------------------------------------------------------------------------------
            while maxTimeStamp - timeStampIn60Sec[0] > 60:
                tweetGraph = deleteGraphEdge(hashTags=hashTags,
                                             tweetGraph=tweetGraph,
                                             timeStampIn60Sec=timeStampIn60Sec,
                                             tweetsIn60Sec=tweetsIn60Sec)
                tweetsIn60Sec.pop(timeStampIn60Sec[0])
                timeStampIn60Sec.pop(0)

    # Condition 2: If tweet does not arrive in order:
    else:
        # Check if the tweet is in last 60 Seconds
        if maxTimeStamp - timeStamp <= 60:
            # Check if timestamp is in list of timestamps
            if timeStamp not in timeStampIn60Sec:
                timeStampIn60Sec.append(timeStamp)

            # Check if timeStamp already in tweet60Sec
            if timeStamp in tweetsIn60Sec:
                tweetsIn60Sec[timeStamp].append(hashTags)
            else:
                tweetsIn60Sec[timeStamp] = [hashTags]

            # Update the Hashtag graph:
            # Step 2: Add edge to tweetGraph only if there are 2 or more hashtags
            if len(hashTags) > 2:
                tweetGraph = addGraphEdge(hashTags, tweetGraph)

            # Check if the tweet is older than 60 Seconds - Do Nothing
        else:
            pass

    return tweetGraph, sorted(timeStampIn60Sec), tweetsIn60Sec, maxTimeStamp

# ----------------------------------
# Main section : processing starts
# ----------------------------------
def main(inputFile,outputFile):
    """
    This Program reads through each input tweet in inputFile
    and generate a hashtag graph and calculate the average degree
    of the graph in 60 seconds window. It will write calculated
    degree to outputFile.
    """
    tweetCount = 0          # count the number of tweets
    tweetGraph = {}         # graph structure
    maxTimeStamp = -1       # time stamp of latest tweet
    timeStampIn60Sec = []   # list of timestamps in 60 second time window
    tweetsIn60Sec = {}      # degree of each node in graph

    # Open files to READ and WRITE:
    with open(inputFile, 'r') as tweets, open(outputFile, 'w') as avgDegree:
        # read through each line of input file
        for tweet in tweets:
            try:
                # Stage 1: parse each input tweet
                parsedTweet = json.loads(tweet)

                # extract hastags and timestamp
                timeStamp, hashTags = extractParsedTweet(parsedTweet)

                # Stage 2: Update the Hashtag Graph for new tweet- tweetGraph{}
                tweetGraph, timeStampIn60Sec, tweetsIn60Sec, maxTimeStamp = updateHashtagGraph(timeStamp=timeStamp,
                                                                                               hashTags=hashTags,
                                                                                               tweetGraph=tweetGraph,
                                                                                               tweetsIn60Sec=tweetsIn60Sec,
                                                                                               timeStampIn60Sec=timeStampIn60Sec,
                                                                                               maxTimeStamp=maxTimeStamp)
                
                # Stage 3: Calculate average degree of graph
                averageDegree = calculateAverageDegree(tweetGraph)

                # Stage 4: Write average degree of graph on rolling basis
                avgDegree.write('%.2f\n' % (averageDegree))

                tweetCount += 1

                # Stage 5: Visualize Hashtag Graph:
                # Generate graph after every 500 tweets.
                if tweetCount % 20 == 0:
                   print(tweetGraph)
                   visualizeHashtagGraph(tweetGraph)
                
                if tweetCount > 200: break

            except:
                continue


# Source files
inputFile = '/Users/dhananjay/Desktop/HashtagPopularity/tweetsBig.txt'
outputFile = '/Users/dhananjay/Desktop/HashtagPopularity/results.txt'

if __name__ == "__main__":
    # sys.argv[1] : Input File
    # sys.argv[2] : Output File
    main(sys.argv[1], sys.argv[2])