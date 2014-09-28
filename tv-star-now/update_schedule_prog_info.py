#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Update TV schedule and program information"


import argparse
import logging
import ujson
import pymongo
import tvinfo
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
                        help="destination date")
    parser.add_argument("--chan-type", dest="chanType", required=True,
                        help="channel type")
    parser.add_argument("--chan-cat", dest="chanCat", required=True,
                        help="channel category")
    args = parser.parse_args()

    return args


def crawlSchedule(date, chanType, chanCat):
    """
    Crawl TV schedule for one week that the destiation date belongs.
    """

    tvInfo = tvinfo.ScheduleInfo(logging.DEBUG)
    tvInfo.setDate(date)
    tvInfo.setChanTypeCat(chanType, chanCat)
    schedule = tvInfo.digSchedule()

    return schedule


def updateSchedule(host, port, schedule):
    """
    Update schedule.
    """

    client = pymongo.MongoClient(host=host, port=port)
    db = client["tv-star-now"]
    coll = db["schedule"]

    for scheduleItem in schedule:
        # Add datetime object property
        dateStr = scheduleItem["date"]
        timeStr = scheduleItem["time"]
        scheduleItem["dateTime"] = str2dateTime(dateStr, timeStr)

        # Upsert
        coll.save(scheduleItem)

    client.close()


def updateProgInfo(host, port, schedule):
    """
    Update program information.
    """

    client = pymongo.MongoClient(host=host, port=port)
    db = client["tv-star-now"]
    programsColl = db["programs"]
    episodesColl = db["episodes"]
    celebsColl = db["celebrities"]

    programIds = [s["programId"] for s in schedule]
    programIds = list(set(programIds))

    for programId in programIds:
        result = programsColl.find_one({"programId": programId})

        if not result:
            programInfo = crawlProgramInfo(programId)
            putProgramInfo(programsColl, episodesColl, celebsColl,
                           programInfo)

    ProgramIdEpisodeNums = [(s["programId"], s["episodeNum"])
                            for s in schedule]

    ProgramIdEpisodeNums = list(set(ProgramIdEpisodeNums))

    for programId, episodeNum in ProgramIdEpisodeNums:
        if not episodeNum:
            continue

        query = {
            "programId": programId,
            "episodeNum": episodeNum
        }

        result = episodesColl.find_one(query)

        if not result:
            episodes = crawlRecentEpisodes(programId)

            if episodes:
                putEpisodes(programsColl, episodesColl, celebsColl, episodes)


def crawlProgramInfo(programId):
    """
    crawl single program information.
    """

    tvInfo = tvinfo.ProgramInfo()


def main(host, port, date, chanType, chanCat):
    """
    Update TV schedule and program information
    """

    print("Crawling schedule.")
    schedule = crawlSchedule(date, chanType, chanCat)
    print("Updating schedule.")
    updateSchedule(host, port, schedule)
    print("Updating program information.")
    updateProgInfo(host, port, schedule)


#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.host, args.port, args.date, args.chanType, args.chanCat)
