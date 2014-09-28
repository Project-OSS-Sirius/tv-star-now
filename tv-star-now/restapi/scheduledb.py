# -*- coding: utf-8 -*-


import datetime
import urllib.parse
import collections
from flask.ext.restful import Resource
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger
import pymongo
from .util import str2dateTime
from .util import validateDate
from .util import getThisWeekSunSatDateTime


# Convinient functions

def delDateTimeId(results):
    """
    Delete datetime and _id objects.
    """

    for result in results:
        del result["_id"]
        del result["dateTime"]
        yield result


def delMongoId(results):
    """
    Delete MongoDB _id objects.
    """

    for result in results:
        del result["_id"]
        yield result


def getCountVal(celebItem):
    """
    Get count value from celebrity item.
    """

    return celebItem["AppearCount"]


class ScheduleDB(object):

    """
    TV information database class.
    """

    def __init__(self, mongoClient, db="tv-star-now",
                 episodeColl="episodes", scheduleColl="schedule",
                 programsColl="programs", celebritiesColl="celebrities"):
        """
        Initialize members.
        """

        self._episodeColl = mongoClient[db][episodeColl]
        self._scheduleColl = mongoClient[db][scheduleColl]
        self._programsColl = mongoClient[db][programsColl]
        self._celebritiesColl = mongoClient[db][celebritiesColl]

    def searchSchedule(self, dateStr, timeStr, celebs):
        """
        Search TV schedule with given parameters.
        """

        results = []

        for celeb in celebs.split("|"):
            scheduleItems = self._searchSchedule(dateStr, timeStr)
            celeb = celeb.strip()
            subResults = collections.defaultdict(list)
            for scheduleItem in scheduleItems:
                programId = scheduleItem.get("programId")
                episodeNum = scheduleItem.get("episodeNum")

                if episodeNum:
                    if self._searchEpisodes(programId, episodeNum, celeb):
                        del scheduleItem["dateTime"]
                        del scheduleItem["_id"]
                        subResults[celeb].append(scheduleItem)
                else:
                    if self._searchPrograms(programId, celeb):
                        del scheduleItem["dateTime"]
                        del scheduleItem["_id"]
                        subResults[celeb].append(scheduleItem)

            if subResults:
                results.append({"celebrity": celeb,
                                "scheduleItems": subResults})

        return results

    def _searchSchedule(self, dateStr, timeStr):
        """
        Search schedule with given parameters.
        """

        curDateTime = str2dateTime(dateStr, timeStr)
        lowerDateTime = curDateTime - datetime.timedelta(minutes=30)
        upperDateTime = curDateTime + datetime.timedelta(hours=1)
        query = {
            "dateTime": {"$gte": lowerDateTime, "$lte": upperDateTime}
        }

        scheduleItems = self._scheduleColl.find(query)

        return scheduleItems

    def _searchEpisodes(self, programId, episodeNum, celeb):
        """
        Search episodes with given paremeters.
        """

        query = {
            "programId": programId,
            "episodeNum": episodeNum,
        }

        episodeItems = self._episodeColl.find(query)

        for episodeItem in episodeItems:
            if celeb in episodeItem["guests"]:
                return True

        return False

    def _searchPrograms(self, programId, celeb):
        """
        Search programs witn given parameters.
        """

        query = {
            "programId": programId,
        }

        programItems = self._programsColl.find(query)

        for programItem in programItems:
            if celeb in programItem["cast"]:
                return True

        return False

    def listSchedule(self, dateStr, dateRange):
        """
        Return TV schedule for given date.
        """

        if dateRange == "day":
            query = {
                "date": dateStr
            }
            scheduleItems = self._scheduleColl.find(query)
        else:
            sunDateTime, satDateTime = getThisWeekSunSatDateTime(dateStr)
            query = {
                "dateTime": {"$gte": sunDateTime, "$lte": satDateTime}
            }
            scheduleItems = self._scheduleColl.find(query)

        return delDateTimeId(scheduleItems)

    def listCelebrities(self, topN):
        """
        Return celebrity items.
        """

        celebItems = \
            self._celebritiesColl.find().sort("appearCount",
                                              pymongo.DESCENDING).limit(topN)

        return delMongoId(celebItems)


