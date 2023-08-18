import pandas as pd
import sqlalchemy
from sqlalchemy import text
import pymysql

# Connect to mysql db 'academicworld'
url = 'mysql+pymysql://root:password@localhost/academicworld'
# Create engine, we can use the value for echo= to turn ON/OFF the tracing
engine = sqlalchemy.create_engine(url, echo=False)


# Get the top 5 faculty members by citations
def queryTop5Faculties():
    entries = []
    topFacultyQ = 'SELECT F.name AS Name,U.name AS University, F.photo_url AS Picture, P.title AS Title FROM ' \
                  'publication P, faculty F, faculty_publication FP, university U WHERE FP.faculty_id = F.id AND ' \
                  'FP.publication_id = P.id AND U.id= F. university_id ORDER BY P.num_citations DESC LIMIT 5;'

    with engine.connect() as con:
        top5fac = pd.read_sql(text(topFacultyQ), con)
    return top5fac


# Get all the universities by name
def queryUniversities(userID=0):
    if userID == 0 or userID is None:
        univQ = 'SELECT DISTINCT name FROM university;'
    else:
        univQ = 'SELECT DISTINCT U.name FROM university U, user_affiliations UA WHERE UA.uid={uid} AND ' \
                'UA.university_id=U.id;'.format(uid=userID)

    with engine.connect() as con:
        allUnivs = pd.read_sql(text(univQ), con)

    allUnivs = allUnivs['name']
    return allUnivs


# Get all the faculties by name
def queryFaculties(userID=0):
    if userID == 0 or userID is None:
        facQ = 'SELECT DISTINCT name FROM faculty;'
    else:
        facQ = 'SELECT DISTINCT F.name FROM faculty F, user_favorite_faculty UFF WHERE UFF.uid={uid} AND ' \
               'UFF.faculty_id=F.id;'.format(
            uid=userID)

    with engine.connect() as con:
        allFacs = pd.read_sql(text(facQ), con)

    allFacs = allFacs['name']
    return allFacs


# Get my favorite keywords
def queryMyFavoriteKeywords(userID):
    myFavKeywordsQ = 'SELECT K.name AS Keyword FROM keyword K, user_favorite_keyword UFK WHERE UFK.uid =' \
                     ' \"{userID}\" AND K.id = UFK.keyword_id;'.format(userID=userID)
    with engine.connect() as con:
        myFavKeywords = pd.read_sql(text(myFavKeywordsQ), con)

    return myFavKeywords


# Get my favorite publications
def queryMyFavoritePublications(userID):
    myFavPubsQ = 'SELECT P.id AS ID, P.title AS Title FROM publication P, user_favorite_publication UFP WHERE UFP.uid =' \
                 ' \"{userID}\" AND P.id = UFP.publication_id;'.format(userID=userID)
    with engine.connect() as con:
        myFavPubs = pd.read_sql(text(myFavPubsQ), con)

    return myFavPubs


# Get my favorite faculties
def queryMyFavoriteFaculties(userID):
    myFavFacsQ = 'SELECT F.name AS Name, U.name AS University FROM faculty F, university U, user_favorite_faculty UFF ' \
                 'WHERE UFF.uid = \"{userID}\" AND F.id = UFF.faculty_id AND F.university_id = U.id;'.format(
        userID=userID)
    with engine.connect() as con:
        myFavFacs = pd.read_sql(text(myFavFacsQ), con)

    return myFavFacs


# Get user affiliations
def queryAffiliationsForUser(userID):
    getAffilationsQ = 'SELECT U.name AS University FROM user_affiliations UA, university U WHERE UA.uid={uid} AND ' \
                      'UA.university_id=U.id;'.format(uid=userID)
    with engine.connect() as con:
        userAffilations = pd.read_sql(text(getAffilationsQ), con)

    return userAffilations


def queryConnectionsForUser(userID):
    if userID is None:
        userID = 0

    getConnectionsQ = 'SELECT F.name AS Name FROM user_connections UC, faculty F WHERE UC.uid={uid} AND ' \
                      'UC.faculty_id=F.id;'.format(uid=userID)

    with engine.connect() as con:
        userConnections = pd.read_sql(text(getConnectionsQ), con)

    return userConnections


