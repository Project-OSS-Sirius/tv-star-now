# -*- coding: utf-8 -*-

"""
scheduleinfo.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2014 by Hwanho Lee <hwanho633@naver.com>
:license: Apache2, see LICENSE for more details.

"""


import logging
import time
import ujson
from .daumtv import Schedule
from .natetv import AuxSchedule
from .util import validateDate


class ScheduleInfo(object):

    """
    TV broadcasting schedule information class.
    """

    # TV channel information

    _chanTypeNameIds = {
        u"공중파": 1,
        u"케이블": 2,
        u"스카이라이프": 3,
        u"종합편성채널": 10
    }

    _chanTypeCatIds = {
        u"공중파": {
            "KBS": {
                "KBS1": 105,
                "KBS2": 106,
                u"강릉KBS1": 496,
                u"경인KBS1": 456,
                u"광주KBS1": 498,
                u"대구KBS1": 501,
                u"대전KBS1": 418,
                u"부산KBS1": 408,
                u"울산KBS1": 495,
                u"전주KBS1": 499,
                u"제주KBS1": 502,
                u"창원KBS1": 500,
                u"청주KBS1": 497,
                u"춘천KBS1": 419,
                u"목포KBS1": 539,
                u"원주KBS1": 541,
                u"충주KBS1": 542,
                "HD KBS2": 581,
                "HD KBS1": 582,
                u"KBS전주1라디오": 666,
                u"KBS제주2라디오": 698
            },
            "MBC": {
                "MBC": 113,
                u"광주MBC": 416,
                u"대구MBC": 484,
                u"강릉MBC": 486,
                u"대전MBC": 428,
                u"목포MBC": 493,
                u"부산MBC": 413,
                u"삼척MBC": 490,
                u"안동MBC": 487,
                u"여수MBC": 494,
                u"울산MBC": 415,
                u"원주MBC": 489,
                u"전주MBC": 491,
                u"제주MBC": 485,
                u"진주MBC": 427,
                u"창원MBC": 492,
                u"청주MBC": 482,
                u"춘천MBC": 412,
                u"충주MBC": 483,
                u"포항MBC": 488,
                "HD MBC": 583
            },
            "SBS": {
                "SBS": 130,
                u"G1강원민방": 1,
                u"KBC광주방송": 2,
                u"TBC대구방송": 10,
                u"TJB대전방송": 12,
                u"KNN부산경남방송": 111,
                u"UBC울산방송": 46,
                u"JTV전주방송": 55,
                u"JIBS제주방송": 314,
                u"CJB청주방송": 63,
                "HD SBS": 580
            },
            u"공용": {
                "EBS": 89,
                u"OBS경인TV": 124
            }
        },
        u"케이블": {
            u"영화": {
                "OCN": 125,
                "XTM": 140,
                u"시네마TV": 33,
                u"채널CGV": 58,
                u"캐치온": 64,
                "ABO": 77,
                "AXN": 79,
                "CNTV": 87,
                "Super Action": 136,
                u"미드나잇채널": 285,
                u"스파이스TV": 294,
                "TVB Korea": 348,
                u"스크린": 380,
                u"씨네프": 420,
                u"인디필름": 426,
                u"(i)캐치온플러스": 431,
                "VIKI HD": 463
            },
            u"다큐/정보": {
                u"국군방송": 3,
                u"국회방송": 4,
                u"기독교TV": 5,
                u"내셔널지오그래픽채널": 6,
                u"리빙TV": 15,
                u"리얼TV": 17,
                u"복지TV": 24,
                u"BTN불교TV": 26,
                u"사이언스TV": 28,
                u"생활건강TV": 29,
                u"실버아이": 34,
                u"실버TV": 35,
                "MBC Life": 42,
                u"평화방송": 68,
                u"한국정책방송KTV": 71,
                u"한방건강TV": 72,
                u"환경TV": 73,
                "CBS TV": 83,
                "Channel J": 84,
                "KBS Prime": 108,
                u"메디컬TV": 118,
                "RTV": 129,
                "TBS TV": 137,
                u"ABS농어민방송": 148,
                "Arirang": 152,
                "ATV": 153,
                "GOODTV": 157,
                "CGN": 162,
                u"디스커버리": 168,
                "KBS Korea": 185,
                "MBCnet": 235,
                u"서울신문STV": 293,
                u"상생방송": 356,
                "HD ONE": 357,
                u"채널뷰": 369,
                "CH-T": 400,
                "KBS World": 429,
                u"BBS불교방송": 443,
                "ONT": 452,
                "SAFE TV": 453,
                "FNC TV": 454,
                "CTS Family": 461,
                "OBS W HD": 462,
                u"헬스메디TV": 464,
                "K.NET": 469,
                u"한국소비자TV": 471,
                "OCB": 472,
                "BOOK TV": 538,
                u"법률방송": 544,
                "C Channel": 590,
                u"라이프 TV": 596,
                "DOGTV": 708
            },
            u"해외위성": {
                "AFN Korea": 149,
                "AN": 150,
                "BBC World": 156,
                "CCTV4": 161,
                "CNBC": 166,
                "CNN Int’l": 167,
                "NHK World Premium": 239,
                "Bloomberg TV": 289,
                "CCTV-9": 387,
                "CCTV News": 460,
                "DWTV": 509
            },
            u"드라마": {
                u"MBC드라마넷": 116,
                u"SBS플러스": 132,
                "KBS Drama": 186,
                u"드라맥스": 14,
                u"중화TV": 57,
                u"FOX채널": 95,
                u"무협TV": 109,
                u"디원TV": 169,
                "DRAMAH": 333,
                "FOXLIFE": 346,
                "OCN Series": 353,
                "CHING": 377,
                "DRAMACUBE": 421,
                u"텔레노벨라": 435,
                "Channel N": 573,
            },
            u"라디오": {
                u"YTN라디오": 411
            },
            u"스포츠/취미": {
                u"MBC스포츠플러스": 117,
                "SBS Sports": 131,
                u"KBS N스포츠": 103,
                u"바둑TV": 23,
                u"브레인TV": 27,
                "FTV": 96,
                "FS-TV": 173,
                "J Golf": 176,
                u"SBS골프": 244,
                u"폴라리스TV": 329,
                "Mountain TV": 389,
                u"(i)스포츠원": 465,
                u"빌리어즈TV": 687
            },
            u"여성/홈쇼핑": {
                "On Style": 127,
                u"올리브": 45,
                u"NS홈쇼핑": 7,
                u"육아방송": 48,
                u"채널동아": 61,
                u"CJ 오쇼핑": 86,
                "GTV": 99,
                "Story On": 135,
                "Food N": 172,
                "GS SHOP": 174,
                u"롯데홈쇼핑": 279,
                u"예술TV Arte": 300,
                "Trend E": 317,
                u"현대홈쇼핑": 332,
                "Fashion N": 368,
                "FOODTV": 458,
                u"홈스토리": 507,
                "Fashion TV": 531,
                u"홈&쇼핑": 532,
                u"큐피드": 540,
                "MBC QueeN": 587,
                "KBS W": 588,
                u"라이프N": 641,
                "EDGE TV": 662
            },
            u"음악/오락": {
                "tvN": 138,
                u"코미디TV": 66,
                "KBS Joy": 107,
                u"E채널": 88,
                "MBC Every1": 114,
                "Mnet": 112,
                u"월드이벤트TV": 47,
                u"ETN연예채널": 92,
                "GAME TV": 98,
                "KM": 110,
                "SBS MTV": 121,
                "ONGAMENET": 126,
                "QTV": 128,
                "Y-STAR": 142,
                u"CMC가족오락TV": 165,
                "SBS funE": 259,
                "FX": 347,
                "I.NET": 455,
                "MBC Music": 475,
                "HD Classica": 510
            },
            u"교육": {
                u"EBS플러스1": 90,
                u"EBS플러스2": 91,
                "JEI English TV": 102,
                "EBS English": 170,
                "OUN": 240,
                u"일자리방송": 391,
                u"한국직업방송": 396,
                u"정철영어TV": 403,
                "CHINA1": 434,
                "EduKids TV": 457,
                "EBS U": 533
            },
            u"어린이/만화": {
                "KBS KIDS": 524,
                u"니켈로디언": 8,
                u"대교어린이TV": 9,
                u"애니맥스": 38,
                "AniBox": 40,
                "AniOne": 41,
                u"챔프": 62,
                u"투니버스": 67,
                u"카툰네트워크": 82,
                u"JEI재능TV": 101,
                u"디즈니채널": 254,
                u"애니플러스": 402,
                u"디즈니주니어": 432
            },
            u"뉴스/재태크": {
                "YTN": 141,
                u"서울경제TV": 19,
                u"RTN부동산TV": 25,
                u"이데일리TV": 50,
                u"한국경제TV": 70,
                u"비즈니스&": 290,
                u"토마토TV": 325,
                "MTN": 386,
                u"쿠키건강TV": 390,
                u"SBS CNBC": 392,
                "Channel News Asia": 423,
                u"팍스TV": 424,
                "news Y": 446,
                "YTN weather": 459,
                u"M머니": 529,
                u"R토마토": 574
            },
            u"공용": {
                "BBC": 80,
                "NHK": 122,
                "SkyEN": 363,
                u"씨앤앰케이블TV채널4": 370
            }
        },
        u"스카이라이프": {
            u"영화": {
                "OCN": 125,
                "XTM": 140,
                u"채널CGV": 58,
                u"HD캐치온플러스": 65,
                "AXN": 79,
                "CNTV": 87,
                "MGM": 119,
                "Mplex": 120,
                "Super Action": 136,
                u"미드나잇채널": 285,
                u"스파이스TV": 294,
                "VIKI HD": 463,
                "M Classic": 547,
                u"HD캐치온": 566,
                "THE MOVIE": 648
            },
            u"다큐/정보": {
                u"국군방송": 3,
                u"국회방송": 4,
                u"기독교TV": 5,
                u"내셔널지오그래픽채널": 6,
                u"리빙TV": 15,
                u"복지TV": 24,
                u"BTN불교TV": 26,
                u"사이언스TV": 28,
                u"실버TV": 35,
                u"평화방송": 68,
                u"한국정책방송KTV": 71,
                u"한방건강TV": 72,
                "CBS TV": 83,
                "HEALTH SKY TV": 100,
                "Sky HD": 134,
                "Arirang": 152,
                "ATV": 153,
                "MBCNET": 235,
                "CH-T": 400,
                "Discovery": 430,
                u"채널IT": 449,
                "OBS W HD": 462,
                "HD Channel J": 562,
                "HD Discovery": 563,
                "HD MBC Life": 565,
                u"HD팍스TV": 567,
                u"HD CH-T": 571
            },
            u"해외위성": {
                "Animal Planet": 151,
                "CCTV4": 161,
                "CNN Int’l": 167,
                "NHK World Premium": 239,
                "STAR SPORTS": 251,
                "CCTV-9": 387,
                "CCTV News": 460,
                "NHK World TV": 466
            },
            u"드라마": {
                u"MBC드라마넷": 116,
                u"SBS플러스": 132,
                "KBS Drama": 186,
                u"중화TV": 57,
                "Asia N": 85,
                "BBC Entertainment": 154,
                "OCN Series": 353,
                u"HD텔레노벨라": 425,
                u"선댄스채널": 519
            },
            u"스포츠/취미": {
                u"MBC스포츠플러스": 117,
                "SBS Sports": 131,
                u"KBS N스포츠": 103,
                u"브레인TV": 27,
                u"스피드스포츠": 32,
                "FTV": 96,
                "J Golf": 176,
                u"SBS골프": 244,
                u"한국바둑방송": 250,
                "Car & Sports TV": 388,
                "The M": 548,
                u"빌리어즈TV": 687
            },
            u"여성/홈쇼핑": {
                "On Style": 127,
                u"올리브": 45,
                u"NS홈쇼핑": 7,
                u"채널동아": 61,
                u"CJ오쇼핑": 86,
                "GS SHOP": 174,
                u"롯데홈쇼핑": 279,
                u"예술TV Arte": 300,
                u"현대홈쇼핑": 332,
                u"홈&쇼핑": 532,
                "HD FoodTV": 537
            },
            u"음악/오락": {
                "tvN": 138,
                u"코미디TV": 66,
                "KBS Joy": 107,
                "MBC Every1": 114,
                "Mnet": 112,
                u"ETN연예채널": 92,
                "GAME TV": 98,
                "KM": 110,
                "QTV": 128,
                "Y-STAR": 142,
                "SBS funE": 259,
                u"채널원": 439,
                "MBC Music": 475,
                "HD Classica": 510
            },
            u"교육": {
                u"EBS플러스1": 90,
                u"EBS플러스2": 91,
                "EBS English": 170,
                u"Kids Talk Talk 플러스": 228,
                "OUN": 240,
                u"일자리방송": 391,
                u"한국직업방송": 396,
                "EBS U": 533
            },
            u"어린이/만화": {
                u"대교어린이TV": 9,
                u"애니맥스": 38,
                "AniBox": 40,
                u"카툰네트워크": 82,
                u"JEI재능TV": 101,
                u"디즈니채널": 254,
                u"HD Kids Talk Talk 플러스": 545
            },
            u"뉴스/재태크": {
                "YTN": 141,
                u"RTN부동산TV": 25,
                u"한국경제TV": 70,
                u"토마토TV": 325,
                "News Y": 446,
                "YTN weather": 459
            },
            u"공용": {
                "HD EBS": 543
            }
        },
        u"종합편성채널": {
            u"전체": {
                "MBN": 18,
                u"TV조선": 436,
                u"채널A": 438,
                "JTBC": 437,
                "HD MBN": 576,
                "HD JTBC": 577,
                u"HD 채널A": 578,
                u"HD TV조선": 579
            }
        }
    }
    _daumChanId2nateChanLinkTmpl = {
        105: "tv_week_1_9_{}-{}-{}.html",
        106: "tv_week_1_7_{}-{}-{}.html",
        113: "tv_week_1_11_{}-{}-{}.html",
        130: "tv_week_1_6_{}-{}-{}.html",
        89: "tv_week_1_13_{}-{}-{}.html",
        124: "tv_week_1_816_{}-{}-{}.html",
        125: "tv_week_2_22_{}-{}-{}.html",
        140: "tv_week_2_388_{}-{}-{}.html",
        #"시네마TV": 33,
        58: "tv_week_2_19_{}-{}-{}.html",
        64: "tv_week_2_31_{}-{}-{}.html",
        #"ABO": 77,
        #"AXN": 79,
        87: "tv_week_2_355_{}-{}-{}.html",
        136: "tv_week_2_129_{}-{}-{}.html",
        285: "tv_week_2_169_{}-{}-{}.html",
        #"스파이스TV": 294,
        348: "tv_week_2_781_{}-{}-{}.html",
        380: "tv_week_2_916_{}-{}-{}.html",
        420: "tv_week_2_103_{}-{}-{}.html",
        426: "tv_week_2_105_{}-{}-{}.html",
        431: "tv_week_2_429_{}-{}-{}.html",
        463: "tv_week_2_86_{}-{}-{}.html",
        #"국군방송": 3,
        4: "tv_week_2_427_{}-{}-{}.html",
        #"기독교TV": 5,
        6: "tv_week_2_119_{}-{}-{}.html",
        15: "tv_week_2_28_{}-{}-{}.html",
        17: "tv_week_2_669_{}-{}-{}.html",
        24: "tv_week_2_707_{}-{}-{}.html",
        26: "tv_week_2_52_{}-{}-{}.html",
        28: "tv_week_2_792_{}-{}-{}.html",
        29: "tv_week_2_26_{}-{}-{}.html",
        34: "tv_week_2_378_{}-{}-{}.html",
        35: "tv_week_2_736_{}-{}-{}.html",
        #"MBC Life": 42,
        68: "tv_week_2_33_{}-{}-{}.html",
        #"한국정책방송KTV": 71,
        72: "tv_week_2_697_{}-{}-{}.html",
        73: "tv_week_2_29_{}-{}-{}.html",
        83: "tv_week_2_156_{}-{}-{}.html",
        84: "tv_week_2_290_{}-{}-{}.html",
        108: "tv_week_2_168_{}-{}-{}.html",
        118: "tv_week_2_185_{}-{}-{}.html",
        129: "tv_week_2_175_{}-{}-{}.html",
        137: "tv_week_2_495_{}-{}-{}.html",
        #"ABS농어민방송": 148,
        152: "tv_week_2_50_{}-{}-{}.html",
        153: "tv_week_2_774_{}-{}-{}.html",
        157: "tv_week_2_293_{}-{}-{}.html",
        162: "tv_week_2_688_{}-{}-{}.html",
        168: "tv_week_2_142_{}-{}-{}.html",
        #"KBS Korea": 185,
        235: "tv_week_2_764_{}-{}-{}.html",
        293: "tv_week_2_379_{}-{}-{}.html",
        356: "tv_week_2_779_{}-{}-{}.html",
        #"HD ONE": 357,
        369: "tv_week_2_918_{}-{}-{}.html",
        #"CH-T": 400,
        429: "tv_week_2_559_{}-{}-{}.html",
        443: "tv_week_2_903_{}-{}-{}.html",
        452: "tv_week_2_402_{}-{}-{}.html",
        453: "tv_week_2_416_{}-{}-{}.html",
        #"FNC TV": 454,
        461: "tv_week_2_42_{}-{}-{}.html",
        462: "tv_week_2_128_{}-{}-{}.html",
        464: "tv_week_2_415_{}-{}-{}.html",
        469: "tv_week_2_89_{}-{}-{}.html",
        471: "tv_week_2_180_{}-{}-{}.html",
        #"OCB": 472,
        538: "tv_week_2_584_{}-{}-{}.html",
        544: "tv_week_2_812_{}-{}-{}.html",
        #"C Channel": 590,
        596: "tv_week_2_845_{}-{}-{}.html",
        708: "tv_week_2_76_{}-{}-{}.html",
        #"AFN Korea": 149,
        150: "tv_week_2_426_{}-{}-{}.html",
        156: "tv_week_2_260_{}-{}-{}.html",
        161: "tv_week_2_159_{}-{}-{}.html",
        166: "tv_week_2_141_{}-{}-{}.html",
        167: "tv_week_2_117_{}-{}-{}.html",
        239: "tv_week_2_166_{}-{}-{}.html",
        289: "tv_week_2_703_{}-{}-{}.html",
        #"CCTV-9": 387,
        460: "tv_week_2_673_{}-{}-{}.html",
        509: "tv_week_2_256_{}-{}-{}.html",
        116: "tv_week_2_253_{}-{}-{}.html",
        132: "tv_week_2_54_{}-{}-{}.html",
        186: "tv_week_2_148_{}-{}-{}.html",
        14: "tv_week_2_285_{}-{}-{}.html",
        57: "tv_week_2_664_{}-{}-{}.html",
        95: "tv_week_2_706_{}-{}-{}.html",
        #"무협TV": 109,
        169: "tv_week_2_693_{}-{}-{}.html",
        333: "tv_week_2_287_{}-{}-{}.html",
        346: "tv_week_2_817_{}-{}-{}.html",
        353: "tv_week_2_912_{}-{}-{}.html",
        377: "tv_week_2_780_{}-{}-{}.html",
        421: "tv_week_2_499_{}-{}-{}.html",
        435: "tv_week_2_925_{}-{}-{}.html",
        #"Channel N": 573,
        #u"YTN라디오": 411
        117: "tv_week_2_124_{}-{}-{}.html",
        131: "tv_week_2_30_{}-{}-{}.html",
        103: "tv_week_2_147_{}-{}-{}.html",
        23: "tv_week_2_46_{}-{}-{}.html",
        27: "tv_week_2_488_{}-{}-{}.html",
        96: "tv_week_2_262_{}-{}-{}.html",
        173: "tv_week_2_254_{}-{}-{}.html",
        176: "tv_week_2_487_{}-{}-{}.html",
        244: "tv_week_2_44_{}-{}-{}.html",
        329: "tv_week_2_683_{}-{}-{}.html",
        389: "tv_week_2_613_{}-{}-{}.html",
        #"(i)스포츠원": 465,
        687: "tv_week_2_615_{}-{}-{}.html",
        127: "tv_week_2_414_{}-{}-{}.html",
        45: "tv_week_2_15_{}-{}-{}.html",
        7: "tv_week_2_133_{}-{}-{}.html",
        48: "tv_week_2_252_{}-{}-{}.html",
        #"채널동아": 61,
        86: "tv_week_2_250_{}-{}-{}.html",
        99: "tv_week_2_35_{}-{}-{}.html",
        135: "tv_week_2_705_{}-{}-{}.html",
        #"Food N": 172,
        174: "tv_week_2_45_{}-{}-{}.html",
        279: "tv_week_2_138_{}-{}-{}.html",
        300: "tv_week_2_333_{}-{}-{}.html",
        317: "tv_week_2_813_{}-{}-{}.html",
        332: "tv_week_2_140_{}-{}-{}.html",
        368: "tv_week_2_917_{}-{}-{}.html",
        458: "tv_week_2_753_{}-{}-{}.html",
        507: "tv_week_2_906_{}-{}-{}.html",
        531: "tv_week_2_494_{}-{}-{}.html",
        532: "tv_week_2_567_{}-{}-{}.html",
        540: "tv_week_2_583_{}-{}-{}.html",
        587: "tv_week_2_176_{}-{}-{}.html",
        588: "tv_week_2_509_{}-{}-{}.html",
        #"라이프N": 641,
        #"EDGE TV": 662
        138: "tv_week_2_743_{}-{}-{}.html",
        66: "tv_week_2_100_{}-{}-{}.html",
        107: "tv_week_2_754_{}-{}-{}.html",
        88: "tv_week_2_108_{}-{}-{}.html",
        114: "tv_week_2_335_{}-{}-{}.html",
        112: "tv_week_2_27_{}-{}-{}.html",
        47: "tv_week_2_102_{}-{}-{}.html",
        92: "tv_week_2_101_{}-{}-{}.html",
        #"GAME TV": 98,
        110: "tv_week_2_43_{}-{}-{}.html",
        121: "tv_week_2_130_{}-{}-{}.html",
        126: "tv_week_2_55_{}-{}-{}.html",
        128: "tv_week_2_25_{}-{}-{}.html",
        142: "tv_week_2_37_{}-{}-{}.html",
        165: "tv_week_2_419_{}-{}-{}.html",
        259: "tv_week_2_684_{}-{}-{}.html",
        347: "tv_week_2_818_{}-{}-{}.html",
        455: "tv_week_2_118_{}-{}-{}.html",
        475: "tv_week_2_126_{}-{}-{}.html",
        510: "tv_week_2_365_{}-{}-{}.html",
        90: "tv_week_2_113_{}-{}-{}.html",
        91: "tv_week_2_114_{}-{}-{}.html",
        102: "tv_week_2_289_{}-{}-{}.html",
        170: "tv_week_2_777_{}-{}-{}.html",
        240: "tv_week_2_47_{}-{}-{}.html",
        391: "tv_week_2_811_{}-{}-{}.html",
        396: "tv_week_2_79_{}-{}-{}.html",
        403: "tv_week_2_561_{}-{}-{}.html",
        434: "tv_week_2_150_{}-{}-{}.html",
        457: "tv_week_2_508_{}-{}-{}.html",
        533: "tv_week_2_723_{}-{}-{}.html",
        #"KBS KIDS": 524,
        8: "tv_week_2_685_{}-{}-{}.html",
        9: "tv_week_2_17_{}-{}-{}.html",
        38: "tv_week_2_725_{}-{}-{}.html",
        #"AniBox": 40,
        41: "tv_week_2_160_{}-{}-{}.html",
        62: "tv_week_2_666_{}-{}-{}.html",
        67: "tv_week_2_38_{}-{}-{}.html",
        82: "tv_week_2_358_{}-{}-{}.html",
        101: "tv_week_2_23_{}-{}-{}.html",
        254: "tv_week_2_172_{}-{}-{}.html",
        402: "tv_week_2_91_{}-{}-{}.html",
        432: "tv_week_2_430_{}-{}-{}.html",
        # 뉴스/재테크
        141: "tv_week_2_24_{}-{}-{}.html",
        19: "tv_week_2_157_{}-{}-{}.html",
        25: "tv_week_2_125_{}-{}-{}.html",
        50: "tv_week_2_380_{}-{}-{}.html",
        70: "tv_week_2_106_{}-{}-{}.html",
        290: "tv_week_2_771_{}-{}-{}.html",
        325: "tv_week_2_359_{}-{}-{}.html",
        386: "tv_week_2_132_{}-{}-{}.html",
        390: "tv_week_2_735_{}-{}-{}.html",
        392: "tv_week_2_622_{}-{}-{}.html",
        423: "tv_week_2_81_{}-{}-{}.html",
        #"팍스TV": 424,
        446: "tv_week_2_573_{}-{}-{}.html",
        459: "tv_week_2_502_{}-{}-{}.html",
        #"M머니": 529,
        574: "tv_week_2_704_{}-{}-{}.html",
        # 공용
        #"BBC": 80,
        #"NHK": 122,
        #"SkyEN": 363,
        #u"씨앤앰케이블TV채널4": 370
        #
        # 스카이라이프
        #
        # 영화
        125: "tv_week_3_22_{}-{}-{}.html",
        140: "tv_week_3_388_{}-{}-{}.html",
        58: "tv_week_3_19_{}-{}-{}.html",
        65: "tv_week_3_161_{}-{}-{}.html",
        79: "tv_week_3_679_{}-{}-{}.html",
        87: "tv_week_3_355_{}-{}-{}.html",
        #"MGM": 119,
        #"Mplex": 120,
        136: "tv_week_3_129_{}-{}-{}.html",
        285: "tv_week_3_169_{}-{}-{}.html",
        #"스파이스TV": 294,
        463: "tv_week_3_86_{}-{}-{}.html",
        #"M Classic": 547,
        566: "tv_week_3_799_{}-{}-{}.html",
        648: "tv_week_3_165_{}-{}-{}.html",
        # 다큐/정보
        #"국군방송": 3,
        4: "tv_week_3_427_{}-{}-{}.html",
        5: "tv_week_3_42_{}-{}-{}.html",
        6: "tv_week_3_119_{}-{}-{}.html",
        15: "tv_week_3_28_{}-{}-{}.html",
        24: "tv_week_3_707_{}-{}-{}.html",
        26: "tv_week_3_52_{}-{}-{}.html",
        28: "tv_week_3_792_{}-{}-{}.html",
        35: "tv_week_3_736_{}-{}-{}.html",
        68: "tv_week_3_33_{}-{}-{}.html",
        71: "tv_week_3_184_{}-{}-{}.html",
        72: "tv_week_3_697_{}-{}-{}.html",
        83: "tv_week_3_156_{}-{}-{}.html",
        #"HEALTH SKY TV": 100,
        #"Sky HD": 134,
        152: "tv_week_3_50_{}-{}-{}.html",
        153: "tv_week_3_774_{}-{}-{}.html",
        #"MBCNET": 235,
        #"CH-T": 400,
        #"Discovery": 430,
        #"채널IT": 449,
        462: "tv_week_3_128_{}-{}-{}.html",
        #"HD Channel J": 562,
        563: "tv_week_3_929_{}-{}-{}.html",
        #"HD MBC Life": 565,
        #"HD팍스TV": 567,
        #"HD CH-T": 571
        # 해외위성
        151: "tv_week_3_182_{}-{}-{}.html",
        161: "tv_week_3_159_{}-{}-{}.html",
        167: "tv_week_3_117_{}-{}-{}.html",
        239: "tv_week_3_166_{}-{}-{}.html",
        251: "tv_week_3_122_{}-{}-{}.html",
        #"CCTV-9": 387,
        460: "tv_week_3_673_{}-{}-{}.html",
        #"NHK World TV": 466
        # 드라마
        116: "tv_week_3_253_{}-{}-{}.html",
        132: "tv_week_3_54_{}-{}-{}.html",
        186: "tv_week_3_148_{}-{}-{}.html",
        57: "tv_week_3_664_{}-{}-{}.html",
        85: "tv_week_3_332_{}-{}-{}.html",
        154: "tv_week_3_694_{}-{}-{}.html",
        353: "tv_week_3_912_{}-{}-{}.html",
        425: "tv_week_3_61_{}-{}-{}.html",
        #"선댄스채널": 519
        # 스포츠/취미
        117: "tv_week_3_124_{}-{}-{}.html",
        131: "tv_week_3_30_{}-{}-{}.html",
        103: "tv_week_3_147_{}-{}-{}.html",
        27: "tv_week_3_488_{}-{}-{}.html",
        #"스피드스포츠": 32,
        96: "tv_week_3_262_{}-{}-{}.html",
        176: "tv_week_3_487_{}-{}-{}.html",
        244: "tv_week_3_44_{}-{}-{}.html",
        250: "tv_week_3_162_{}-{}-{}.html",
        #"Car & Sports TV": 388,
        #"The M": 548,
        #"빌리어즈TV": 687
        # 여성/홈쇼핑
        127: "tv_week_3_414_{}-{}-{}.html",
        45: "tv_week_3_15_{}-{}-{}.html",
        7: "tv_week_3_133_{}-{}-{}.html",
        #"채널동아": 61,
        86: "tv_week_3_250_{}-{}-{}.html",
        174: "tv_week_3_45_{}-{}-{}.html",
        279: "tv_week_3_138_{}-{}-{}.html",
        #"예술TV Arte": 300,
        332: "tv_week_3_140_{}-{}-{}.html",
        532: "tv_week_3_567_{}-{}-{}.html",
        537: "tv_week_3_556_{}-{}-{}.html",
        # 음악/오락
        138: "tv_week_3_743_{}-{}-{}.html",
        66: "tv_week_3_100_{}-{}-{}.html",
        107: "tv_week_3_754_{}-{}-{}.html",
        114: "tv_week_3_335_{}-{}-{}.html",
        112: "tv_week_3_27_{}-{}-{}.html",
        92: "tv_week_3_101_{}-{}-{}.html",
        #"GAME TV": 98,
        #"KM": 110,
        28: "tv_week_3_25_{}-{}-{}.html",
        142: "tv_week_3_37_{}-{}-{}.html",
        259: "tv_week_3_684_{}-{}-{}.html",
        #"채널원": 439,
        475: "tv_week_3_126_{}-{}-{}.html",
        510: "tv_week_3_365_{}-{}-{}.html",
        # 교육
        90: "tv_week_3_113_{}-{}-{}.html",
        91: "tv_week_3_114_{}-{}-{}.html",
        170: "tv_week_3_777_{}-{}-{}.html",
        228: "tv_week_3_360_{}-{}-{}.html",
        240: "tv_week_3_47_{}-{}-{}.html",
        391: "tv_week_3_811_{}-{}-{}.html",
        396: "tv_week_3_79_{}-{}-{}.html",
        #"EBS U": 533
        # 어린이/만화
        9: "tv_week_3_17_{}-{}-{}.html",
        38: "tv_week_3_725_{}-{}-{}.html",
        #"AniBox": 40,
        82: "tv_week_3_358_{}-{}-{}.html",
        101: "tv_week_3_23_{}-{}-{}.html",
        #"디즈니채널": 254,
        545: "tv_week_3_92_{}-{}-{}.html",
        # 뉴스/재태크
        141: "tv_week_3_24_{}-{}-{}.html",
        25: "tv_week_3_125_{}-{}-{}.html",
        70: "tv_week_3_106_{}-{}-{}.html",
        325: "tv_week_3_359_{}-{}-{}.html",
        446: "tv_week_3_573_{}-{}-{}.html",
        459: "tv_week_3_502_{}-{}-{}.html",
        # 공용"
        # "HD EBS": 543
        #
        # 종합편성채널
        #
        18: "tv_week_2_20_{}-{}-{}.html",
        436: "tv_week_2_569_{}-{}-{}.html",
        438: "tv_week_2_571_{}-{}-{}.html",
        437: "tv_week_2_570_{}-{}-{}.html",
        576: "tv_week_2_562_{}-{}-{}.html",
        577: "tv_week_2_563_{}-{}-{}.html",
        578: "tv_week_2_564_{}-{}-{}.html",
        579: "tv_week_2_549_{}-{}-{}.html"
    }

    def __init__(self):
        """
        Initialize members.
        """

        self._setLogger()
        self._startTime = time.time()
        self._schedule = Schedule()
        self._auxSchedule = AuxSchedule()

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

    def setDate(self, date):
        """
        Set target date.
        """

        validateDate(date)
        self._date = date
        self._logger.info("Target date: {}".format(date))

    def setChanTypeCat(self, chanType, chanCat):
        """
        Set channel type and category.
        """

        if chanType not in self._chanTypeNameIds:
            raise ValueError("Invalid channel type: {}".format(chanType))

        if chanCat not in self._chanTypeCatIds[chanType].keys():
            raise ValueError("Invalid channel category: {}".format(chanCat))

        self._chanType = chanType
        self._chanCat = chanCat
        self._chanTypeId = self._chanTypeNameIds[chanType]
        self._chanNameIds = self._chanTypeCatIds[chanType][chanCat]
        self._logger.info("Channel type: {}".format(chanType))
        self._logger.info("Channel category: {}".format(chanCat))

    def setOutputFile(self, outputFileName):
        """
        Set output file.
        """

        try:
            self._outputFile = open(outputFileName, "w", encoding="utf-8")
        except IOError:
            raise IOError("Cannot create output file.")

        self._logger.info("Output file created: {}".format(outputFileName))

    def getSchedule(self):
        """
        Get TV schedule for given parameters.
        """

        numChans = len(self._chanNameIds)

        for i, chanName in enumerate(sorted(self._chanNameIds), 1):
            chanId = self._chanNameIds[chanName]

            if chanId != 107:
                continue

            self._logger.info("Fetching schedule information: chanName={}, "
                              "chanId={} ({}/{})".format(chanName, chanId, i,
                                                         numChans))
            schedule = self._schedule.getChanSchedule(self._date,
                                                      self._chanTypeId,
                                                      chanId)
            linkTmpl = self._daumChanId2nateChanLinkTmpl[chanId]
            auxSchedule = self._auxSchedule.getChanSchedule(self._date,
                                                            linkTmpl)
            fullSchedule = self._combineSchedule(schedule, auxSchedule)

            for scheduleElem in fullSchedule:
                chanSchedule = {
                    "channelName": chanName,
                    "channelId": chanId,
                    "date": scheduleElem["date"],
                    "schedule": scheduleElem["daySchedule"]
                }
                self._writeChanSchedule(chanSchedule)

            break

    def _combineSchedule(self, schedule, auxSchedule):
        """
        Combine main and auxiliary schedules.
        """

        fullSchedule = []

        for scheduleElem in schedule:
            date = scheduleElem["date"]
            daySchedule = scheduleElem["daySchedule"]
            fullScheduleElem = {}
            fullScheduleElem["date"] = date
            fullScheduleElem["daySchedule"] = []

            for dayScheduleElem in daySchedule:
                time = dayScheduleElem["time"]
                auxDayScheduleElem = self._searchSchedule(auxSchedule, date,
                                                          time)
                if auxDayScheduleElem and auxDayScheduleElem["episodeNum"]:
                    dayScheduleElem["episodeNum"] = \
                        auxDayScheduleElem["episodeNum"]
                else:
                    dayScheduleElem["episodeNum"] = ""

                fullScheduleElem["daySchedule"].append(dayScheduleElem)

            fullSchedule.append(fullScheduleElem)

        return fullSchedule

    def _searchSchedule(self, schedule, date, time):
        """
        Search schedule with date and time.
        """

        for scheduleElem in schedule:
            if scheduleElem["date"] != date:
                continue

            for dayScheduleElem in scheduleElem["daySchedule"]:
                if dayScheduleElem["time"] == time:
                    return dayScheduleElem

        return None

    def _writeChanSchedule(self, chanSchedule):
        """
        Write channel schedule to output file.
        """

        self._outputFile.write("{}\n".format(ujson.dumps(chanSchedule,
                                                         ensure_ascii=
                                                         False)))
        self._outputFile.flush()
