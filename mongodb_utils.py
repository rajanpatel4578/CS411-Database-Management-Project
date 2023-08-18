import copy

import pandas as pd
from pandas import DataFrame
from pymongo import MongoClient

from mysql_utils import queryFavKeywordsForUser, queryTopTrendingKeywordsLast5Years

client = MongoClient(host='localhost', port=27017)
db = client['academicworld']


# get top 25 publications and faculties for the given keyword.
def queryPublicationAndFacultyForKeyword(keyword):
    query = [{'$unwind': '$keywords'}, {'$match': {'keywords.name': "{keyword}".format(keyword=keyword)}},
             {'$project': {'_id': 0, 'ID': '$id', 'Title': '$title', 'Year': '$year', 'Citation count': '$numCitations',
                           'Venue': '$venue'}},
             {'$lookup': {'from': 'faculty', 'localField': 'ID', 'foreignField': 'publications', 'as': 'Authors'}},
             {'$project': {'ID': 1, 'Title': 1, 'Year': 1, 'Citation count': 1, 'Venue': 1, 'Authors.id': 1,
                           'Authors.name': 1, 'Authors.affiliation.name': 1}}, {'$limit': 25}]
    myDoc = db['publications'].aggregate(query)
    return myDoc


def queryRelevantPublications(user_id=0, limit=10):
    keywordsDF = pd.DataFrame(data=[])

    if user_id > 0:
        keywordsDF = queryFavKeywordsForUser(user_id, limit)

    if keywordsDF.empty:
        keywordsDF = queryTopTrendingKeywordsLast5Years(limit)

    if keywordsDF.empty:
        query = [{'$project': {'_id': 0, 'ID': '$id', 'Title': '$title', 'citationCount': '$numCitations'}},
                 {'$sort': {'citationCount': -1}}, {'$limit': limit}]
    else:
        keyListForMatch = []
        for key in keywordsDF['Keyword']:
            keyListForMatch.append({'keywords.name': "{key}".format(key=key)})

        matchCriteria = {
            '$match':
                {
                    '$or': copy.deepcopy(keyListForMatch)
                }
        }

        query = [{'$unwind': '$keywords'}, matchCriteria,
                 {'$project': {'_id': 0, 'pub': '$id', 'title': 1,
                               'KRC': {'$multiply': ['$keywords.score', '$numCitations']}}}, {'$sort': {'KRC': -1}},
                 {'$limit': 10}, {'$project': {'_id': 0, 'ID': '$pub', 'Title': '$title'}}]

    # print(query)

    myDoc = db['publications'].aggregate(query)
    resList = list(myDoc)
    searchResDF = DataFrame(resList)
    return searchResDF


def queryTopKeywords(limit):
    query = [{'$unwind': '$keywords'}, {'$unwind': '$keywords.name'},
             {'$group': {"_id": "$keywords.name", 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}, {'$limit': limit},
             {'$project': {'Keyword': "$_id", "_id": 0}}, {'$limit': limit}]
    # print(query)
    myDoc = db['publications'].aggregate(query)
    resList = list(myDoc)
    topKeywordsResDF = DataFrame(resList)
    return topKeywordsResDF


# Query top universities by relevance for the keywords. If user is known then we use top 5 users keywords
def getTopUniversitiesByKeywords(user_id=0, limit=5):
    keywordsDF = pd.DataFrame(data=[])

    if user_id > 0:
        keywordsDF = queryFavKeywordsForUser(user_id, limit)

    if keywordsDF.empty:
        keywordsDF = queryTopTrendingKeywordsLast5Years(limit)

    if not keywordsDF.empty:
        keyListForMatch = []
        for key in keywordsDF['Keyword']:
            keyListForMatch.append({'keywords.name': "{key}".format(key=key)})

        matchCriteria = {
            '$match':
                {
                    '$or': copy.deepcopy(keyListForMatch)
                }
        }
        query = [{'$unwind': '$keywords'}, matchCriteria, {'$unwind': '$affiliation.name'}, {
            '$group': {'_id': '$affiliation.name', 'URL': {'$first': '$affiliation.photoUrl'}, 'count': {'$sum': 1}}},
                 {'$sort': {'count': -1}},
                 {'$project': {'University': '$_id', '_id': 0, 'URL': 1, 'KeywordCount': '$count'}}, {'$limit': limit}]
    else:
        query = [{'$unwind': '$keywords'}, {'$unwind': '$affiliation.name'}, {
            '$group': {'_id': '$affiliation.name', 'URL': {'$first': '$affiliation.photoUrl'}, 'count': {'$sum': 1}}},
                 {'$sort': {'count': -1}},
                 {'$project': {'University': '$_id', '_id': 0, 'URL': 1, 'KeywordCount': '$count'}}, {'$limit': limit}]

    # print(query)
    myDoc = db['faculty'].aggregate(query)
    resList = list(myDoc)
    searchResDF = DataFrame(resList)
    return searchResDF


# Query top faculties by relevance for the keywords. If user is known then we use top 10 users keywords
def getTopFacultiesByKeywords(user_id=0, limit=5):
    keywordsDF = pd.DataFrame(data=[])

    if user_id > 0:
        keywordsDF = queryFavKeywordsForUser(user_id, limit)

    if keywordsDF.empty:
        keywordsDF = queryTopTrendingKeywordsLast5Years(limit)

    if not keywordsDF.empty:
        keyListForMatch = []
        for key in keywordsDF['Keyword']:
            keyListForMatch.append({'keywords.name': "{key}".format(key=key)})

        matchCriteria = {
            '$match':
                {
                    '$or': copy.deepcopy(keyListForMatch)
                }
        }
        query = [{'$unwind': '$keywords'}, matchCriteria,
                 {'$group': {'_id': '$name', 'count': {'$sum': 1}, 'Picture': {'$first': '$photoUrl'},
                             'University': {'$first': '$affiliation.name'},
                             'Title': {'$first': '$position'}}}, {'$sort': {'count': -1}},
                 {'$project': {'Name': "$_id", 'count': 1, 'University': 1, 'Title': 1, 'Picture': 1, "_id": 0}},
                 {'$limit': limit}]
    else:
        query = [{'$unwind': '$keywords'},
                 {'$group': {'_id': '$name', 'count': {'$sum': 1}, 'Picture': {'$first': '$photoUrl'},
                             'University': {'$first': '$affiliation.name'},
                             'Title': {'$first': '$position'}}}, {'$sort': {'count': -1}},
                 {'$project': {'Name': "$_id", 'count': 1, 'University': 1, 'Title': 1, 'Picture': 1, "_id": 0}},
                 {'$limit': limit}]

    myDoc = db['faculty'].aggregate(query)
    resList = list(myDoc)
    searchResDF = DataFrame(resList)
    return searchResDF