# Get users current works
def queryWorksForUser(userID):
    userWorks = pd.DataFrame()
    # Query the work ID and title for the current works for the user
    currentWorksQ = 'SELECT UW.pre_pub_id AS ID,  UW.title AS Title FROM user_work UW WHERE UW.uid={uid};'.format(
        uid=userID)

    with engine.connect() as con:
        currentWorks = pd.read_sql(text(currentWorksQ), con)

    # Query the Citations list for the current works of the user
    citationsQ = 'SELECT UWPC.pre_pub_id AS ID, UWPC.cited_publication_id AS Citations FROM ' \
                 'user_work_publication_citations UWPC, user_work UW WHERE UW.uid={uid} AND ' \
                 'UWPC.pre_pub_id=UW.pre_pub_id;'.format(
        uid=userID)
    with engine.connect() as con:
        workCitations = pd.read_sql(text(citationsQ), con)

    # Query the Keyword references for the users current work.
    keywordsQ = 'SELECT UWK.pre_pub_id AS ID, K.name AS Keywords FROM user_work UW, user_work_keyword UWK, keyword K ' \
                'WHERE UW.uid={uid} AND UWK.pre_pub_id=UW.pre_pub_id AND K.id=UWK.keyword_id;'.format(
        uid=userID)
    with engine.connect() as con:
        workKeywords = pd.read_sql(text(keywordsQ), con)

    # Prepare the query output by combining the works by id correctly
    if not currentWorks.empty:
        combinedIDs = currentWorks[['ID']].groupby('ID')['ID'].apply(set)
        combinedIDs = combinedIDs.apply(lambda x: "".join(map(str, x)))
        combinedTitles = currentWorks[['ID', 'Title']].groupby('ID')['Title'].apply(set)
        combinedTitles = combinedTitles.apply(lambda x: "".join(map(str, x)))
        combinedCitations = workCitations[['ID', 'Citations']].groupby('ID')['Citations'].apply(set)
        combinedCitations = combinedCitations.apply(lambda x: ",".join(map(str, x)))
        combinedKeywords = workKeywords[['ID', 'Keywords']].groupby('ID')['Keywords'].apply(set)
        combinedKeywords = combinedKeywords.apply(lambda x: ",".join(map(str, x)))
        userWorks = pd.concat([combinedIDs, combinedTitles, combinedCitations, combinedKeywords], axis=1)

    return userWorks.astype(str), userWorks


# Search by keyword name
def queryKeywordID(keywordName):
    searchKeyWQ = 'SELECT id FROM keyword WHERE name=\"{key}\";'.format(key=keywordName)
    with engine.connect() as con:
        keywordID = pd.read_sql(text(searchKeyWQ), con)

    return keywordID


# Search for user work by title
def queryUserWorkTitle(title, userID):
    userWorkQ = 'SELECT pre_pub_id FROM user_work WHERE title=\"{title}\" AND uid={uid};'.format(title=title,
                                                                                                 uid=userID)
    with engine.connect() as con:
        workID = pd.read_sql(text(userWorkQ), con)

    return workID


# Search by university name
def queryUniversityID(univName):
    searchUnivWQ = 'SELECT id FROM university WHERE name=\"{name}\";'.format(name=univName)
    with engine.connect() as con:
        univID = pd.read_sql(text(searchUnivWQ), con)

    return univID


# Search by faculty name
def queryFacultyID(facultyName):
    searchFacWQ = 'SELECT id FROM faculty WHERE name=\"{name}\";'.format(name=facultyName)
    with engine.connect() as con:
        facID = pd.read_sql(text(searchFacWQ), con)

    return facID


# Search for keyword by name
def queryTopTrendingKeywordsLast5Years(limit):
    searchKeyWQ = 'SELECT name as Keyword FROM top_trending_keywords_last_5_years LIMIT {limit};'.format(limit=limit)
    with engine.connect() as con:
        keywordsRes = pd.read_sql(text(searchKeyWQ), con)

    return keywordsRes


# Search for username
def queryUserByName(username):
    searchUserQ = 'SELECT username, id FROM users WHERE username = \"{user}\";'.format(user=username)
    with engine.connect() as con:
        searchUser = pd.read_sql(text(searchUserQ), con)

    return searchUser


