# -*- coding: utf-8 -*-

import logging
import itertools
import bs4
from ..util import Sleep
from ..util import getHtml
from ..util import getThisMonday
from ..util import splitDate
from ..util import containsNum
from ..util import filterNonNums
from ..util import to24Hour
from ..util import adjustDate
from ..util import getLastWeekDay
from ..util import getThisWeekDateRange
from ..util import getFirstElem


class AuxSchedule(object):

    """
    Nate TV schedule class.
    """

    _url = "http://news.nate.com/ent/tvTable"

    # GET request parameters
    _params = {
        "mid": "e0500",
        "date": None,
        "move": None
    }

    # Web crawling sleep time
    _minShortTime = 1
    _maxShortTime = 2
    _minLongTime = 3
    _maxLongTime = 4

    # Web crawling retry count
    _maxRetryCnt = 3

    def __init__(self):
        """
        Initialize members.
        """

        requestsLogger = logging.getLogger("requests")
        requestsLogger.setLevel(logging.WARNING)
        self._sleep = Sleep(self._minShortTime, self._maxShortTime,
                            self._minLongTime, self._maxLongTime)

    def getChanSchedule(self, srcDate, linkTmpl):
        """
        Get TV broadcasting schedule.
        """

        lastWeekDate = getLastWeekDay(srcDate)
        srcDates = [srcDate, lastWeekDate]
        thisWeekDateRange = getThisWeekDateRange(srcDate)
        scheduleItems = []

        for date in srcDates:
            monDate = getThisMonday(date)
            year, mon, day = splitDate(monDate)
            link = linkTmpl.format(year, mon, day)

            self._params["date"] = monDate
            self._params["move"] = link

            html = getHtml(self._url, self._params, self._sleep,
                           self._maxRetryCnt)
            soup = bs4.BeautifulSoup(html)
            scheduleItems.extend(self._extSchedule(soup, date))

        scheduleItems = [s for s in scheduleItems
                         if s[0] in thisWeekDateRange]
        scheduleItems = sorted(scheduleItems, key=getFirstElem)
        schedule = []

        for dstDate, scheduleGroup in itertools.groupby(scheduleItems,
                                                        key=getFirstElem):
            scheduleElem = {
                "date": dstDate,
                "daySchedule": []
            }
            for _, time, title, episodeNum in scheduleGroup:
                scheduleElem["daySchedule"].append({"time": time,
                                                    "title": title,
                                                    "episodeNum": episodeNum})

            schedule.append(scheduleElem)

        return schedule

    def _extSchedule(self, soup, date):
        """
        Parse daily schedule in HTML text.
        """

        scheduleItems = []
        tableElems = soup.find_all("table", class_="timetable")

        for tableElem in tableElems:
            subScheduleItems = self._parseTable(tableElem, date)
            scheduleItems.extend(subScheduleItems)

        return scheduleItems

    def _parseTable(self, tableElem, srcDate):
        """
        Parse table element.
        """

        scheduleItems = []
        dayPart = self._extDayPart(tableElem)
        dates = self._extDates(tableElem, srcDate)
        scheduleElems = self._extScheduleElems(tableElem, dayPart)

        for i, scheduleElem in enumerate(scheduleElems):
            date = dates[i % 7]
            for time, title, episodeNum in scheduleElem:
                adjDate = adjustDate(date, time)
                scheduleItems.append((adjDate, time, title, episodeNum))

        return scheduleItems

    def _extDayPart(self, tableElem):
        """
        Extract day part.
        """

        dayPart = tableElem.find("th", class_="day").string

        return dayPart

    def _extDates(self, tableElem, date):
        """
        Extract dates from table element.
        """

        year = date[:4]
        headers = tableElem.find_all("th", width="14%")
        dates = [h.font.string for h in headers]
        dates = [year+filterNonNums(d) for d in dates]

        return dates

    def _extScheduleElems(self, tableElem, dayPart):
        """
        Extract schedule elements.
        """

        scheduleElems = []
        rows = tableElem.find("tbody").find_all("tr")

        for row in rows:
            hour = row.find("td", class_="time").string
            hour = to24Hour(hour, dayPart)
            cols = row.find_all("td", class_=None)
            for col in cols:
                colElems = []
                programInfos = col.find_all("div")
                for programInfo in programInfos:
                    text = programInfo.text.strip()
                    minute = text[:2]
                    program = text[3:]
                    title, episodeNum = self._splitTitleEpisodeNum(program)
                    if containsNum(episodeNum):
                        episodeNum = filterNonNums(episodeNum)
                    colElems.append((hour+minute, title, episodeNum))

                scheduleElems.append(colElems)

        return scheduleElems

    def _splitTitleEpisodeNum(self, program):
        """
        Split program into title and episode number.
        """

        if not program.endswith(")"):
            return program, ""

        p = program.rfind("(")
        title = program[:p].strip()
        episodeNum = program[p+1:-1].strip()

        return title, episodeNum
