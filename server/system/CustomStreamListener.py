import json
import datetime
import uuid
import datetime
import time
import requests

import tweepy

from django.db import connection

from system.MongoDBManager import MongoDBManager
from system.TwitterManager import TwitterManager

class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        json_data = status._json
        
        if(json_data["user"]["screen_name"] not in TwitterManager.ban_name_list):
            if(MongoDBManager.collection):
                MongoDBManager.insertCollection(json_data)

        #print(json_data["timestamp_ms"])

    def on_error(self, status_code):
        
        error_code = {
            "200":	"OK	Success!",
            "304":	"Not Modified	There was no new data to return.",
            "400":	"Bad Request	The request was invalid or cannot be otherwise served. An accompanying error message will explain further. Requests without authentication are considered invalid and will yield this response.",
            "401":	"Unauthorized	Missing or incorrect authentication credentials. This may also returned in other undefined circumstances.",
            "403":	"Forbidden	The request is understood, but it has been refused or access is not allowed. An accompanying error message will explain why. This code is used when requests are being denied due to update limits . Other reasons for this status being returned are listed alongside the error codes in the table below.",
            "404":  "Not Found	The URI requested is invalid or the resource requested, such as a user, does not exist.",
            "406":	"Not Acceptable	Returned when an invalid format is specified in the request.",
            "410":	"Gone	This resource is gone. Used to indicate that an API endpoint has been turned off.",
            "420":	"Enhance Your Calm	Returned when an app is being rate limited for making too many requests.",
            "422":	"Unprocessable Entity	Returned when the data is unable to be processed (for example, if an image uploaded to POST account / update_profile_banner is not valid, or the JSON body of a request is badly-formed).",
            "429":	"Too Many Requests	Returned when a request cannot be served due to the app\'s rate limit having been exhausted for the resource. See Rate Limiting.",
            "500":	"Internal Server Error	Something is broken. This is usually a temporary error, for example in a high load situation or if an endpoint is temporarily having issues. Check in the developer forums in case others are having similar issues,  or try again later.",
            "502":	"Bad Gateway	Twitter is down, or being upgraded.",
            "503":	"Service Unavailable	The Twitter servers are up, but overloaded with requests. Try again later.",
            "504":	"Gateway timeout	The Twitter servers are up, but the request couldn’t be serviced due to some failure within the internal stack. Try again later.",
        }

        if(str(status_code) in error_code):
            print(status_code,error_code[str(status_code)])
        else:
            print(status_code,"Unknown Error.")

        return False


        '''
        created_at
        id
        id_str
        text
        source
        truncated
        in_reply_to_status_id
        in_reply_to_status_id_str
        in_reply_to_user_id
        in_reply_to_user_id_str
        in_reply_to_screen_name
        user
        geo
        coordinates
        place
        contributors
        retweeted_status
        is_quote_status
        quote_count
        reply_count
        retweet_count
        favorite_count
        entities
        extended_entities
        favorited
        retweeted
        possibly_sensitive
        filter_level
        lang
        timestamp_ms
        '''