# Search for user by id
def queryUserByID(user_id):
    if user_id > 0:
        searchUserQ = 'SELECT username AS Name FROM users WHERE id = {uid};'.format(uid=user_id)
        with engine.connect() as con:
            searchUser = pd.read_sql(text(searchUserQ), con)
        return searchUser
    else:
        return None

# Get favorite keywords
def queryFavKeywordsForUser(userID, count):
    getFavKeywordsQ = 'SELECT K.name AS Keyword FROM user_favorite_keyword UFK, keyword K WHERE UFK.uid={uid} AND ' \
                      'K.id=UFK.keyword_id LIMIT {cnt};'.format(
        uid=userID, cnt=count)
    with engine.connect() as con:
        favKeywords = pd.read_sql(text(getFavKeywordsQ), con)

    return favKeywords


# Get all the Publication Years
def queryPublicationYears():
    publicationYearQ = 'SELECT DISTINCT year AS Year FROM publication ORDER BY year;'

    with engine.connect() as con:
        allYears = pd.read_sql(text(publicationYearQ), con)
        allYears = allYears['Year']

    return allYears


# Get all the Keywords by name
def queryKeywords(userID=0):
    if userID == 0 or userID is None:
        keywordQ = 'SELECT DISTINCT name FROM keyword ORDER BY name;'
    else:
        keywordQ = 'SELECT K.name FROM keyword K, user_favorite_keyword UFK WHERE UFK.uid =' \
                   ' \"{userID}\" AND K.id = UFK.keyword_id;'.format(userID=userID)

    with engine.connect() as con:
        allKeywords = pd.read_sql(text(keywordQ), con)
        allKeywords = allKeywords['name']
    return allKeywords


# Get Trending Keywords
def queryTrendingKeywordsByYear(year, limit):
    trendingKeywordsQ = 'SELECT keyword AS Keyword, ROW_NUMBER() OVER (ORDER BY COUNT(pub_id) DESC) AS Ranking FROM ' \
                        'university_trends WHERE year={year} GROUP BY Keyword ORDER BY COUNT(pub_id) DESC LIMIT ' \
                        '{limit};'.format(
        year=year, limit=limit)
    with engine.connect() as con:
        trendingKeywords = pd.read_sql(text(trendingKeywordsQ), con)

    return trendingKeywords


# Get University Research Trends
def queryUniversityResearchTrends(selectedUnivs, selectedKeyword):
    selectedUnivs = str(selectedUnivs)
    selectedUnivs = selectedUnivs.removeprefix('[')
    selectedUnivs = selectedUnivs.removesuffix(']')
    univResearchTrendsQ = 'SELECT university AS University, year AS Year, COUNT(pub_id) AS \'Publications Count\' ' \
                          'FROM university_trends WHERE University IN ({univList}) AND Keyword = \'{keyword}\' ' \
                          'GROUP BY University, year ORDER BY year;'.format(univList=selectedUnivs,
                                                                            keyword=selectedKeyword)
    # print(univResearchTrendsQ)
    with engine.connect() as con:
        univResearchTrends = pd.read_sql(text(univResearchTrendsQ), con)

    return univResearchTrends


# Add to favorite publications
def addToFavoritePublications(user_id, publication_id):
    addFavPubsQ = 'INSERT IGNORE INTO user_favorite_publication (uid, publication_id) VALUES ("{uid}", "{pub_id}");'.format(
        uid=user_id, pub_id=publication_id)
    with engine.connect() as con:
        con.execute(text(addFavPubsQ))
        con.commit()

    return


# Add to favorite authors
def addToFavoriteAuthors(user_id, authors):
    addFavAuthorsQ = 'INSERT IGNORE INTO user_favorite_faculty (uid, faculty_id) VALUES '
    entries = []
    for auth in authors:
        entries.append('("{uid}", "{faculty_id}")'.format(uid=user_id, faculty_id=auth))
    addFavAuthorsQ = addFavAuthorsQ + ','.join(entries) + ';'
    with engine.connect() as con:
        con.execute(text(addFavAuthorsQ))
        con.commit()

    return


