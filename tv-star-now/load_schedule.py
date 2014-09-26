#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Load crawled TV schedule information into MongoDB"


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

    parser.add_argument("--sched-file", dest="scheduleFileName", required=True,
                        help="schedule information file name")
    args = parser.parse_args()

    return args


def main(scheduleFileName):
    """
    Load crawled TV schedule information into MongoDB.
    """

    # Connect to DB
    try:
        conn = Connection(host="localhost", port=21017)
    except ConnectionFailure as e:
        sys.stderr.write("cannot connect to MongoDB: {}".format(e))

    # Get handle of collection
    handle = conn["tv-star-now"]

    # Insert data
    with open(scheduleFileName, "r", encoding="utf-8") as scheduleFile:
        for line in scheduleFile:
            scheduleItem = ujson.loads(line.strip())
            handle.schedule.insert(scheduleItem, safe=True)

    # Create index
    # handle.schedule.create_index("programId")
    # handle.schedule.create_index("cast")
    # handle.schedule.create_index("episodes.episodeNum")
    # handle.schedule.create_index("episodes.episodeGuests")


#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.scheduleFileName)
