# Network-based-Social-Media-Analytics

This is the guide on how to run this application. Please access the **server** folder and follow these steps to run the app.

Firstly, to setup the environment, run this command in the server folder :

```bash
source env/bin/activate
```

Secondly, in case you host your MongoDB database elsewhere. You can change the database location in the setup function in `System/MongoDBManager.py`. This line is what you will be looking for.

```python
MongoDBManager.client = pymongo.MongoClient("mongodb://localhost:27017/")
```

Thirdly, you should import the sample data into your MongoDB database. [You can download sample data here](https://drive.google.com/open?id=1GqjMegZncrWFRlZZy4nHL1xKTJ-iHaTg) since git does not allow data larger than 100mb. You should name the database `socialmediadatabase`, if you want the application to work right away. If not, you can change the database name in `System/MongoDBManager.py`. This line is what you will be looking for.

```python
MongoDBManager.db = MongoDBManager.client["socialmediadatabase"]
```

After the virtual environment is activated and the database link is correct, you will have the means to run the application. Let's go through the features of the software.


### 1) Start Twitter Streaming API
This streaming API will track a specific set of keywords and collect 1% streaming data. To run the streaming API, run this command: 

```bash
python3 apps.py startstream
```

The streaming API is quite simple. The function is in the `startStreaming` method in `System/TwitterManager.py` file. Also, a custom stream listener is located in `System/CustomStreamListener.py`, which is where the streaming API sends status to. Additionally, the status is sent further to `insertCollection` method in `System/MongoDBManager.py`, where the user object and the entity object is pulled from the status object into their own table for convenient query (mostly counting). Each status is then checked for duplication before inserting into the `collection` table. I did not use `id_str` as `_id` tree because I too late to realise the possibility.

### 2) Start Twitter Streaming & REST APIs 
This streaming API will track a specific set of keywords, and the rest API will execute tweepy.user_timeline to get the 20 most recent statuses posted by the user who is the most mentioned about. To run the streaming and REST API, run this command: 

```bash
python3 apps.py startstreamrest
```

In this method, the `startGettingUserTimeline` method in `System/TwitterManager.py` will be run over and over again until the API's limit is reached. A list of 60 most mentioned users will be queried every time, and the already queried users will be recorded in a MongoDB table using `MongoDBManager.insertTimelineUser`. The table is cleared every time its size reaches 60. The status is inserted using `MongoDBManager.insertTimeline` into a table called `timeline`.

### 3) Start Getting Reply Status
This REST API will query full statuses from a list of `in_reply_to_user_id_str` field in an existing status object. 

```bash
python3 apps.py startgettingreplystatus
```

The statuses are recorded in the `replystatus` table using `MongoDBManager.insertReplyStatus`.

### 4) Show SSE Graph
This method will generate Sum of Squared Errors graph from 1-40 group as default. Also, the range of groups can be customised.

```bash
python3 apps.py showssegraph
```

A number can be appended to the command to generate Sum of Squared Errors graph from 1-20 group instead.

```bash
python3 apps.py showssegraph 20
```

Credit for the SSE Graph : https://www.kaggle.com/jbencina/clustering-documents-with-tfidf-and-kmeans

### 5) Clustering
This method will cluster and print the most frequent users, hashtags, mentioned users in each group. You can access the implementation in `ClusteringTweet.run`. The first most important is `ClusteringTweet.cluster_texts`, which is a pipeline for converting a list of texts into a bag of words using `CountVectorizer`, then to a TF-IDF vector using `TfidfTransformer`, and then to a group using `KMeans` clustering. Finally, a table which shows the top 10 common user id, top 10 hashtags, and the top 10 most mentioned users. 

```bash
python3 apps.py clustering
```

To customise the amount of data, append a number after the command. For example, this command will cluster and extract 10,000 tweets from the whole dataset. Moreover, setting the number of tweets to 0 will cause the system to cluster the whole dataset.

```bash
python3 apps.py clustering 10000
```

To customise the number of the group, append a number after the above command.

```bash
python3 apps.py clustering 10000 15
```

### 6) Clustering and Extract User Network
This method will extract user network information from clustered texts. This method will do clustering and print two markdown tables for each group. For each group, a markdown table will consist of the number of each triadic types exists and the number of weak and strong ties for mentioned users, retweeted tweet's owner, and tweet's owner of the tweet that was replied to.

```bash
python3 apps.py clusteringandextract
```

To customise the amount of data, append a number after the command. For example, this command will cluster and extract 10,000 tweets from the whole dataset. Moreover, setting the number of tweets to 0 will cause the system to cluster the whole dataset.

```bash
python3 apps.py clusteringandextract 10000
```

To customise the number of the group, append a number after the above command.

```bash
python3 apps.py clusteringandextract 10000 15
```

### 7) Clustering and Extract Hashtag Network
This method will extract hashtag network information from clustered texts. This method will do clustering and print two markdown tables for each group. For each group, a markdown table will consist of the number of each triadic types exists and the number of weak and strong ties.

```bash
python3 apps.py clusteringandextracthashtag
```

To customise the amount of data, append a number after the command. For example, this command will cluster and extract 10,000 tweets from the whole dataset. Moreover, setting the number of tweets to 0 will cause the system to cluster the whole dataset.

```bash
python3 apps.py clusteringandextracthashtag 10000
```

To customise the number of the group, append a number after the above command.

```bash
python3 apps.py clusteringandextracthashtag 10000 15
```