class ScheduleSearch(Resource):

    """
    TV schedule search class.
    """

    @classmethod
    def make(cls, db):
        """
        Make db.
        """

        cls._db = db
        return cls

    @swagger.operation(
        summary=u"방송 편성표 검색",
        parameters=[
            {
                "name": "date",
                "description": u"날짜(YYYYMMDD)",
                "dataType": "string",
                "paramType": "query",
                "required": True
            },
            {
                "name": "time",
                "description": u"시간(HHMM)",
                "dataType": "string",
                "paramType": "query",
                "required": True
            },
            {
                "name": "celebs",
                "description": u"출연자(여러 명일 경우 '|'로 구분)",
                "dataType": "string",
                "paramType": "query",
                "required": True
            }
        ]
    )
    def get(self):
        """
        주어진 시간과 날짜, 그리고 연예인 목록을 기준으로 방송 편성 정보를 검색한다.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("date", type=str, location="args")
        parser.add_argument("time", type=str, location="args")
        parser.add_argument("celebs", type=str, location="args")
        args = parser.parse_args()
        dateStr = args["date"]
        timeStr = args["time"]
        celebs = urllib.parse.unquote(args["celebs"], encoding="utf-8")

        records = self._db.searchSchedule(dateStr, timeStr, celebs)
        data = {"data": records}

        return data, 200, {"Access-Control-Allow-Origin": "*"}


class ScheduleList(Resource):

    """
    TV schedule list class.
    """

    @classmethod
    def make(cls, db):
        """
        Make db.
        """

        cls._db = db
        return cls

    @swagger.operation(
        summary=u"방송 편성 정보 보기",
        parameters=[
            {
                "name": "date",
                "description": u"날짜. YYYYMMDD 형식으로 입력",
                "dataType": "string",
                "paramType": "query",
                "required": True
            },
            {
                "name": "range",
                "description": u"범위. 'day' 또는 'week'로 지정.",
                "dataType": "string",
                "paramType": "query",
                "required": True
            }
       ]
    )
    def get(self):
        """
        주어진 날짜의 방송 편성 정보를 보인다.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("date", type=str, location="args")
        parser.add_argument("range", type=str, location="args")
        args = parser.parse_args()
        dateStr = args["date"]
        dateRange = args["range"]

        try:
            validateDate(dateStr)
        except ValueError as e:
            data = {"error": "{}".format(e)}
            return data, 200, {"Access-Control-Allow-Origin": "*"}

        if dateRange not in ["day", "week"]:
            data = {"error": "Invalid range: {}".format(dateRange)}
            return data, 200, {"Access-Control-Allow-Origin": "*"}

        records = self._db.listSchedule(dateStr, dateRange)
        data = {"data": list(records)}

        return data, 200, {"Access-Control-Allow-Origin": "*"}


class CelebritiesList(Resource):

    """
    Celebrities list class.
    """

    @classmethod
    def make(cls, db):
        """
        Make db.
        """

        cls._db = db
        return cls

    @swagger.operation(
        summary=u"방송 출연 유명인 보기",
        parameters=[
            {
                "name": "topN",
                "description": u"출연 횟수 기준 결과 수 지정, 최대 100.",
                "dataType": "integer",
                "paramType": "query",
                "required": True
            }
       ]
    )
    def get(self):
        """
        방송 출연 유명인의 목록을 출연 빈도순으로 보인다.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("topN", type=int, location="args")
        args = parser.parse_args()
        topN = args["topN"]

        if topN > 100:
            data = {"error": "Invalid topN: {}".format(topN)}
            return data, 200, {"Access-Control-Allow-Origin": "*"}

        records = self._db.listCelebrities(topN)
        data = {"data": list(records)}

        return data, 200, {"Access-Control-Allow-Origin": "*"}
