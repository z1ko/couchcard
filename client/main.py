
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


# IP of the server
if __name__ == "__main__":
    print("HELLO")
    cluster = query.initialize(credentials, node_ip=interface_ip)

    # All availalbe actions
    action_map = {
        'x' : setup_query
    }

    action = actions.menu()
    while action != 'e':
         action_map[action]()
