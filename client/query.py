
from xml.dom import InvalidAccessErr
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import (QueryOptions, ClusterOptions)
from couchbase.exceptions import (InvalidArgumentException, CouchbaseException)

from datetime import timedelta

# Per ogni giorno del mese trovare il numero totale di accessi ai POI
q1_name = "DailyPOIAccess"
q1 = f'''
PREPARE {q1_name} AS
SELECT AP.poi, AP.day, IFMISSINGORNULL(CNT.counter, 0) AS counter
FROM (
    -- Ottiene tutte le coppie (Giorno, POI) estraibili dai dati
    SELECT META(P).id AS poi, DS.day
    FROM Couchcard.data.pois P, (
        SELECT META(D).id as day
        FROM Couchcard.data.days D
        WHERE META(D).id BETWEEN "2020-01-01" AND "2020-02-01"
    ) AS DS
) AS AP LEFT JOIN (
    -- Ottiene tutte le coppie (Giorno, POI) presenti e il numero associato di swipes
    SELECT META(D).id AS day, P.poi, ARRAY_COUNT(P.swipes) AS counter
    FROM Couchcard.data.days AS D UNNEST D.pois P
    WHERE META(D).id BETWEEN $date AND DATE_ADD_STR($date, 1, "month")
) AS CNT
ON AP.poi = CNT.poi AND AP.day = CNT.day;
'''

# In un giorno del mese trovare POI con numero massimo e minimo di accessi
q2_name = "BestWorstPOIDaily"
q2 = f'''
PREPARE {q2_name} AS
WITH POIGRPS AS (
    SELECT RES.swipes, ARRAY_AGG(RES.poi) AS pois
    FROM (
        -- Conta il numero di accessi ad un POI, anche se questo non appare nella giornata
        SELECT META(ALLPOI).id as poi, IFMISSINGORNULL(CNT.swipes, 0) AS swipes
        FROM Couchcard.data.pois ALLPOI LEFT JOIN (
            SELECT P.poi, ARRAY_COUNT(P.swipes) AS swipes
            FROM Couchcard.data.days D UNNEST D.pois P
            WHERE META(D).id BETWEEN $date AND DATE_ADD_STR($date, 1, "day")
        ) AS CNT
        ON META(ALLPOI).id = CNT.poi
    ) AS RES
    GROUP BY RES.swipes
)
SELECT MAXIM.swipes AS max_swipes, 
       MAXIM.pois   AS max_pois, 
       MINIM.swipes AS min_swipes, 
       MINIM.pois   AS min_pois
FROM (
    SELECT PG.swipes, PG.pois FROM POIGRPS PG
    ORDER BY PG.swipes DESC
    LIMIT 1
) AS MAXIM, (
    SELECT PG.swipes, PG.pois FROM POIGRPS PG
    ORDER BY PG.swipes ASC
    LIMIT 1
) AS MINIM;
'''

# Dato un profilo VC, trovare i codici delle VC di quel profilo con almeno 3 strisciate in un giorno, 
# riportandole tutte e 3
q3_name = "ThreeSwipesVC"
q3 = f'''
PREPARE {q3_name} AS
SELECT META(C).id AS card, S.swipe_date, ARRAY_AGG({{ S.poi_device, S.poi_name, S.swipe_time }}) AS swipes, COUNT(*) AS swipe_count
FROM Couchcard.data.cards C UNNEST C.swipes S
WHERE C.type = $profile
GROUP BY META(C).id, S.swipe_date
HAVING COUNT(*) > 3;
'''

# Initialize queries
def setup(cluster):
    print(f"Preparing standard queries...", end='')
    try:
        prep1 = cluster.query(q1)
        prep2 = cluster.query(q2)
        prep3 = cluster.query(q3)
        print("Done")

    except CouchbaseException as e:
        print("Error!")
        print(e)
        exit(-1)


# Precompila queries nel cluster
def initialize(credentials, node_ip) -> Cluster:

    username = credentials["username"]
    password = credentials["password"]

    print(f"Connecting to cluster at {node_ip} with (username: {username}, password: {password})... ", end='')
    try:
        auth = PasswordAuthenticator(username, password)
        cluster = Cluster(node_ip, ClusterOptions(auth))
        cluster.wait_until_ready(timedelta(seconds = 5))
        print("Done!")
    
    except InvalidArgumentException as e:
        print("Error!")
        print(e)
        exit(-1)

    setup(cluster)
    return cluster


# Per ogni giorno del mese trovare il numero totale di accessi ai POI
def query_1(cluster: Cluster, m: str):
    date = f"2020-{m}-01"
    row_iter = cluster.query(
        q1, QueryOptions(named_parameters = { 'date' : date })
    )

    print("Results:")
    for row in row_iter:
        print(row)


# In un giorno del mese trovare POI con numero massimo e minimo di accessi
def query_2(d: str, m: str, y: str):
    pass


# Dato un profilo VC, trovare i codici delle VC di quel profilo con almeno 3 strisciate in un giorno, 
# riportandole tutte e 3
def query_3(profilo: str):
    pass
