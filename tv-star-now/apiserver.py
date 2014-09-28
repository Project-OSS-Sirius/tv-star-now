#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Serve TV program episode and schedule information in REST style"


import argparse
import pymongo
from flask import Flask
from flask import redirect
from flask.ext.restful import Api
from flask_restful_swagger import swagger
from restapi import ScheduleDB
from restapi import ScheduleSearch
from restapi import ScheduleList
from restapi import CelebritiesList


def parseCmdLineArgs():
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description=__desc__,
                                     epilog="Contact {} <{}> for reporting "
                                     "bugs and suggestions.\n"
                                     "{}".format(__author__, __email__,
                                                 __copyright__))

    parser.add_argument("--mongo-host", default="localhost", dest="mongoHost",
                        help="MongoDB host")
    parser.add_argument("--mongo-port", type=int, default=27017,
                        dest="mongoPort", help="MongoDB port")
    parser.add_argument("--server-host", required=True, dest="serverHost",
                        help="API server address")
    parser.add_argument("--server-port", type=int, default=5000,
                        dest="serverPort", help="API server port")

    args = parser.parse_args()

    return args


def main(mongoHost, mongoPort, serverHost, serverPort):
    """
    Serve TV program episode and schedule information in REST style
    """

    # Connect to MongoDB and create a DB instance
    mongoClient = pymongo.MongoClient(host=mongoHost, port=mongoPort)
    db = ScheduleDB(mongoClient)

    # Set up Flask app with Swagger document
    app = Flask(__name__)
    api = swagger.docs(
        Api(app),
        basePath="http://{}:{}".format(serverHost, serverPort)
    )

    # Redirect / to API document
    @app.route("/")
    def index():
        return redirect("/api/spec.html")

    # Register API methods
    api.add_resource(ScheduleSearch.make(db), "/schedule/search")
    api.add_resource(ScheduleList.make(db), "/schedule/list")
    api.add_resource(CelebritiesList.make(db), "/celebrities/list")

    # Run the app
    app.run(host=serverHost, port=serverPort)

#
# main
#

if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.mongoHost, args.mongoPort, args.serverHost, args.serverPort)
