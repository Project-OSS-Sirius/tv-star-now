#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Load crawled TV program information into MongoDB"


import sys
import argparse
import ujson
from pymongo import Connection
from pymongo.erros import ConnectionFailure


def parseCmdLineArgs():
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description=__desc__,
                                     epilog="Contact {} <{}> for reporting "
                                     "bugs and suggestions.\n"
                                     "{}".format(__author__, __email__,
                                                 __copyright__))

    parser.add_argument("--prog-file", dest="progInfoFileName", required=True,
                        help="program information file name")
    args = parser.parse_args()

    return args


def main(progInfoFileName):
    """
    Load crawled TV program information into MongoDB
    """

    # Connect to DB
    try:
        conn = Connection(host="localhost", port=21017)
    except ConnectionFailure as e:
        sys.stderr.write("cannot connect to MongoDB: {}".format(e))

    # Get handle of collection
    handle = conn["tv-star-now"]

    # Insert data
    with open(progInfoFileName, "r", encoding="utf-8") as progInfoFile:
        for line in progInfoFile:
            progInfo = ujson.loads(line.strip())
            handle.programs.insert(progInfo, safe=True)

    # Create index
    handle.programs.create_index("programId")
    handle.programs.create_index("cast")
    handle.programs.create_index("episodes.episodeNum")
    handle.programs.create_index("episodes.episodeGuests")


#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.progInfoFileName)