# Add to favorite keywords
def addToFavoriteKeywords(user_id, keyword):
    addFavKeywordQ = 'INSERT IGNORE INTO user_favorite_keyword (uid, keyword_id) SELECT "{uid}", id FROM keyword ' \
                     'WHERE name="{keyword}";'.format(uid=user_id, keyword=keyword)
    with engine.connect() as con:
        con.execute(text(addFavKeywordQ))
        con.commit()

    return


# Add affiliation
def addToUserAffiliations(user_id, universityName):
    addAffQ = 'INSERT IGNORE INTO user_affiliations (uid, university_id) SELECT "{uid}", id FROM university ' \
              'WHERE name="{univName}";'.format(uid=user_id, univName=universityName)
    with engine.connect() as con:
        con.execute(text(addAffQ))
        con.commit()

    return


# Add connection
def addToUserConnections(user_id, conName):
    addConnQ = 'INSERT IGNORE INTO user_connections (uid, faculty_id) SELECT "{uid}", id FROM faculty ' \
               'WHERE name="{facName}";'.format(uid=user_id, facName=conName)
    with engine.connect() as con:
        con.execute(text(addConnQ))
        con.commit()

    return


# Add users work
def addToUserWorks(user_id, workTitle, publicationsCited, keywordsReferenced):
    # Add the work to user_work table
    addWorkQ = 'INSERT IGNORE INTO user_work(uid, title) VALUES ({uid}, "{title}");'.format(uid=user_id,
                                                                                            title=workTitle)
    # First insert the work title into user work table so that we have the pre publication ID which is auto generated.
    with engine.connect() as con:
        con.execute(text(addWorkQ))
        con.commit()

    # Fetch the newly assigned ID for the work
    queryPrePubID = 'SELECT pre_pub_id FROM user_work WHERE title="{title}" AND uid={uid}'.format(title=workTitle,
                                                                                                  uid=user_id)
    with engine.connect() as con:
        prePubID = pd.read_sql(text(queryPrePubID), con)

    if prePubID.empty:
        return 'FAILED'
    else:
        # Iterate over the cited publications and to the user_work_keyword table
        if keywordsReferenced:
            for x in keywordsReferenced.strip().split(","):
                x = x.strip()
                if x:
                    addRefKeywordsQ = 'INSERT IGNORE INTO user_work_keyword(pre_pub_id, keyword_id) SELECT {' \
                                      'pre_pub_id}, id FROM keyword WHERE name="{kName}";'.format(
                        pre_pub_id=prePubID['pre_pub_id'][0], kName=x)
                    with engine.connect() as con:
                        con.execute(text(addRefKeywordsQ))
                        con.commit()

        # Iterate over the cited publications and to the user_work_publication_citations table
        if publicationsCited:
            for x in publicationsCited.strip().split(","):
                x = x.strip()
                if x:
                    addCitationsQ = 'INSERT IGNORE INTO user_work_publication_citations(pre_pub_id, ' \
                                    'cited_publication_id) VALUES ({pre_pub_id}, {cit_pub_id});'.format(
                        pre_pub_id=prePubID['pre_pub_id'][0],
                        cit_pub_id=x)
                    with engine.connect() as con:
                        con.execute(text(addCitationsQ))
                        con.commit()

    return "SUCCESS"


# Create new username
def createuserByName(username):
    createUserQ = 'INSERT INTO users (username) VALUES ("{user}");'.format(user=username)
    with engine.connect() as con:
        con.execute(text(createUserQ))
        con.commit()

    return


