#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Drop schedule collection from MongoDB"


import argparse
import pymongo


def parseCmdLineArgs():
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description=__desc__,
                                     epilog="Contact {} <{}> for reporting "
                                     "bugs and suggestions.\n"
                                     "{}".format(__author__, __email__,
                                                 __copyright__))

    parser.add_argument("--host", default="localhost", help="MongoDB host",
                        dest="host")
    parser.add_argument("--port", type=int, default=27017, dest="port",
                        help="MongoDB port")
    args = parser.parse_args()

    return args


def main(host, port):
    """
    Drop schedule collection from MongoDB.
    """

    client = pymongo.MongoClient(host=host, port=port)
    db = client["tv-star-now"]
    coll = db["schedule"]

    # Drop
    print("Dropping schedule collection.")
    coll.drop()

#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.host, args.port)
