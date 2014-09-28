#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Crawl TV schedule information from http://movie.daum.net"


import argparse
import tvinfo


def parseCmdLineArgs():
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description=__desc__,
                                     epilog="Contact {} <{}> for reporting "
                                     "bugs and suggestions.\n"
                                     "{}".format(__author__, __email__,
                                                 __copyright__))

    parser.add_argument("--date", dest="date", required=True,
                        help="destination date")
    parser.add_argument("--chan-type", dest="chanType", required=True,
                        help="channel type")
    parser.add_argument("--chan-cat", dest="chanCat", required=True,
                        help="channel category")
    parser.add_argument("--output-file",
                        dest="outputFileName", required=True,
                        help="output file name")

    args = parser.parse_args()

    return args


def main(date, chanType, chanCat, outputFileName):
    """
    Crawl TV schedule information from http://movie.daum.net.
    """

    tvInfo = tvinfo.ScheduleInfo()
    tvInfo.setDate(date)
    tvInfo.setChanTypeCat(chanType, chanCat)
    tvInfo.setOutputFile(outputFileName)
    tvInfo.getSchedule()


#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.date, args.chanType, args.chanCat, args.outputFileName)
