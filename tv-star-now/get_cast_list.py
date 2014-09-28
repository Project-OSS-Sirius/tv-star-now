#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Get cast (and guest) list from TV program information file"


import argparse
import collections
import ujson


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


def getSecondElem(seq):
    """
    Get the second element of give sequence.
    """

    return seq[1]


def main(progInfoFileName):
    """
    Get cast (and guest) list from TV program information file.
    """

    castCount = collections.Counter()

    with open(progInfoFileName, "r", encoding="utf-8") as progInfoFile:
        for line in progInfoFile:
            progInfo = ujson.loads(line.strip())
            if not progInfo["cast"]:
                continue
            for member in progInfo["cast"]:
                castCount[member] += 1
            if not progInfo["episodes"]:
                continue
            for episode in progInfo["episodes"]:
                for member in episode["episodeGuests"]:
                    castCount[member] += 1

    for member, count in sorted(castCount.items(), key=getSecondElem,
                                reverse=True):
        print("{}\t{}".format(member, count))

#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.progInfoFileName)
