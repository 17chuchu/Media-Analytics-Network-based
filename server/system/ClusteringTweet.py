import collections

import pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk import FreqDist
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.decomposition import PCA

import matplotlib.pyplot as plt


from System.MongoDBManager import MongoDBManager


class ClusteringTweet:

    tweetDataFrame = None
    tfidfModel = None
    kmeanModel = None
    countVecTweet = None

    @staticmethod
    def run(max_text_size = 0,group_num = 1):
        ClusteringTweet.fetch_texts(max_text_size)
        
        if(group_num > 0):
            ClusteringTweet.cluster_texts(ClusteringTweet.tweetDataFrame.loc[:, 'text'],group_num)
        else:
            ClusteringTweet.cluster_texts(ClusteringTweet.tweetDataFrame.loc[:, 'text'],1)

        ClusteringTweet.tweetDataFrame["group"] = [0 for i in range(ClusteringTweet.tweetDataFrame.shape[0])]

        for index, row in ClusteringTweet.tweetDataFrame.iterrows():
            ClusteringTweet.tweetDataFrame.at[index,'group'] = ClusteringTweet.find_text_cluster(row["text"])

    @staticmethod
    def print_info():
        data_size = ClusteringTweet.tweetDataFrame.shape[0]
        group_num = ClusteringTweet.tweetDataFrame.groupby('group').nunique().shape[0]
        
        max_group_size = max(ClusteringTweet.tweetDataFrame.groupby('group').nunique().loc[:, 'text'])
        min_group_size = min(ClusteringTweet.tweetDataFrame.groupby('group').nunique().loc[:, 'text'])
        avg_group_size = (ClusteringTweet.tweetDataFrame.groupby('group').nunique().loc[:, 'text']).sum() / group_num
        avg_group_size = int(avg_group_size * 1000) / 1000

        group_info = {}
        all_tweet = {}
        for tweet in MongoDBManager.collection.find():
            all_tweet[tweet["id_str"]] = tweet
        for tweet in MongoDBManager.timeline.find():
            all_tweet[tweet["id_str"]] = tweet

        print("| Data size | Number of groups | Average group size | Maximum group size | Minimum group size |")
        print("|:------------:|:-----------------:|:--------------------:|:--------------------:|:--------------------:|")
        print("|",data_size,"|",group_num,"|",avg_group_size,"|",max_group_size,"|",min_group_size,"|")
        print()

        for index, row in ClusteringTweet.tweetDataFrame.iterrows():
            if(row['group'] not in group_info):
                group_info[row['group']] = {'users': [], 'hashtags': [],"mentions": []}
            
            tweet = all_tweet[row['id']]

            group_info[row['group']]['users'].append(tweet["user"]["screen_name"])

            for hashtags in tweet["entities"]["hashtags"]:
                group_info[row['group']]['hashtags'].append(hashtags['text'])
                
            for user_mentions in tweet["entities"]["user_mentions"]:
                group_info[row['group']]['mentions'].append(user_mentions['screen_name'])
        
        print("| Group Number | Top 10 most common users | Top 10 most common hashtags | Top 10 most mentioned users |")
        print("|:------------:|:-----------------:|:--------------------:|----------------------|")
        for keys in range(group_num):

            most_commom_user = " "
            for i in FreqDist(group_info[keys]['users']).most_common(10):
                most_commom_user += str(i[0]) + "(" + str(i[1]) + ") "
            
            most_commom_hashtags = " "
            for i in FreqDist(group_info[keys]['hashtags']).most_common(10):
                most_commom_hashtags += str(i[0]) + "(" + str(i[1]) + ") "
            
            most_commom_mentions = " "
            for i in FreqDist(group_info[keys]['mentions']).most_common(10):
                most_commom_mentions += str(i[0]) + "(" + str(i[1]) + ") "
            
            print("|",keys + 1,"|",most_commom_user,"|",most_commom_hashtags,"|",most_commom_mentions,"|")



        #Important username 
        #Important hashtags
        #average size of a group
        #min size
        #max size 

    @staticmethod
    def draw():
        count_vec = ClusteringTweet.countVecTweet.transform(ClusteringTweet.tweetDataFrame.loc[:, 'text'])
        tfidf_data = ClusteringTweet.tfidfModel.transform(count_vec).todense()
        kmeans = ClusteringTweet.kmeanModel.predict(tfidf_data)

        pca = PCA().fit(tfidf_data)
        data2D = pca.transform(tfidf_data)
        plt.scatter(data2D[:,0], data2D[:,1],c = kmeans)

        centers2D = pca.transform(ClusteringTweet.kmeanModel.cluster_centers_)
        plt.scatter(centers2D[:,0], centers2D[:,1], 
                    marker='x', s=200, linewidths=3, c='r')

        plt.show()   

    @staticmethod
    def fetch_texts(maxsize = 0):
        tweetData = {}
        for tweets in MongoDBManager.timeline.find():
            tweetData[tweets["id_str"]] = tweets["text"]
        for tweets in MongoDBManager.collection.find():
            tweetData[tweets["id_str"]] = tweets["text"]
        if(maxsize > 0):
            ClusteringTweet.tweetDataFrame = pd.DataFrame(data={'id': list(tweetData.keys())[0:maxsize], 'text': list(tweetData.values())[0:maxsize]})
        else:
            ClusteringTweet.tweetDataFrame = pd.DataFrame(data={'id': list(tweetData.keys()), 'text': list(tweetData.values())})

    @staticmethod
    def cluster_texts(texts,clusters):
        ClusteringTweet.countVecTweet = CountVectorizer()
        ClusteringTweet.tfidfModel = TfidfTransformer(smooth_idf=True,use_idf=True)

        ClusteringTweet.kmeanModel = KMeans(n_clusters=clusters)
        word_count_vector = ClusteringTweet.countVecTweet.fit_transform(texts)
        tfidf_model = ClusteringTweet.tfidfModel.fit_transform(word_count_vector)
        
        ClusteringTweet.kmeanModel.fit(tfidf_model)

    @staticmethod
    def find_text_cluster(text):
        count_vec = ClusteringTweet.countVecTweet.transform([text])
        tfidf_model = ClusteringTweet.tfidfModel.transform(count_vec)
        result = ClusteringTweet.kmeanModel.predict(tfidf_model)
        return result[0]


    @staticmethod
    def show_optimised_cluster_graph(k_range):
        ClusteringTweet.fetch_texts()
        ClusteringTweet.tweetDataFrame.loc[:, 'text']
        sse = []

        countv = CountVectorizer()
        word_count_vector = countv.fit_transform(ClusteringTweet.tweetDataFrame.loc[:, 'text'])
        tfidf_transformer = TfidfTransformer(smooth_idf=True,use_idf=True)
        ClusteringTweet.tfidfModel = tfidf_transformer.fit_transform(word_count_vector)

        for k in k_range:
            sse.append(MiniBatchKMeans(n_clusters=k, init_size=1024, batch_size=2048, random_state=20).fit(ClusteringTweet.tfidfModel).inertia_)
        
        f, ax = plt.subplots(1, 1)
        ax.plot(k_range, sse, marker='o')
        ax.set_xlabel('Cluster Centers')
        ax.set_xticks(k_range)
        ax.set_xticklabels(k_range)
        ax.set_ylabel('SSE')
        ax.set_title('SSE by Cluster Center Plot')
        plt.show()

        #Credit : https://www.kaggle.com/jbencina/clustering-documents-with-tfidf-and-kmeans
        
 