# Update/Modify users work
def updateUserWorks(user_id, workID, workTitle, publicationsCited, keywordsReferenced):
    # Add the work to user_work table
    updateWorkQ = 'UPDATE user_work SET title= "{title}" WHERE uid={uid} AND pre_pub_id={workID};'.format(
        title=workTitle,
        uid=user_id,
        workID=workID)

    # Update the work title in the user work table.
    with engine.connect() as con:
        con.execute(text(updateWorkQ))
        con.commit()

    # Delete the existing references to the keywords in the user_work_keyword table for this publication
    deleteExistingKeywordsQ = 'DELETE FROM user_work_keyword WHERE pre_pub_id={pubID};'.format(pubID=workID)
    # Update the work title in the user work table.
    with engine.connect() as con:
        con.execute(text(deleteExistingKeywordsQ))
        con.commit()

    # Iterate over the updated list of keywords and to the user_work_keyword table
    if keywordsReferenced:
        for x in keywordsReferenced.strip().split(","):
            x = x.strip()
            if x:
                addRefKeywordsQ = 'INSERT IGNORE INTO user_work_keyword(pre_pub_id, keyword_id) SELECT {pre_pub_id}, ' \
                                  'id FROM keyword WHERE name="{kName}";'.format(pre_pub_id=workID, kName=x)

            with engine.connect() as con:
                con.execute(text(addRefKeywordsQ))
                con.commit()

    # Delete the existing publication citations
    deleteExistingCitQ = 'DELETE FROM user_work_publication_citations WHERE pre_pub_id={pubID};'.format(pubID=workID)
    # Update the work title in the user work table.
    with engine.connect() as con:
        con.execute(text(deleteExistingCitQ))
        con.commit()

    # Iterate over the updated cited publications and add those user_work_publication_citations table
    if publicationsCited:
        for x in publicationsCited.strip().split(","):
            x = x.strip()
            if x:
                addCitationsQ = 'INSERT IGNORE INTO user_work_publication_citations(pre_pub_id, cited_publication_id) ' \
                                'VALUES ({pre_pub_id}, {cit_pub_id});'.format(
                    pre_pub_id=workID, cit_pub_id=x)

            with engine.connect() as con:
                con.execute(text(addCitationsQ))
                con.commit()

    return "SUCCESS"


# Delete user account/profile
def deleteUserProfile(userName):
    delUserQ = 'DELETE FROM users WHERE username="{name}";'.format(name=userName)
    with engine.connect() as con:
        con.execute(text(delUserQ))
        con.commit()

    return


# Delete from favorite keywords
def deleteFromFavoriteKeywords(user_id, keyword):
    delFavKeywordQ = 'DELETE FROM user_favorite_keyword WHERE uid={uid} AND keyword_id=(SELECT id FROM ' \
                     'keyword WHERE name="{keyword}");'.format(uid=user_id, keyword=keyword)
    with engine.connect() as con:
        con.execute(text(delFavKeywordQ))
        con.commit()

    return


# Delete from user affiliations
def deleteFromUserAffiliations(user_id, universityName):
    delAffUnivQ = 'DELETE FROM user_affiliations WHERE uid={uid} AND university_id=(SELECT id FROM ' \
                  'university WHERE name="{univ}");'.format(uid=user_id, univ=universityName)
    with engine.connect() as con:
        con.execute(text(delAffUnivQ))
        con.commit()
    return


# Delete from user connections
def deleteFromUserConnections(user_id, conName):
    delConnQ = 'DELETE FROM user_connections WHERE uid={uid} AND faculty_id=(SELECT id FROM ' \
               'faculty WHERE name="{conn}");'.format(uid=user_id, conn=conName)
    with engine.connect() as con:
        con.execute(text(delConnQ))
        con.commit()
    return


# Delete from user works table
def deleteFromUsersWork(user_id, prePubID):
    delWorkQ = 'DELETE FROM user_work WHERE uid={uid} AND pre_pub_id={prePubID};'.format(uid=user_id, prePubID=prePubID)
    with engine.connect() as con:
        con.execute(text(delWorkQ))
        con.commit()
    return


# Delete from favorite keywords
def deleteFromFavoritePublications(user_id, pubID):
    delFavPubQ = 'DELETE FROM user_favorite_publication WHERE uid={uid} AND ' \
                 'publication_id={pubID};'.format(uid=user_id, pubID=pubID)
    with engine.connect() as con:
        con.execute(text(delFavPubQ))
        con.commit()
    return


# Delete from favorite faculty
def deleteFromFavoriteFaculty(user_id, facName):
    delFavFacQ = 'DELETE FROM user_favorite_faculty WHERE uid={uid} AND faculty_id IN' \
                 ' (SELECT id FROM faculty WHERE name="{name}");'.format(uid=user_id, name=facName)
    with engine.connect() as con:
        con.execute(text(delFavFacQ))
        con.commit()
    return
