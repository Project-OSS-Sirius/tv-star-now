# -*- coding: utf-8 -*-

"""
programs.py
~~~~~~~~~~~~

이 모듈은 다음포털의 영화 및 TV 정보 사이트(http://movie.daum.net)에서
TV 프로그램 정보를 수집하여 JSON 형식으로 제공하는 기능을 제공한다.

:copyright: (c) 2014 by Hwanho Lee <hwanho633@naver.com>
:license: Apache2, see LICENSE for more details.
"""


import math
import re
import logging
import bs4
from ..util import Sleep
from ..util import getHtml
from ..util import containsNum
from ..util import filterNonNums


class Programs(object):

    """
    TV 프로그램 정보 수집 클래스
    """

    # Web crawling sleep time
    _minShortTime = 3
    _maxShortTime = 6
    _minLongTime = 10
    _maxLongTime = 20

    # Web crawling retry count
    _maxRetryCnt = 3

    # urls
    _searchUrl = "http://movie.daum.net/tv/search/genre/searchProgram.do"
    _castUrl = "http://movie.daum.net/tv/detail/castcrew.do"
    _episodeUrl = "http://movie.daum.net/tv/detail/episode.do"

    # GET request parameters
    _searchParams = {
        "type": "genre",
        "startWord": 0,
        "category": None,
        "subCategory": None,
        "page": None
    }
    _castParams = {
        "tvProgramId": None
    }
    _episodeParams = {
        "tvProgramId": None,
        "page": None
    }

    # Text patterns
    _totCountRePat = u"총 (\d+)편"
    _progIdRePat = "=(\d+)$"
    _numProgsPerPage = 20
    _noCastPat = '<div class="c topBorder noborder">'
    _noEpisodesPat = u"죄송합니다. 회차 정보가 존재하지 않습니다."

    def __init__(self):
        requestsLogger = logging.getLogger("requests")
        requestsLogger.setLevel(logging.WARNING)
        self._sleep = Sleep(self._minShortTime, self._maxShortTime,
                            self._minLongTime, self._maxLongTime)

    def getPrograms(self, mainCatName, mainCatId, subCatName, subCatId,
                    page=1):
        """
        Search TV programs from Daum.
        """

        self._searchParams["category"] = mainCatId
        self._searchParams["subCategory"] = subCatId
        self._searchParams["page"] = page

        html = getHtml(self._searchUrl, self._searchParams, self._sleep,
                       self._maxRetryCnt)
        soup = bs4.BeautifulSoup(html)

        result = {}
        totalCount = self._extTotCount(soup)
        result["totalCount"] = totalCount
        result["programs"] = self._extPrograms(soup, mainCatName, subCatName)
        result["lastPageNum"] = self._getLastProgPageNum(totalCount)

        return result

    def _extPrograms(self, soup, mainCatName, subCatName):
        programs = []
        programElems = soup.find_all("tr", class_="norm")

        for elem in programElems:
            program = {}

            try:
                titleElem = elem.find("p", class_="posterWrap").find("a")
                title = titleElem.string
                m = re.search(self._progIdRePat, titleElem["href"])
                programId = int(m.group(1))
                chanName = elem.find("span", class_="cast").string
                ratingAverage = float(elem.find("em").string)
            except Exception as e:
                raise RuntimeError("Cannot extract programs: {}".format(e))

            program["mainCatName"] = mainCatName
            program["subCatName"] = subCatName
            program["title"] = title
            program["programId"] = programId
            program["channelName"] = chanName
            program["ratingAverage"] = ratingAverage
            programs.append(program)

        return programs

    def _extTotCount(self, soup):
        """
        Extract total count of the search result.
        """

        try:
            totCountStr = soup.find("em", class_="fs12 fc4").string
            m = re.search(self._totCountRePat, totCountStr)
            totCount = int(m.group(1))
        except Exception as e:
            raise ValueError("Cannot extract total count: {}".format(e))

        return totCount

    def _getLastProgPageNum(self, totCount):
        """
        Get last program page number.
        """

        lastProgPageNum = math.ceil(totCount / self._numProgsPerPage)

        return lastProgPageNum

    def getCast(self, programId):
        """
        Get cast of a program.
        """

        result = {
            "programId": programId,
            "cast": None
        }
        self._castParams["tvProgramId"] = programId

        try:
            html = getHtml(self._castUrl, self._castParams, self._sleep,
                           self._maxRetryCnt)

            if self._noCastPat not in html:
                return result

            soup = bs4.BeautifulSoup(html)
            castWrapElem = soup.find("div", class_="clearfix")
            castElems = castWrapElem.find_all("a", class_="em b")
            cast = [castElem.string for castElem in castElems]
        except Exception as e:
            raise RuntimeError("Cannot get cast for program "
                               "{}: {}".format(programId, e))

        result["cast"] = cast

        return result

    def getEpisodes(self, programId, page=1):
        """
        Get episodes information for given program ID.
        """

        result = {
            "programId": programId,
            "episodes": None,
            "isLastPage": None
        }
        self._episodeParams["tvProgramId"] = programId
        self._episodeParams["page"] = page

        html = getHtml(self._episodeUrl, self._episodeParams, self._sleep,
                       self._maxRetryCnt)

        if self._noEpisodesPat in html:
            raise ValueError("No episode information: "
                             "programId={}".format(programId))

        soup = bs4.BeautifulSoup(html)
        episodes = self._extEpisodes(soup)
        result["episodes"] = episodes
        result["isLastPage"] = self._isLastPage(soup)

        return result

    def _extEpisodes(self, soup):
        episodes = []

        try:
            episodeElems = soup.find("div", class_="c").find_all("li")

            for elem in episodeElems:
                episode = {}
                episodeNum, episodeDate = self._extEpisodeNumDate(elem)
                episode["episodeNum"] = episodeNum
                episode["episodeDate"] = episodeDate
                episodeGuests = self._extEpisodeGuests(elem)
                episode["episodeGuests"] = episodeGuests
                episodes.append(episode)
        except Exception as e:
            raise ValueError("Canot extract episodes: {}".format(e))

        return episodes

    def _extEpisodeNumDate(self, elem):
        """
        Extract episode number and date.
        """

        try:
            episodeNumElem = elem.find("span", class_="episode_num")
            episodeNumDate = episodeNumElem.string.strip()
            episodeNum, episodeDate = episodeNumDate.split("\n")
        except Exception as e:
            raise ValueError("Cannot extract episode number and date: "
                             "{}".format(e))

        episodeNum = episodeNum.strip()

        if containsNum(episodeNum):
            episodeNum = filterNonNums(episodeNum)

        episodeDate = filterNonNums(episodeDate.strip())

        return episodeNum, episodeDate

    def _extEpisodeGuests(self, elem):
        """
        Extract episode guests.
        """

        guests = []

        try:
            guestElems = elem.find_all("a", class_="em")

            for guestElem in guestElems:
                guest = guestElem.string.strip()
                guests.append(guest)
        except Exception as e:
            raise ValueError("Cannot extract episode guests: {}".format(e))

        return guests

    def _isLastPage(self, soup):
        """
        Check if current page is the last page.
        """

        currentPageElem = soup.find("span", class_="current")
        nextPageLinks = currentPageElem.find_next_siblings("a")

        if nextPageLinks:
            return False

        return True
