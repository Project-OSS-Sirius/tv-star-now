#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Hwanho Lee"
__email__ = "hanwho633@naver.com"
__copyright__ = "Copyright (c) 2014 by Hwanho Lee"
__desc__ = "Crawl TV program information from http://movie.daum.net"


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

    parser.add_argument("--main-cat", dest="mainCatName", required=True,
                        help="program main category")
    parser.add_argument("--sub-cat", dest="subCatName", default=None,
                        help="program sub-category")
    parser.add_argument("--output-file",
                        dest="outputFileName", required=True,
                        help="output file name")
    parser.add_argument("--min-rating", dest="minRating", default=0,
                        type=int, help="minimum rating")

    args = parser.parse_args()

    return args


def main(mainCatName, subCatName, outputFileName, minRating):
    """
    Crawl TV program information from http://movie.daum.net.
    """

    tvInfo = tvinfo.ProgramInfo()
    tvInfo.setProgCatNames(mainCatName, subCatName)
    tvInfo.setProgMinRating(minRating)
    tvInfo.setOutputFile(outputFileName)
    tvInfo.getProgramInfo()


#
# main
#


if __name__ == "__main__":
    args = parseCmdLineArgs()
    main(args.mainCatName, args.subCatName, args.outputFileName,
         args.minRating)
