import json
import datetime
import uuid
import datetime
import time
import requests

import nltk

import pymongo

import tweepy

from django.db import connection

class MongoDBManager:

    client = None
    db = None
    collection = None
    mention = None
    timeline = None
    user = None
    entities = None
    replystatus = None

    gottentimelineuser = None

    @staticmethod
    def setup():
        MongoDBManager.client = pymongo.MongoClient("mongodb://localhost:27017/")
        MongoDBManager.db = MongoDBManager.client["socialmediadatabase"]
        MongoDBManager.collection = MongoDBManager.db["socialmediacollection"]
        MongoDBManager.mention = MongoDBManager.db["socialmediamention"]
        MongoDBManager.timeline = MongoDBManager.db["socialmediatimeline"]
        MongoDBManager.user = MongoDBManager.db["socialmediauser"]
        MongoDBManager.entities = MongoDBManager.db["socialmediaentities"]
        MongoDBManager.replystatus = MongoDBManager.db["socialmediareplystatus"]

        MongoDBManager.gottentimelineuser = MongoDBManager.db["gottentimelineuser"]


    @staticmethod
    def insertCollection(tweeter_post):
        if(MongoDBManager.collection.find_one({ "id": tweeter_post["id"] })):
            return
        else:
            data_id = MongoDBManager.collection.insert_one(tweeter_post).inserted_id
            data_id = str(data_id)
        
            tweeter_post["user"]["_id"] = data_id
            tweeter_post["entities"]["_id"] = data_id
            if(MongoDBManager.user.find_one({ "id": tweeter_post["user"]["id"] })):
                MongoDBManager.user.delete_one({ "id": tweeter_post["user"]["id"] })
                MongoDBManager.user.insert_one(tweeter_post["user"])
                
            else:
                MongoDBManager.user.insert_one(tweeter_post["user"])

            MongoDBManager.entities.insert_one(tweeter_post["entities"])
            print("streaming       \t",data_id)

    @staticmethod
    def insertMention(mention):
        if(MongoDBManager.mention.find_one({ "id": mention["id"] })):
            return
        else:
            data_id = MongoDBManager.mention.insert_one(mention).inserted_id
            data_id = str(data_id)
        
            mention["user"]["_id"] = data_id
            mention["entities"]["_id"] = data_id
            if(MongoDBManager.user.find_one({ "id": mention["user"]["id"] })):
                MongoDBManager.user.delete_one({ "id": mention["user"]["id"] })
                MongoDBManager.user.insert_one(mention["user"])
                
            else:
                MongoDBManager.user.insert_one(mention["user"])

            MongoDBManager.entities.insert_one(mention["entities"])
            print("mention_timeline\t",data_id)

    @staticmethod
    def insertTimeline(timeline):
        if(MongoDBManager.timeline.find_one({ "id": timeline["id"] })):
            return
        else:
            data_id = MongoDBManager.timeline.insert_one(timeline).inserted_id
            data_id = str(data_id)
        
            timeline["user"]["_id"] = data_id
            timeline["entities"]["_id"] = data_id
            if(MongoDBManager.user.find_one({ "id": timeline["user"]["id"] })):
                MongoDBManager.user.delete_one({ "id": timeline["user"]["id"] })
                MongoDBManager.user.insert_one(timeline["user"])
                
            else:
                MongoDBManager.user.insert_one(timeline["user"])

            MongoDBManager.entities.insert_one(timeline["entities"])
            print("user_timeline\t",data_id)

    @staticmethod
    def insertReplyStatus(reply):
        if(MongoDBManager.replystatus.find_one({ "id": reply["id"] })):
            return
        else:
            data_id = MongoDBManager.replystatus.insert_one(reply).inserted_id
            print("reply_status\t",data_id)


    

    @staticmethod
    def getMostActiveUser(ban_name_list):
        result = {}
        for user in MongoDBManager.collection.find():
            if user["user"]["screen_name"] not in ban_name_list:
                if(user["user"]["id"] in result):
                    result[user["user"]["id"]] += 1
                else:
                    result[user["user"]["id"]] = 1
        
        user_frequency = 0
        top_user = ""

        for user_id in result.keys():
            if(result[user_id] >= user_frequency):
                user_frequency = result[user_id]
                top_user = user_id
        return top_user

    @staticmethod
    def getMostActiveUsersIDByLimit(limit, ban_list):
        result = {}
        result_by_limit = []
        for user in MongoDBManager.collection.find():
            if(user["user"]["id"] not in ban_list):
                if(user["user"]["id"] in result):
                    result[user["user"]["id"]] += 1
                else:
                    result[user["user"]["id"]] = 1

        #Credit : https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        result = sorted(result.items(), key=lambda item: item[1],reverse=True)
        #
        for user in result:
            result_by_limit.append(user[0])
            if(len(result_by_limit) >= limit):
                break
        return result_by_limit

    @staticmethod
    def getMostMentionedAboutUsersIDByLimit(limit,ban_list):
        result = {}
        result_by_limit = []
        for entities in MongoDBManager.entities.find():
            for user in entities["user_mentions"]:
                if(user["id"] not in ban_list):
                    if(user["id"] in result):
                        result[user["id"]] += 1
                    else:
                        result[user["id"]] = 1
        
        #Credit : https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        result = sorted(result.items(), key=lambda item: item[1],reverse=True)
        #
        for user in result:
            result_by_limit.append(user[0])
            if(len(result_by_limit) >= limit):
                break
        return result_by_limit

    @staticmethod
    def insertTimelineUser(userid):
        MongoDBManager.gottentimelineuser.insert_one({"userid" :userid})

    @staticmethod
    def getTimelineUserNumbers(filter):
        return MongoDBManager.gottentimelineuser.count_documents(filter)

    @staticmethod
    def removeAllTimelineUser():
        MongoDBManager.gottentimelineuser.delete_many({})