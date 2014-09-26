# -*- coding: utf-8 -*-


import logging
import itertools
import bs4
from ..util import Sleep
from ..util import getHtml
from ..util import extTxtElem
from ..util import filterNonNums
from ..util import getColumnDate
from ..util import getFirstElem


class Schedule(object):

    """
    TV schedule class.
    """

    # urls
    _chanUrls = {
        1: "http://movie.daum.net/tv/chart/public/chartTable.do",
        2: "http://movie.daum.net/tv/chart/cable/chartTable.do",
        3: "http://movie.daum.net/tv/chart/skylife/chartTable.do",
        10: "http://movie.daum.net/tv/chart/publicChannels/chartTable.do"
    }

    # GET request parameters
    _chanParams = {
        "channelType": 0,
        "date": None,
        "genre": None,
        "channelId": 0,
        "page": 1
    }

    # Web crawling sleep time
    _minShortTime = 1
    _maxShortTime = 2
    _minLongTime = 3
    _maxLongTime = 4

    # Web crawling retry count
    _maxRetryCnt = 3

    def __init__(self):
        requestsLogger = logging.getLogger("requests")
        requestsLogger.setLevel(logging.WARNING)
        self._sleep = Sleep(self._minShortTime, self._maxShortTime,
                            self._minLongTime, self._maxLongTime)

    def getChanSchedule(self, date, chanTypeId, chanId, genre="", page=1):
        """
        Get TV broadcasting schedule.
        """

        url = self._chanUrls[chanTypeId]
        self._chanParams["channelType"] = chanTypeId
        self._chanParams["date"] = date
        self._chanParams["genre"] = genre
        self._chanParams["channelId"] = chanId
        self._chanParams["page"] = page

        html = getHtml(url, self._chanParams, self._sleep,
                       self._maxRetryCnt)
        soup = bs4.BeautifulSoup(html)
        schedule = self._extSchedule(soup, date)

        return schedule

    def _extSchedule(self, soup, date):
        """
        Extract TV schedule.
        """

        scheduleItems = []
        tableElems = soup.find_all("table", class_="tvTimeTable")

        for tableElem in tableElems:
            subScheduleItems = self._parseTable(tableElem, date)
            scheduleItems.extend(subScheduleItems)

        scheduleItems = sorted(scheduleItems, key=getFirstElem)
        schedule = []

        for dstDate, scheduleGroup in itertools.groupby(scheduleItems,
                                                        key=getFirstElem):
            scheduleElem = {
                "date": dstDate,
                "daySchedule": []
            }
            for _, time, progId, title in scheduleGroup:
                scheduleElem["daySchedule"].append({"time": time,
                                                    "programId": progId,
                                                    "title": title})

            schedule.append(scheduleElem)

        return schedule

    def _parseTable(self, tableElem, date):
        """
        Parse schedule table.
        """

        hours = self._extHours(tableElem)
        colElems = tableElem.find_all("td", class_="7")
        scheduleItems = []

        for colIdx, colElem in enumerate(colElems):
            rawColItems = []
            paraElems = colElem.find_all("p")

            for paraElem in paraElems:
                aElem = paraElem.find("a")

                if not aElem:
                    continue

                minute = paraElem.find("em").string
                progLink = aElem["href"]
                title = aElem["title"]
                progId = int(extTxtElem(progLink, "tvProgramId=(\d+)"))
                rawColItems.append((minute, progId, title))

            colItems = self._conColItems(rawColItems, colIdx, date, hours)

            if colItems:
                scheduleItems.extend(colItems)

        return scheduleItems

    def _extHours(self, tableElem):
        """
        extract hours from schedule table.
        """

        hourElems = tableElem.find_all("td", class_="time")
        hours = [e.text for e in hourElems]
        hours = [filterNonNums(h).zfill(2) for h in hours]

        return hours

    def _conColItems(self, rawColItems, colIdx, date, hours):
        """
        Construct column items.
        """

        colItems = []
        colDate = getColumnDate(colIdx, date)
        hour = hours[colIdx//7]

        for minute, progId, title in rawColItems:
            colItem = (colDate, hour+minute, progId, title)
            colItems.append(colItem)

        return colItems
