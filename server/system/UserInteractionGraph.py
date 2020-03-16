import collections

import matplotlib.pyplot as plt
import networkx as nx

import numpy as np

from System.MongoDBManager import MongoDBManager
from System.ClusteringTweet import ClusteringTweet



class UserInteractionGraph:

    adjacencyMatrixSeperatedByGroup = {}
    nxGraphSeperatedByGroup = {}
    edgesByGroup = {}

    nxGraphGeneral = {"mention": nx.DiGraph(),"retweet": nx.DiGraph(),"reply": nx.DiGraph()}
    edgesGeneral = {"mention": {},"retweet": {},"reply": {}}

    @staticmethod
    def printStatistics():
        # Reply graph Traid

        print()
        for i in range(ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0]):
            tabletitleString = "|Group Number|Interaction Type|"
            tabletitleBottom = "|:------------:|:------------:|"
            for triadic_type in (nx.triadic_census(UserInteractionGraph.nxGraphSeperatedByGroup[1]["mention"])).keys():
                tabletitleString += triadic_type + "|"
                tabletitleBottom += ":-----------------:|"

            print(tabletitleString)
            print(tabletitleBottom)
            tabletitlerow = "|" + str(i) + "|mention|"
            triadic_cencus = nx.triadic_census(UserInteractionGraph.nxGraphSeperatedByGroup[i]["mention"]).values()
            for value in triadic_cencus:
                tabletitlerow += str(value) + "|"
            print(tabletitlerow)
            
            tabletitlerow = "|" + str(i) + "|retweet|"
            triadic_cencus = nx.triadic_census(UserInteractionGraph.nxGraphSeperatedByGroup[i]["retweet"]).values()
            for value in triadic_cencus:
                tabletitlerow += str(value) + "|"
            print(tabletitlerow)
            
            tabletitlerow = "|" + str(i) + "|reply|"
            triadic_cencus = nx.triadic_census(UserInteractionGraph.nxGraphSeperatedByGroup[i]["reply"]).values()
            for value in triadic_cencus:
                tabletitlerow += str(value) + "|"
            print(tabletitlerow)
            print()


            tabletitleString = "|Group Number|Interaction Type|Strong Tie|Weak Tie|"
            tabletitleBottom = "|:------------:|:------------:|:------------:|:------------:|"
            print(tabletitleString)
            print(tabletitleBottom)

            mention_dict = UserInteractionGraph.edgesByGroup[i]["mention"]
            mention_np = np.array(list(mention_dict.values()))
            print("|" + str(i) + "|mention|" + str(np.count_nonzero(mention_np > 1)) + "|" + str(np.count_nonzero(mention_np == 1)) + "|")
                
            
            retweet_dict = UserInteractionGraph.edgesByGroup[i]["retweet"]
            retweet_np = np.array(list(retweet_dict.values()))
            print("|" + str(i) + "|retweet|" + str(np.count_nonzero(retweet_np > 1)) + "|" + str(np.count_nonzero(retweet_np == 1)) + "|")
            

            reply_dict = UserInteractionGraph.edgesByGroup[i]["reply"]
            reply_np = np.array(list(reply_dict.values()))
            print("|" + str(i) + "|reply|" + str(np.count_nonzero(reply_np > 1)) + "|" + str(np.count_nonzero(reply_np == 1)) + "|")

            print()
        print()




    @staticmethod
    def constructUserStatistic():
        #print(ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0])
        all_tweet = {}
        for tweet in MongoDBManager.collection.find():
            all_tweet[tweet["id_str"]] = tweet
        for tweet in MongoDBManager.timeline.find():
            all_tweet[tweet["id_str"]] = tweet

        UserInteractionGraph.constructAdjacencyMatrixForGeneralData(all_tweet)
        print("Constructed Group: 0")

        for i in range(ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0]):
            print("Constructed Group:", i + 1)
            UserInteractionGraph.constructAdjacencyMatrixForGroup(all_tweet,i + 1)

    @staticmethod
    def constructAdjacencyMatrixForGeneralData(all_tweet):
        adjacencyMatrix = {"mention": {},"retweet": {},"reply": {}}
        
        tweetData = ClusteringTweet.tweetDataFrame.copy()

        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]

            tweets_user_id = tweet["id_str"]

            if(tweets_user_id not in adjacencyMatrix["mention"].keys()):
                adjacencyMatrix["mention"][tweets_user_id] = {}
                UserInteractionGraph.nxGraphGeneral["mention"].add_node(tweets_user_id)
            if(tweets_user_id not in adjacencyMatrix["retweet"].keys()):
                adjacencyMatrix["retweet"][tweets_user_id] = {}
                UserInteractionGraph.nxGraphGeneral["retweet"].add_node(tweets_user_id)
            if(tweets_user_id not in adjacencyMatrix["reply"].keys()):
                adjacencyMatrix["reply"][tweets_user_id] = {}
                UserInteractionGraph.nxGraphGeneral["reply"].add_node(tweets_user_id)


        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]
            tweets_user_id = tweet["id_str"]

            #first order tie direction
            #second order tie no direction

            mentions = tweet["entities"]["user_mentions"]
            for ment in mentions:
                mention_user_id = ment["id_str"]

                if(not UserInteractionGraph.nxGraphGeneral["mention"].has_node(mention_user_id)):
                    UserInteractionGraph.nxGraphGeneral["mention"].add_node(mention_user_id)

                if((tweets_user_id + mention_user_id not in UserInteractionGraph.edgesGeneral) and (mention_user_id + tweets_user_id not in UserInteractionGraph.edgesGeneral)):
                    UserInteractionGraph.edgesGeneral["mention"][tweets_user_id + mention_user_id] = 1
                elif(tweets_user_id + mention_user_id in UserInteractionGraph.edgesGeneral):
                    UserInteractionGraph.edgesGeneral["mention"][tweets_user_id + mention_user_id] += 1
                elif(mention_user_id + tweets_user_id in UserInteractionGraph.edgesGeneral):
                    UserInteractionGraph.edgesGeneral["mention"][mention_user_id + tweets_user_id] += 1

                UserInteractionGraph.nxGraphGeneral["mention"].add_edge(tweets_user_id,mention_user_id)
                if(mention_user_id in adjacencyMatrix["mention"][tweets_user_id].keys()):
                    adjacencyMatrix["mention"][tweets_user_id][mention_user_id] += 1
                else:
                    adjacencyMatrix["mention"][tweets_user_id][mention_user_id] = 1
            
            if("retweeted_status" in tweet):
                retweet_user_id = tweet["retweeted_status"]["user"]["id_str"]

                if(not UserInteractionGraph.nxGraphGeneral["retweet"].has_node(retweet_user_id)):
                    UserInteractionGraph.nxGraphGeneral["retweet"].add_node(retweet_user_id)
                
                UserInteractionGraph.nxGraphGeneral["retweet"].add_edge(tweets_user_id,retweet_user_id)
                
                if((tweets_user_id + retweet_user_id not in UserInteractionGraph.edgesGeneral) and (retweet_user_id + tweets_user_id not in UserInteractionGraph.edgesGeneral)):
                    UserInteractionGraph.edgesGeneral["retweet"][tweets_user_id + retweet_user_id] = 1
                elif(tweets_user_id + retweet_user_id in UserInteractionGraph.edgesGeneral):
                    UserInteractionGraph.edgesGeneral["retweet"][tweets_user_id + retweet_user_id] += 1
                elif(retweet_user_id + tweets_user_id in UserInteractionGraph.edgesGeneral):
                    UserInteractionGraph.edgesGeneral["retweet"][retweet_user_id + tweets_user_id] += 1

                if(retweet_user_id in adjacencyMatrix["retweet"][tweets_user_id].keys()):
                        adjacencyMatrix["retweet"][tweets_user_id][retweet_user_id] += 1
                else:
                    adjacencyMatrix["retweet"][tweets_user_id][retweet_user_id] = 1

            if(not (tweet["in_reply_to_user_id_str"] == None or tweet["in_reply_to_user_id_str"] == "null")):
                reply_user_id = tweet["in_reply_to_user_id_str"]

                if(not UserInteractionGraph.nxGraphGeneral["reply"].has_node(reply_user_id)):
                    UserInteractionGraph.nxGraphGeneral["reply"].add_node(tweet["in_reply_to_user_id_str"])
                
                UserInteractionGraph.nxGraphGeneral["reply"].add_edge(tweets_user_id,reply_user_id)

                if((tweets_user_id + reply_user_id not in UserInteractionGraph.edgesGeneral) and (reply_user_id + tweets_user_id not in UserInteractionGraph.edgesGeneral)):
                    UserInteractionGraph.edgesGeneral["reply"][tweets_user_id + reply_user_id] = 1
                elif(tweets_user_id + reply_user_id in UserInteractionGraph.edgesGeneral):
                    UserInteractionGraph.edgesGeneral["reply"][tweets_user_id + reply_user_id] += 1
                elif(reply_user_id + tweets_user_id in UserInteractionGraph.edgesGeneral):
                    UserInteractionGraph.edgesGeneral["reply"][reply_user_id + tweets_user_id] += 1

                if(reply_user_id in adjacencyMatrix["reply"][tweets_user_id].keys()):
                    adjacencyMatrix["reply"][tweets_user_id][reply_user_id] += 1
                else:
                    adjacencyMatrix["reply"][tweets_user_id][reply_user_id] = 1

        UserInteractionGraph.nxGraphSeperatedByGroup[0] = UserInteractionGraph.nxGraphGeneral
        UserInteractionGraph.edgesByGroup[0] = UserInteractionGraph.edgesGeneral


    @staticmethod
    def constructAdjacencyMatrixForGroup(all_tweet,gnum):

        adjacencyMatrix = {"mention": {},"retweet": {},"reply": {}}
        nxGraph = {"mention": nx.DiGraph(),"retweet": nx.DiGraph(),"reply": nx.DiGraph()}
        edgecount = {"mention": {},"retweet": {},"reply": {}}

        tweetData = ClusteringTweet.tweetDataFrame.copy()
        tweetData.where(tweetData["group"] == gnum, inplace = True)

        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]

            tweets_user_id = tweet["id_str"]

            if(tweets_user_id not in adjacencyMatrix["mention"].keys()):
                adjacencyMatrix["mention"][tweets_user_id] = {}
                nxGraph["mention"].add_node(tweets_user_id)
            if(tweets_user_id not in adjacencyMatrix["retweet"].keys()):
                adjacencyMatrix["retweet"][tweets_user_id] = {}
                nxGraph["retweet"].add_node(tweets_user_id)
            if(tweets_user_id not in adjacencyMatrix["reply"].keys()):
                adjacencyMatrix["reply"][tweets_user_id] = {}
                nxGraph["reply"].add_node(tweets_user_id)


        for index, row in tweetData.dropna().iterrows():
            tweet = all_tweet[row['id']]
            tweets_user_id = tweet["id_str"]

            #first order tie direction
            #second order tie no direction

            mentions = tweet["entities"]["user_mentions"]
            for ment in mentions:
                mention_user_id = ment["id_str"]

                if(not nxGraph["mention"].has_node(mention_user_id)):
                    nxGraph["mention"].add_node(mention_user_id)

                if((tweets_user_id + mention_user_id not in edgecount) and (mention_user_id + tweets_user_id not in edgecount)):
                    edgecount["mention"][tweets_user_id + mention_user_id] = 1
                elif(tweets_user_id + mention_user_id in edgecount):
                    edgecount["mention"][tweets_user_id + mention_user_id] += 1
                elif(mention_user_id + tweets_user_id in edgecount):
                    edgecount["mention"][mention_user_id + tweets_user_id] += 1

                nxGraph["mention"].add_edge(tweets_user_id,mention_user_id)
                if(mention_user_id in adjacencyMatrix["mention"][tweets_user_id].keys()):
                    adjacencyMatrix["mention"][tweets_user_id][mention_user_id] += 1
                else:
                    adjacencyMatrix["mention"][tweets_user_id][mention_user_id] = 1
            
            if("retweeted_status" in tweet):
                retweet_user_id = tweet["retweeted_status"]["user"]["id_str"]

                if(not nxGraph["retweet"].has_node(retweet_user_id)):
                    nxGraph["retweet"].add_node(retweet_user_id)
                
                nxGraph["retweet"].add_edge(tweets_user_id,retweet_user_id)
                
                if((tweets_user_id + retweet_user_id not in edgecount) and (retweet_user_id + tweets_user_id not in edgecount)):
                    edgecount["retweet"][tweets_user_id + retweet_user_id] = 1
                elif(tweets_user_id + retweet_user_id in edgecount):
                    edgecount["retweet"][tweets_user_id + retweet_user_id] += 1
                elif(retweet_user_id + tweets_user_id in edgecount):
                    edgecount["retweet"][retweet_user_id + tweets_user_id] += 1

                if(retweet_user_id in adjacencyMatrix["retweet"][tweets_user_id].keys()):
                        adjacencyMatrix["retweet"][tweets_user_id][retweet_user_id] += 1
                else:
                    adjacencyMatrix["retweet"][tweets_user_id][retweet_user_id] = 1

            if(not (tweet["in_reply_to_user_id_str"] == None or tweet["in_reply_to_user_id_str"] == "null")):
                reply_user_id = tweet["in_reply_to_user_id_str"]

                if(not nxGraph["reply"].has_node(reply_user_id)):
                    nxGraph["reply"].add_node(tweet["in_reply_to_user_id_str"])
                
                nxGraph["reply"].add_edge(tweets_user_id,reply_user_id)

                if((tweets_user_id + reply_user_id not in edgecount) and (reply_user_id + tweets_user_id not in edgecount)):
                    edgecount["reply"][tweets_user_id + reply_user_id] = 1
                elif(tweets_user_id + reply_user_id in edgecount):
                    edgecount["reply"][tweets_user_id + reply_user_id] += 1
                elif(reply_user_id + tweets_user_id in edgecount):
                    edgecount["reply"][reply_user_id + tweets_user_id] += 1

                if(reply_user_id in adjacencyMatrix["reply"][tweets_user_id].keys()):
                    adjacencyMatrix["reply"][tweets_user_id][reply_user_id] += 1
                else:
                    adjacencyMatrix["reply"][tweets_user_id][reply_user_id] = 1

        UserInteractionGraph.nxGraphSeperatedByGroup[gnum] = nxGraph
        UserInteractionGraph.adjacencyMatrixSeperatedByGroup[gnum] = adjacencyMatrix
        UserInteractionGraph.edgesByGroup[gnum] = edgecount
