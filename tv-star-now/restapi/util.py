# -*- coding: utf-8 -*-

import time
import random
import datetime
import re
import json
import requests


class Sleep(object):

    """
    Crawling sleep class.
    """

    def __init__(self, minShortTime=0, maxShortTime=0, minLongTime=0,
                 maxLongTime=0):
        """
        Initialize members.
        """

        self._minShortTime = minShortTime
        self._maxShortTime = maxShortTime
        self._minLongTime = minLongTime
        self._maxLongTime = maxLongTime

    def sleep(self, long=False):
        """
        Sleep for a while.
        """

        if long:
            t = random.uniform(self._minLongTime, self._maxLongTime)
        else:
            t = random.uniform(self._minShortTime, self._maxShortTime)

        time.sleep(t)


def filterNonNums(src):
    """
    Filter non-numeric characters.
    """

    dstChrs = [c for c in src if c.isdigit()]

    return "".join(dstChrs)


def splitDate(date):
    """
    Split given date string into year, month and day.
    """

    year = date[:4]
    month = date[4:6]
    day = date[6:]

    return year, month, day


def validateDate(date):
    """
    Validate date string.
    """

    try:
        year, month, day = splitDate(date)
        datetime.datetime(int(year), int(month), int(day))
    except:
        raise ValueError("Invalid date: {}".format(date))


_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) " + \
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 " + \
    "Safari/537.36"
_HEADERS = {"User-Agent": _USER_AGENT}


def getHtml(url, params, sleep, maxRetryCnt):
    """
    Get HTML for given url and parameters.
    """

    retryCnt = 0

    while True:
        try:
            response = requests.get(url, params=params,
                                    headers=_HEADERS)
            html = response.text
            break
        except Exception as e:
            if retryCnt <= maxRetryCnt:
                sleep.sleep(long=True)
                retryCnt += 1
                continue

            raise RuntimeError("Cannot get response from Daum: "
                               "{}".format(e))

    sleep.sleep()

    return html


_KO_EN_DAY_PARTS = {
    u"오전": "AM",
    u"오후": "PM",
    u"저녁": "PM",
}


def to24Hour(hour, koDayPart):
    """
    Normalize hour string.
    """

    hour = hour.replace(":", "")
    hour = hour.zfill(4)

    if koDayPart == u"오후" or (koDayPart == u"저녁" and hour >= "0700"):
        enDayPart = _KO_EN_DAY_PARTS[koDayPart]
        t = datetime.datetime.strptime(hour+enDayPart, "%I%M%p")
        hour = t.strftime("%H")
    else:
        hour = hour[:2]

    if hour == "12" and koDayPart == u"저녁":
        hour = "00"

    return hour


def extTxtElem(src, pat, newLine=False):
    """
    Extract text element using regular expression.
    """

    if newLine:
        m = re.search(pat, src, re.S)
    else:
        m = re.search(pat, src)

    if not m:
        return None

    txt = m.group(1)

    return txt


def getColumnDate(colIdx, date):
    """
    Get the date of current column.
    """

    colWeekDay = colIdx % 7
    year, mon, day = splitDate(date)
    curDate = datetime.date(int(year), int(mon), int(day))
    curWeekDay = curDate.isoweekday()

    if colWeekDay == curWeekDay:
        return date

    if colWeekDay < curWeekDay:
        colDate = curDate - datetime.timedelta(days=curWeekDay-colWeekDay)
    else:
        colDate = curDate + datetime.timedelta(days=colWeekDay-curWeekDay)

    return colDate.strftime("%Y%m%d")


def getThisMonday(date):
    """
    Get the Monday of the weeek.
    """

    year, mon, day = splitDate(date)
    curDate = datetime.date(int(year), int(mon), int(day))
    curWeekDay = curDate.isoweekday()

    if curWeekDay == 1:
        return date

    monDate = curDate - datetime.timedelta(days=curWeekDay-1)

    return monDate.strftime("%Y%m%d")


def getLastWeekDay(date):
    """
    Get the date a week ago.
    """

    year, mon, day = splitDate(date)
    curDate = datetime.date(int(year), int(mon), int(day))
    lastWeekDate = curDate - datetime.timedelta(days=7)

    return lastWeekDate.strftime("%Y%m%d")


def getThisWeekDateRange(date):
    """
    Get the date range of this week.
    """

    year, mon, day = splitDate(date)
    curDate = datetime.date(int(year), int(mon), int(day))
    curWeekDay = curDate.isoweekday()
    sunDate = curDate - datetime.timedelta(days=curWeekDay)
    dateRange = [sunDate+datetime.timedelta(days=i) for i in range(7)]
    dateRange = [d.strftime("%Y%m%d") for d in dateRange]

    return dateRange


def getThisWeekSunSatDateTime(date):
    """
    Get the dateTimes of Sunday and Saturday of this week.
    """

    year, mon, day = splitDate(date)
    curDateTime = datetime.datetime(int(year), int(mon), int(day))
    curWeekDay = curDateTime.isoweekday()

    if curWeekDay == 7:
        satDateTime = curDateTime + datetime.timedelta(days=6)
        return curDateTime, satDateTime

    sunDateTime = curDateTime - datetime.timedelta(days=curWeekDay)
    satDateTime = sunDateTime + datetime.timedelta(days=6)

    return sunDateTime, satDateTime


def getFirstElem(seq):
    """
    Get first element of given sequence.
    """

    return seq[0]


def adjustDate(date, time):
    """
    Adjust date according to time.
    """

    hour = time[:2]

    if hour in ["00", "01", "02", "03", "04"]:
        year, mon, day = splitDate(date)
        today = datetime.date(int(year), int(mon), int(day))
        tomorrow = today + datetime.timedelta(days=1)

        return tomorrow.strftime("%Y%m%d")

    return date


def str2date(dateStr):
    """
    Convert date in string to Python date object.
    """

    year, mon, day = splitDate(dateStr)
    date = datetime.date(int(year), int(mon), int(day))

    return date


def str2time(timeStr):
    """
    Convert time in string to Python time object.
    """

    hour = int(timeStr[:2])
    minute = int(timeStr[-2:])
    time = datetime.time(hour=hour, minute=minute)

    return time


def str2dateTime(dateStr, timeStr):
    """
    Convert date and time in string to Python datetime object.
    """

    year, mon, day = splitDate(dateStr)
    hour = int(timeStr[:2])
    minute = int(timeStr[-2:])
    dateTime = datetime.datetime(int(year), int(mon), int(day), hour=hour,
                                 minute=minute)

    return dateTime


def containsNum(src):
    """
    Check if given string contains number character.
    """

    for ch in src:
        if ch.isdigit():
            return True

    return False


def prettifyJson(jsonTxt):
    """
    Prettify JSON text.
    """

    jsonTxt = json.dumps(jsonTxt, ensure_ascii=False, indent=2)

    return jsonTxt
