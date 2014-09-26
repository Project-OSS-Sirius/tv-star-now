# -*- coding: utf-8 -*-


import logging
import time
import ujson
from .daumtv import Programs


class ProgramInfo(object):

    # TV program categories

    _mainCatNameIds = {
        u"국내드라마": 1,
        u"해외드라마": 2,
        u"연예/오락": 3,
        u"시사교양": 4,
        u"애니메이션": 5,
        u"기타": 6
    }

    _subCatNameIds = {
        u"미국드라마": 2,
        u"일본드라마": 3,
        u"기타국가드라마": 4,
        u"게임/스포츠": 5,
        u"리얼리티쇼": 6,
        u"시트콤": 7,
        u"연예/오락": 8,
        u"연예정보/영화정보": 9,
        u"음악": 10,
        u"경제/재테크": 11,
        u"어린이/교육": 12,
        u"문화/생활": 13,
        u"다큐멘터리/종교": 14,
        u"시사교양": 15,
        u"뉴스": 16
    }

    _mainSubCatNames = {
        u"해외드라마": [
            u"미국드라마", u"일본드라마", u"기타국가드라마"
        ],
        u"연예/오락": [
            u"게임/스포츠", u"리얼리티쇼", u"시트콤", u"연예/오락", u"연예정보/영화정보",
            u"음악"
        ],
        u"시사교양": [
            u"경제/재태크", u"어린이/교육", u"문화/생활", u"다큐멘터리/종교", u"시사교양",
            u"뉴스"
        ]
    }

    _minRatingAverage = 0.0
    _maxRatingAverage = 10.0

    def __init__(self):
        """
        Initialize members.
        """

        self._setLogger()
        self._startTime = time.time()
        self._programs = Programs()

    def __del__(self):
        """
        Clean up and display elapsed time.
        """

        elapsedTime = time.time() - self._startTime
        mins, secs = divmod(elapsedTime, 60)
        hours, mins = divmod(mins, 60)
        self._logger.info("Total elapsed time: %02d:%02d:%02d" %
                          (hours, mins, secs))

    def _setLogger(self):
        """
        Set logger.
        """

        formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s "
                                      "%(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self._logger = logging.getLogger(__file__)
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._logger.propagate = 0

    def _validateProgCatNames(self, mainCatName, subCatName):
        """
        Validate main and sub category names.
        """

        if mainCatName not in self._mainCatNameIds:
            raise ValueError("Invalid category name: {}".format(mainCatName))

        if subCatName and subCatName not in self._mainSubCatNames[mainCatName]:
            raise ValueError("Invalid sub-category Name: "
                             "{}".format(subCatName))

    def _validateProgMinRating(self, minRating):
        """
        Validate minimum rating.
        """

        if not self._minRatingAverage <= minRating <= self._maxRatingAverage:
            raise ValueError("Invalid minimum rating: {}".format(minRating))

    def setProgCatNames(self, mainCatName, subCatName):
        """
        Set program main and sub category names.
        """

        self._validateProgCatNames(mainCatName, subCatName)
        self._mainCatName = mainCatName
        self._subCatName = subCatName
        self._mainCatId = self._mainCatNameIds[mainCatName]
        self._subCatId = self._subCatNameIds.get(subCatName, "")

        self._logger.info("Program main caregory: {}".format(mainCatName))
        self._logger.info("Program sub-caregory: {}".format(subCatName))

    def setProgMinRating(self, minRating):
        """
        Set minimum ranking for filtering programs.
        """

        self._validateProgMinRating(minRating)
        self._minRating = minRating

        self._logger.info("Minimum program rating: {}".format(minRating))

    def setOutputFile(self, outputFileName):
        """
        Set output file.
        """

        try:
            self._outputFile = open(outputFileName, "w", encoding="utf-8")
        except IOError:
            raise IOError("Cannot create output file.")

        self._logger.info("Output file created: {}".format(outputFileName))

    def getProgramInfo(self):
        """
        Get program information.
        """

        page = 1
        lastPageNum = 0
        numProgs = 0

        while True:
            if page == 1:
                self._logger.info("Crawling program information: mainCat={}, "
                                  "subCat={}, "
                                  "page={}".format(self._mainCatName,
                                                   self._subCatName,
                                                   page))
            else:
                self._logger.info("Crawling program information: mainCat={}, "
                                  "subCat={}, "
                                  "page={}/{}".format(self._mainCatName,
                                                      self._subCatName,
                                                      page, lastPageNum))

            result = self._programs.getPrograms(self._mainCatName,
                                                self._mainCatId,
                                                self._subCatName,
                                                self._subCatId, page)
            programs = result["programs"]
            numProgs += len(programs)

            for program in programs:
                if program["ratingAverage"] < self._minRating:
                    continue

                program = self._addCastInfo(program)
                program = self._addEpisodeInfo(program)
                self._writeProgramInfo(program)

            lastPageNum = result["lastPageNum"]

            if lastPageNum == page:
                break

            page += 1

        self._logger.info("Total number of fetched programs: "
                          "{}".format(numProgs))
        self._logger.info("Total number of filtered-in programs: "
                          "{}".format(len(self._programInfo)))

    def _addCastInfo(self, program):
        """
        Add cast information.
        """

        programId = program["programId"]
        self._logger.info("Fetching cast information: programId={}".format(
                          programId))
        cast = self._programs.getCast(programId)
        program["cast"] = cast["cast"]

        return program

    def _addEpisodeInfo(self, program):
        """
        Add episode information.
        """

        programId = program["programId"]

        allEpisodes = []
        page = 1

        while True:
            self._logger.info("Fetching episode information: "
                              "programId={}, "
                              "page={}".format(programId, page))

            try:
                episodes = self._programs.getEpisodes(programId, page)
            except ValueError:
                self._logger.warn("No episode information: "
                                  "programId={}".format(programId))
                break

            if episodes["episodes"]:
                allEpisodes.extend(episodes["episodes"])

            if episodes["isLastPage"]:
                break

            page += 1

        program["episodes"] = allEpisodes

        return program

    def _writeProgramInfo(self, program):
        """
        Write program information to output file.
        """

        self._outputFile.write("{}\n".format(ujson.dumps(program,
                                                         ensure_ascii=
                                                         False)))
        self._outputFile.flush()
