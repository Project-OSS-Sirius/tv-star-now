#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Update TV schedule and program information"


import argparse
import ujson
import pymongo
from restapi.util import str2dateTime


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
    parser.add_argument("--date", dest="date", required=True,
                        help="target date")
    args = parser.parse_args()

    return args


def main(host, port, scheduleFiles):
    """
    Update TV schedule and program information
    """

    client = pymongo.MongoClient(host=host, port=port)
    db = client["tv-star-now"]

    # Create "schedule" collection if not exists.
    if "schedule" not in db.collection_names():
        db.create_collection("schedule")

    coll = db["schedule"]

    # Create index
    coll.ensure_index("date")
    coll.ensure_index("time")
    coll.ensure_index("dateTime")

    for scheduleFile in scheduleFiles:
        print("Inserting data from {}".format(scheduleFile.name))

        for line in scheduleFile:
            scheduleItem = ujson.loads(line.strip())

            # Add datetime object property
            dateStr = scheduleItem["date"]
            timeStr = scheduleItem["time"]
            scheduleItem["dateTime"] = str2dateTime(dateStr, timeStr)

            # Upsert
            coll.save(scheduleItem)

#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.host, args.port, args.scheduleFiles)
