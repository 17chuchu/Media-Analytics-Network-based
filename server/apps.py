import sys
import tweepy
import threading

from system.TwitterManager import TwitterManager

from system.MongoDBManager import MongoDBManager

from system.CustomStreamListener import CustomStreamListener

from system.ClusteringTweet import ClusteringTweet

from system.UserInteractionGraph import UserInteractionGraph

from system.HashtagInteractionGraph import HashtagInteractionGraph



if __name__ == "__main__":
    if(len(sys.argv) == 1):
        print("Please specify a command.")
    elif(sys.argv[1] == "startstream"):
        TwitterManager.setup()
        MongoDBManager.setup()

        customListener = CustomStreamListener()
        TwitterManager.startStreaming(listener=customListener,track_list=['Sonic Movie','Sonic the Hedgehog', 'pokemon','Pokemon','doom eternal','Doom Eternal','Animal Crossing','animal crossing'])
    
    elif(sys.argv[1] == "startstreamrest"):
        TwitterManager.setup()
        MongoDBManager.setup()
        
        TwitterManager.startGettingUserMentionsTimeline()
        customListener = CustomStreamListener()
        TwitterManager.startStreaming(listener=customListener,track_list=['Sonic Movie','Sonic the Hedgehog', 'pokemon','Pokemon','doom eternal','Doom Eternal','Animal Crossing','animal crossing'])

    elif(sys.argv[1] == "startgettingreplystatus"):
        TwitterManager.setup()
        MongoDBManager.setup()

        HashtagInteractionGraph.startGettingReplyStatus()
    
    elif(sys.argv[1] == "showssegraph"):
        MongoDBManager.setup()
        if(len(sys.argv) >= 3):
            if(str(sys.argv[2].isnumeric())):
                if(int(sys.argv[2]) > 0):
                    ClusteringTweet.show_optimised_cluster_graph([i for i in range(1,int(sys.argv[2]) + 1)])
        ClusteringTweet.show_optimised_cluster_graph([i for i in range(1,40 + 1)])

    elif(sys.argv[1] == "clustering"):
        MongoDBManager.setup()
        if(len(sys.argv) >= 3):
            if(str(sys.argv[2].isnumeric())):
                if(int(sys.argv[2]) > 0):
                    if(len(sys.argv) >= 4):
                        if(str(sys.argv[3].isnumeric())):
                            if(int(sys.argv[3]) > 0):
                                ClusteringTweet.run(max_text_size= int(sys.argv[2]),group_num=int(sys.argv[3]))
                    else:
                        ClusteringTweet.run(max_text_size= int(sys.argv[2]),group_num=29)
        else:
            ClusteringTweet.run(max_text_size= 0,group_num=29)
        ClusteringTweet.print_info()

    elif(sys.argv[1] == "clusteringandextract"):
        MongoDBManager.setup()
        if(len(sys.argv) >= 3):
            if(str(sys.argv[2].isnumeric())):
                if(int(sys.argv[2]) > 0):
                    if(len(sys.argv) >= 4):
                        if(str(sys.argv[3].isnumeric())):
                            if(int(sys.argv[3]) > 0):
                                ClusteringTweet.run(max_text_size= int(sys.argv[2]),group_num=int(sys.argv[3]))
                    else:
                        ClusteringTweet.run(max_text_size= int(sys.argv[2]),group_num=29)
        else:
            ClusteringTweet.run(max_text_size= 0,group_num=29)

        UserInteractionGraph.constructUserStatistic()
        UserInteractionGraph.printStatistics()

    elif(sys.argv[1] == "clusteringandextracthashtag"):
        MongoDBManager.setup()
        if(len(sys.argv) >= 3):
            if(str(sys.argv[2].isnumeric())):
                if(int(sys.argv[2]) > 0):
                    if(len(sys.argv) >= 4):
                        if(str(sys.argv[3].isnumeric())):
                            if(int(sys.argv[3]) > 0):
                                ClusteringTweet.run(max_text_size= int(sys.argv[2]),group_num=int(sys.argv[3]))
                    else:
                        ClusteringTweet.run(max_text_size= int(sys.argv[2]),group_num=29)
        else:
            ClusteringTweet.run(max_text_size= 0,group_num=29)

        HashtagInteractionGraph.constructHashTagStatistic()
        HashtagInteractionGraph.printStatistics()
