#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Insert crawled TV program information into MongoDB"


import argparse
import logging
import ujson
import pymongo
from tvinfo import ProgramInfo


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
    parser.add_argument("--prog-files", dest="progInfoFiles", required=True,
                        type=argparse.FileType("r"), nargs="+",
                        help="program information file names")
    args = parser.parse_args()

    return args


def createPrograms(db):
    """
    Create Programs collection.
    """

    # Create collection if not exists.
    if "programs" not in db.collection_names():
        db.create_collection("programs")

    programsColl = db["programs"]

    # Create index
    #programsColl.ensure_index("programId", unique=True, drop_dupes=True)
    programsColl.ensure_index("programId")
    programsColl.ensure_index("cast")

    return programsColl


def createEpisodes(db):
    """
    Create Episodes collection.
    """

    # Create collection if not exists.
    if "episodes" not in db.collection_names():
        db.create_collection("episodes")

    episodesColl = db["episodes"]

    # Create index
    #episodesColl.ensure_index("programId", unique=True, drop_dups=True)
    episodesColl.ensure_index("programId")
    episodesColl.ensure_index("cast")
    episodesColl.ensure_index("guests")
    #episodesColl.ensure_index("episodeNum", unique=True, drop_dups=True)
    episodesColl.ensure_index("episodeNum")

    return episodesColl


def createCelebrities(db):
    """
    Create celebrities collection.
    """

    # Create collection if not exists.
    if "celebrities" not in db.collection_names():
        db.create_collection("celebrities")

    celebritiesColl = db["celebrities"]

    # Create index
    celebritiesColl.ensure_index("appearCount", pymongo.DESCENDING)

    return celebritiesColl


def insertProgramCelebs(programsColl, celebritiesColl, progInfo):
    """
    Insert program basic information and celebrities.
    """

    programInfo = ProgramInfo(logging.DEBUG)
    progBasicInfo, celebs = programInfo.getProgBasicInfoCelebs(progInfo)
    print(progBasicInfo)

    programsColl.save(progBasicInfo)

    # TODO
    # Need to run how to upsert.

    for celeb in celebs:
        print(celeb)
        celebritiesColl.update({"name": celeb["name"]},
                               {"$inc": {"appearCount": celeb["appearCount"]}},
                               safe=True, upsert=True)


def insertEpisodesCelebs(episodesColl, celebritiesColl, progInfo):
    """
    Insert episodes and celebrities.
    """

    programInfo = ProgramInfo(logging.DEBUG)
    episodes, celebs = programInfo.getEpisodesCelebs(progInfo)

    if not episodes:
        return

    for episode in episodes:
        episodesColl.save(episode)

    for celeb in celebs:
        celebritiesColl.update({"name": celeb["name"]},
                               {"$inc": {"appearCount": celeb["appearCount"]}},
                               safe=True, upsert=True)


def main(host, port, progInfoFiles):
    """
    Insert crawled TV program information into MongoDB
    """

    client = pymongo.MongoClient(host=host, port=port)
    db = client["tv-star-now"]

    programsColl = createPrograms(db)
    episodesColl = createEpisodes(db)
    celebritiesColl = createCelebrities(db)

    for progInfoFile in progInfoFiles:
        print("Reading program information from {}".format(progInfoFile.name))

        for line in progInfoFile:
            progInfo = ujson.loads(line.strip())
            print("Inserting program information and celebrities")
            insertProgramCelebs(programsColl, celebritiesColl, progInfo)
            print("Inserting episode information and celebrities")
            insertEpisodesCelebs(episodesColl, celebritiesColl, progInfo)


#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.host, args.port, args.progInfoFiles)
