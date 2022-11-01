# estabilish a connection pfrom collections import OrderedDict
from urllib.parse import quote_plus
from pymongo import MongoClient


def getConn():
    username = quote_plus('Agile')
    password = quote_plus('Agile@Fall2022')

    uri = 'mongodb+srv://' + username + ':' + password + \
        '@clusteragile.sgmrknw.mongodb.net/?retryWrites=true&w=majority'
    cluster = MongoClient(uri)

    return cluster

    # db = cluster["test"]
    # collection = db["test"]

    # collection.insert_one({"_id": 0, "name": "Pratik"})


if __name__ == '__main__':
    getConn()
