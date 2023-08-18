from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))


def findFacultyPath(tx, faculty1, faculty2):
    q = 'profile match (f1:FACULTY), (f2:FACULTY), path=shortestPath((f1)-[:PUBLISH*]-(f2)) WHERE f1.name=$name1 and ' \
        'f2.name=$name2 return path limit 5'
    paths = tx.run(q, name1=faculty1, name2=faculty2)
    nodes = []
    for path in paths:
        allNodes = path['path'].nodes
        tempNodes = []
        for node in allNodes[::2]:
            tempNodes.append({"data": {"id": node["id"], "label": node["name"]}})
        len_nodes = len(tempNodes)
        for i in range(len_nodes - 1):
            tempNodes.append({"data": {"source": tempNodes[i]['data']['id'], "target": tempNodes[i + 1]['data']['id'],
                                       "label": 'Co-Authors'}})
        nodes.extend(tempNodes)
    return nodes


def findKeywordPath(tx, faculty, keyword, university):
    q = 'profile match (f1:FACULTY),(k:KEYWORD)<--(f2:FACULTY)-->(inst:INSTITUTE), path=shortestPath((f1)-[' \
        ':INTERESTED_IN*]-(f2)) WHERE f1.name=$name and k.name=$key and inst.name=$uni return path limit 5'
    paths = tx.run(q, name=faculty, key=keyword, uni=university)
    # print(paths)
    nodes = []
    for path in paths:
        allNodes = path['path'].nodes
        tempNodes = []
        for node in allNodes[::2]:
            tempNodes.append({"data": {"id": node["id"], "label": node["name"]}})
        len_nodes = len(tempNodes)
        for i in range(len_nodes - 1):
            tempNodes.append({"data": {"source": tempNodes[i]['data']['id'], "target": tempNodes[i + 1]['data']['id'],
                                       "label": 'Co-Authors'}})
        nodes.extend(tempNodes)
    return nodes


def findUniversityPath(tx, affiliatedUniversity, keyword, interestedUniversity):
    q = 'profile match (f1:FACULTY)-->(inst1:INSTITUTE),(k:KEYWORD)<--(f2:FACULTY)-->(inst2:INSTITUTE), ' \
        'path=shortestPath((f1)-[:PUBLISH*]-(f2)) WHERE inst1.name=$uni1 and k.name=$key and inst2.name=$uni2 return ' \
        'path limit 5'
    paths = tx.run(q, uni1=affiliatedUniversity, key=keyword, uni2=interestedUniversity)
    # print(paths)
    nodes = []
    for path in paths:
        allNodes = path['path'].nodes
        tempNodes = []
        for node in allNodes[::2]:
            tempNodes.append({"data": {"id": node["id"], "label": node["name"]}})
        len_nodes = len(tempNodes)
        for i in range(len_nodes - 1):
            tempNodes.append({"data": {"source": tempNodes[i]['data']['id'], "target": tempNodes[i + 1]['data']['id'],
                                       "label": 'Co-Authors'}})
        nodes.extend(tempNodes)
    return nodes


# Get Connection between two faculties
def getConnectionsToFaculty(knownFaculty, unknownFaculty):
    with driver.session(database="academicworld") as session:
        result = session.execute_read(findFacultyPath, knownFaculty, unknownFaculty)
        return result


# Get Connection between a know faculty and some faculty working on some keyword at some university
def getConnectionsForKeywordByFac(knownFaculty, interestedKeyword, interestedUniversity):
    # print(knownFaculty)
    # print(interestedKeyword)
    # print(interestedUniversity)
    with driver.session(database="academicworld") as session:
        result = session.execute_read(findKeywordPath, knownFaculty, interestedKeyword, interestedUniversity)
        return result


# Get Connection between a know faculty and some faculty working on some keyword at some university
def getConnectionsForKeywordByUni(affiliatedUniversity, interestedKeyword, interestedUniversity):
    # print(affiliatedUniversity)
    # print(interestedKeyword)
    # print(interestedUniversity)
    with driver.session(database="academicworld") as session:
        result = session.execute_read(findUniversityPath, affiliatedUniversity, interestedKeyword, interestedUniversity)
        return result


driver.close()
