import collections
import time

import matplotlib.pyplot as plt
import networkx as nx

import numpy as np

import tweepy

from system.MongoDBManager import MongoDBManager
from system.ClusteringTweet import ClusteringTweet
from system.TwitterManager import TwitterManager



class HashtagInteractionGraph:

    adjacencyMatrixSeperatedByGroup = {}
    nxGraphSeperatedByGroup = {}

    nxGraphGeneral = nx.DiGraph()

    @staticmethod
    def startGettingReplyStatus():
        api = tweepy.API(TwitterManager.auth)
        all_reply_status_id = []

        all_tweet = {}
        for tweet in MongoDBManager.collection.find():
            all_tweet[tweet["id_str"]] = tweet
        for tweet in MongoDBManager.timeline.find():
            all_tweet[tweet["id_str"]] = tweet


        for tweet in all_tweet.values():

            if(not (tweet["in_reply_to_user_id_str"] == None or tweet["in_reply_to_user_id_str"] == "null")):
                all_reply_status_id.append(tweet["in_reply_to_user_id_str"])
        print("Getting",len(all_reply_status_id),"number of reply.")
        index = 0
        for i in range(len(all_reply_status_id[::100])):
            index += 100
            response = api.statuses_lookup(id_ = all_reply_status_id[index: index + 100])

            for post in response:
                MongoDBManager.insertReplyStatus(post._json)
            print(index)
            time.sleep(1)

    
    @staticmethod
    def printStatistics():
        # Reply graph Traid

        print()
        for i in range(ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0]):
            tabletitleString = "|Group Number|Interaction Type|"
            tabletitleBottom = "|:------------:|:------------:|"
            for triadic_type in (nx.triadic_census(HashtagInteractionGraph.nxGraphSeperatedByGroup[1]["retweet"])).keys():
                tabletitleString += triadic_type + "|"
                tabletitleBottom += ":-----------------:|"

            print(tabletitleString)
            print(tabletitleBottom)
            
            tabletitlerow = "|" + str(i) + "|retweet|"
            triadic_cencus = nx.triadic_census(HashtagInteractionGraph.nxGraphSeperatedByGroup[i]["retweet"]).values()
            for value in triadic_cencus:
                tabletitlerow += str(value) + "|"
            print(tabletitlerow)
            
            tabletitlerow = "|" + str(i) + "|reply|"
            triadic_cencus = nx.triadic_census(HashtagInteractionGraph.nxGraphSeperatedByGroup[i]["reply"]).values()
            for value in triadic_cencus:
                tabletitlerow += str(value) + "|"
            print(tabletitlerow)
            print()
        print()

    @staticmethod
    def constructHashTagStatistic():
        #print(ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0])
        all_tweet = {}
        for tweet in MongoDBManager.collection.find():
            all_tweet[tweet["id_str"]] = tweet
        for tweet in MongoDBManager.timeline.find():
            all_tweet[tweet["id_str"]] = tweet
        for tweet in MongoDBManager.replystatus.find():
            all_tweet[tweet["id_str"]] = tweet

        HashtagInteractionGraph.constructHashTagInteractionGraphGeneral(all_tweet)
        print("Constructed Group: 0")

        for i in range(ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0]):
            print("Constructed Group:", i + 1)
            HashtagInteractionGraph.constructHashTagInteractionGraph(all_tweet,i + 1)

    @staticmethod
    def constructHashTagInteractionGraph(all_tweet,gnum):

        adjacencyMatrix = {"retweet": {},"reply": {}}
        nxGraph = {"retweet": nx.DiGraph(),"reply": nx.DiGraph()}

        tweetData = ClusteringTweet.tweetDataFrame.copy()
        tweetData.where(tweetData["group"] == gnum, inplace = True)

        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]

            tweets_user_id = tweet["id_str"]
            hashtag_list = tweet["entities"]["hashtags"]

            for hashtag in hashtag_list:
                hashtag = hashtag["text"]
                if(hashtag not in list(adjacencyMatrix["retweet"].keys())):
                    adjacencyMatrix["retweet"][hashtag] = {}
                    nxGraph["retweet"].add_node(hashtag)
                if(hashtag not in list(adjacencyMatrix["reply"].keys())):
                    adjacencyMatrix["reply"][hashtag] = {}
                    nxGraph["reply"].add_node(hashtag)


        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]

            hashtag_list = tweet["entities"]["hashtags"]

            #first order tie direction
            #second order tie no direction

            if("retweeted_status" in tweet):
                retweeted_hashtag_list = tweet["retweeted_status"]["entities"]["hashtags"]

                for retweeted_hashtag in retweeted_hashtag_list:
                    retweeted_hashtag = retweeted_hashtag["text"]
                    if(not nxGraph["retweet"].has_node(retweeted_hashtag)):
                        nxGraph["retweet"].add_node(retweeted_hashtag)

                    for hashtag in hashtag_list:
                        hashtag = hashtag["text"]
                        nxGraph["retweet"].add_edge(hashtag,retweeted_hashtag)
                        nxGraph["retweet"].add_edge(retweeted_hashtag,hashtag)

                        if(retweeted_hashtag in adjacencyMatrix["retweet"][hashtag].keys()):
                                adjacencyMatrix["retweet"][hashtag][retweeted_hashtag] += 1
                        else:
                            adjacencyMatrix["retweet"][hashtag][retweeted_hashtag] = 1

            if(not (tweet["in_reply_to_user_id_str"] == None or tweet["in_reply_to_user_id_str"] == "null")):
                if(tweet["in_reply_to_user_id_str"] in all_tweet):
                    reply_hashtag_list = all_tweet[tweet["in_reply_to_user_id_str"]]["entities"]["hashtags"]

                    for reply_hashtag in reply_hashtag_list:
                        reply_hashtag = reply_hashtag["text"]
                        if(not nxGraph["reply"].has_node(reply_hashtag)):
                            nxGraph["reply"].add_node(reply_hashtag)
                        
                        for hashtag in hashtag_list:
                            hashtag = hashtag["text"]
                            nxGraph["reply"].add_edge(hashtag,reply_hashtag)
                            nxGraph["reply"].add_edge(reply_hashtag,hashtag)

                            if(reply_hashtag in adjacencyMatrix["reply"][hashtag].keys()):
                                adjacencyMatrix["reply"][hashtag][reply_hashtag] += 1
                            else:
                                adjacencyMatrix["reply"][hashtag][reply_hashtag] = 1

        HashtagInteractionGraph.nxGraphSeperatedByGroup[gnum] = nxGraph


    @staticmethod
    def constructHashTagInteractionGraphGeneral(all_tweet):

        adjacencyMatrix = {"retweet": {},"reply": {}}
        nxGraph = {"retweet": nx.DiGraph(),"reply": nx.DiGraph()}

        tweetData = ClusteringTweet.tweetDataFrame.copy()

        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]

            tweets_user_id = tweet["id_str"]
            hashtag_list = tweet["entities"]["hashtags"]

            for hashtag in hashtag_list:
                hashtag = hashtag["text"]
                if(hashtag not in adjacencyMatrix["retweet"].keys()):
                    adjacencyMatrix["retweet"][hashtag] = {}
                    nxGraph["retweet"].add_node(hashtag)
                if(hashtag not in adjacencyMatrix["reply"].keys()):
                    adjacencyMatrix["reply"][hashtag] = {}
                    nxGraph["reply"].add_node(hashtag)


        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]

            hashtag_list = tweet["entities"]["hashtags"]

            #first order tie direction
            #second order tie no direction

            if("retweeted_status" in tweet):
                retweeted_hashtag_list = tweet["retweeted_status"]["entities"]["hashtags"]

                for retweeted_hashtag in retweeted_hashtag_list:
                    retweeted_hashtag = retweeted_hashtag["text"]
                    if(not nxGraph["retweet"].has_node(retweeted_hashtag)):
                        nxGraph["retweet"].add_node(retweeted_hashtag)

                    for hashtag in hashtag_list:
                        hashtag = hashtag["text"]
                        nxGraph["retweet"].add_edge(hashtag,retweeted_hashtag)
                        nxGraph["retweet"].add_edge(retweeted_hashtag,hashtag)

                        if(retweeted_hashtag in adjacencyMatrix["retweet"][hashtag].keys()):
                                adjacencyMatrix["retweet"][hashtag][retweeted_hashtag] += 1
                        else:
                            adjacencyMatrix["retweet"][hashtag][retweeted_hashtag] = 1

            if(not (tweet["in_reply_to_user_id_str"] == None or tweet["in_reply_to_user_id_str"] == "null")):
                if(tweet["in_reply_to_user_id_str"] in all_tweet):
                    
                    reply_hashtag_list = all_tweet[tweet["in_reply_to_user_id_str"]]["entities"]["hashtags"]
                    
                    for reply_hashtag in reply_hashtag_list:
                        reply_hashtag = reply_hashtag["text"]
                        if(not nxGraph["reply"].has_node(reply_hashtag)):
                            nxGraph["reply"].add_node(reply_hashtag)
                        
                        for hashtag in hashtag_list:
                            hashtag = hashtag["text"]
                            nxGraph["reply"].add_edge(hashtag,reply_hashtag)
                            nxGraph["reply"].add_edge(reply_hashtag,hashtag)


                            if(reply_hashtag in adjacencyMatrix["reply"][hashtag].keys()):
                                adjacencyMatrix["reply"][hashtag][reply_hashtag] += 1
                            else:
                                adjacencyMatrix["reply"][hashtag][reply_hashtag] = 1

        HashtagInteractionGraph.nxGraphSeperatedByGroup[0] = nxGraph










