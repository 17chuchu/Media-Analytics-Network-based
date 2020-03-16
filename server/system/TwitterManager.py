import json
import datetime
import uuid
import datetime
import time
import requests
import threading

import tweepy


from System.MongoDBManager import MongoDBManager


class TwitterManager:

    auth = None
    ban_name_list = [
        'abhimovies',
        'vernajonesa',
        'morrellmyles',
        'WarpsiwaHOT',
        'MartelDione',
        'jonmsculley',
        'phegleydam',
        'ClaireMovie',
        'chloritzmovie',
        'OsoPand56069545',
        'alxturnnnr',
        'maitruc115',
        'wehjne924008',
        'heirex_',
        'RedRose32367698',
        'budibondowoso66'
    ]





    @staticmethod
    def setup():
        consumer_key = 'y6S6RulvjNTGdSiZRF57zG39e'
        consumer_secret = 'exAdeWcjLTHM2zkFE1apWzMfj2qWhEasZ6qNcMvlbZcDlif3zU'

        access_token = '1225417516031381514-wzMm45HXJKOvfJ0HYpi53HRMhhYKXi'
        access_token_secret = 'MKOwGMDOqmAh3f19ZcAi1BG276VpqtR24sUIBYHQzfKq3'


        TwitterManager.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        TwitterManager.auth.set_access_token(access_token, access_token_secret)

    @staticmethod
    def startStreaming(listener,track_list,follow_users = []):
        stream = tweepy.Stream(TwitterManager.auth, listener)
        if(len(follow_users) > 0):
            stream.filter(track=track_list,follow=follow_users, is_async=True, languages=["en"])
        else:
            stream.filter(track=track_list, is_async=True, languages=["en"])
    
    @staticmethod
    def startGettingUserMentionsTimeline():
        
        tUserTimeline = threading.Thread(target=TwitterManager.startGettingUserTimeline)
        tUserTimeline.start()

        #tMentionsTimeline = threading.Thread(target=TwitterManager.startGettingMentionsTimeline)
        #tMentionsTimeline.start()
        
    @staticmethod
    def startGettingUserTimeline():
        while(True):
            api = tweepy.API(TwitterManager.auth)
            #users_list = MongoDBManager.getMostActiveUsersIDByLimit(60,TwitterManager.ban_name_list)
            users_list = MongoDBManager.getMostMentionedAboutUsersIDByLimit(60,TwitterManager.ban_name_list)

            if(MongoDBManager.getTimelineUserNumbers({}) >= 60):
                MongoDBManager.removeAllTimelineUser()
            else:
                print("Currently",MongoDBManager.getTimelineUserNumbers({}), "people have been GET.")

            is_user_list_gettable = False

            for userid in users_list:
                if(MongoDBManager.getTimelineUserNumbers({"userid": userid}) == 0):
                    try:
                        response = api.user_timeline(user_id = userid)
                        MongoDBManager.insertTimelineUser(userid)
                        is_user_list_gettable = True
                        for post in response:
                            if(post._json["user"]["screen_name"] not in TwitterManager.ban_name_list):
                                MongoDBManager.insertTimeline(post._json)
                        time.sleep(10)
                        break
                    except:
                        MongoDBManager.insertTimelineUser(userid)
                        is_user_list_gettable = True
                        print("Rate limit reach.")
                        time.sleep(30)
                        break
            
            if(not is_user_list_gettable):
                MongoDBManager.removeAllTimelineUser()

    @staticmethod
    def startGettingMentionsTimeline():
        while(True):
            api = tweepy.API(TwitterManager.auth)
            for post in tweepy.Cursor(api.mentions_timeline).items():
                if(post._json["user"]["screen_name"] not in TwitterManager.ban_name_list):
                    MongoDBManager.insertMention(post._json)
            time.sleep(900)
        

        #api.mentions_timeline()
    

