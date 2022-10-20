
import csv
from turtle import back
import uuid
from datetime import timedelta
from couchbase.cluster import Cluster, ClusterOptions 
from couchbase.auth import PasswordAuthenticator

import actions
import query

# Interface node IP
interface_ip = "couchbase://localhost"

# Connection credentials to server
credentials = {
    "username" : "admin",
    "password" : "password"
}


def setup_query_1(): 
    m = actions.month()
    query.query_1(m)


def setup_query_2():
    d, m, y = actions.day()
    query.query_2(d, m, y)


def setup_query_3():
    p = actions.profiles()
    query.query_3(p)


def setup_query():
    query_map = {
        '1' : setup_query_1,
        '2' : setup_query_1,
        '3' : setup_query_3
    }
    
    query = actions.stored_queries()
    if query != 'e': query_map[query]()

# Aggiunge un CSV al cluster
def add_csv(cluster: Cluster):
    
    swipes = cluster.bucket("couchcard").scope("data").collection("swipes")

    path = actions.filename()
    with open(path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)

        batch_size = 10000
        batch = 0
        items = 0

        documents = { }
        for i, row in enumerate(reader):
            if i == 0: continue

            items += 1

            # swipe_date,swipe_time,poi_name,poi_device,card_id,card_activation,card_type
            id = str(uuid.uuid4())
            documents[id] = {
                "swipe_date"        : row[0],
                "swipe_time"        : row[1],
                "poi_name"          : row[2],
                "poi_device"        : row[3],
                "card_id"           : row[4],
                "card_activation"   : row[5],
                "card_type"         : row[6]
            }

            if items == batch_size:
                swipes.insert_multi(documents)
                print(f"Batch {batch}, inserted {items} elements")
                documents.clear()
                
                batch += 1
                items = 0

        if items != 0:
            swipes.insert_multi(documents)
            print(f"Inserted {batch} elements")
            documents.clear()


# IP of the server
if __name__ == "__main__":
    print("HELLO")
    cluster = query.initialize(credentials, node_ip=interface_ip)

    # All availalbe actions
    action_map = {
        'x' : setup_query,
        'a' : add_csv
    }

    action = '0'
    while action != 'e':
        action = actions.menu()

        if action == 'x': 
            setup_query()
        elif action == 'a': 
            add_csv(cluster)
