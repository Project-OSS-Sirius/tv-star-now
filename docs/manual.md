## 사용 설명서

이 문서에서는 TV Star Now API 서비스를 설치하고 구동하는 방법을 간략히 기술한다. 설치 운영체제는 우분투 리눅스를 기준으로 한다.

### 설치

* TV Star Now 설치

[github 저장소](https://github.com/Project-OSS-Sirius/tv-star-now)에서 TV Star Now를 복제한다.

``` shell-session
$ git clone git@github.com:Project-OSS-Sirius/tv-star-now.git
```

* MongoDB 설치

우분투 리눅스 패키지 관리자로 MongoDB를 설치한다.

``` shell-session
$ sudo apt-get install mongodb
```

* 파이썬 패키지 설치

TV Star Now의 작동에 필요한 파이썬 패키지들을 설치한다. TV Star Now는 파이썬 3.4를 이용하여 개발하고 있다.

``` shell-session
$ sudo pip3 install --upgrade requests
$ sudo pip3 install --upgrade pymongo
$ sudo pip3 install --upgrade beautifulsoup4
$ sudo pip3 install --upgrade flask
$ sudo pip3 install --upgrade flask-restful
$ sudo pip3 install --upgrade jinja2
$ sudo pip3 install --upgrade markupsafe
$ sudo pip3 install --upgrade werkzeug
$ sudo pip3 install --upgrade aniso8601
$ sudo pip3 install --upgrade flask-restful-swagger
$ sudo pip3 install --upgrade itsdangerous
$ sudo pip3 install --upgrade pytz
$ sudo pip3 install --upgrade six
```

어떤 패키지들은 다른 패키지에 의해 자동적으로 설치되었을 수도 있다.

### 초기 데이터 수집

* 방송 일정(schedule) 수집

이 작업은 초기 데이터 수집 과정이므로 한 번만 수행하면 된다. 여기서는 데모를 위해 일정 범주의 프로그램들에 대한 일정만 수집한다.

``` shell-session
$ ./crawl_schedule.py --date 20140927 --chan-type 케이블 --chan-cat 음악/오락 --output-file schedule.20140927.cable.music-ent.txt
$ ./crawl_schedule.py --date 20140927 --chan-type 공중파 --chan-cat KBS --output-file schedule.20140927.air.kbs.txt
$ ./crawl_schedule.py --date 20140927 --chan-type 공중파 --chan-cat MBC --output-file schedule.20140927.air.mbc.txt
$ ./crawl_schedule.py --date 20140927 --chan-type 공중파 --chan-cat SBS --output-file schedule.20140927.air.sbs.txt
$ ./crawl_schedule.py --date 20140927 --chan-type 종합편성채널 --chan-cat 종합편성채널 --output-file schedule.20140927.comp.txt
```

`crawl_schedule.py`의 명령행 문법은 다음과 같이 확인할 수 있다.

``` shell-session
$ ./crawl_schedule.py -h
usage: crawl_schedule.py [-h] --date DATE --chan-type CHANTYPE --chan-cat
                         CHANCAT --output-file OUTPUTFILENAME

Crawl TV schedule information from http://movie.daum.net

optional arguments:
  -h, --help            show this help message and exit
  --date DATE           destination date
  --chan-type CHANTYPE  channel type
  --chan-cat CHANCAT    channel category
  --output-file OUTPUTFILENAME
                        output file name

Contact Hwanho Lee <hanwho633@naver.com> for reporting bugs and suggestions.
Copyright (c) 2014 by Hwanho Lee
```

개별 명령행 인자는 위에서 충분히 설명된다. 채널 유형(channel type)과 범주(channel category)는 `tv-star-now/tvinfo/scheduleinfo.py`를 참고하기 바란다.

* 프로그램 정보(program information) 수집

프로그램 정보는 방송 프로그램과 에피소드, 그리고 출연자 정보를 포함한다. 데모를 위해 연예/오락 범주 프로그램들에 대한 정보만 수집한다.

``` shell-session
$ ./crawl_prog_info.py --main-cat 연예/오락 --sub-cat 연예/오락 --output-file programinfo.20140927.txt --min-rating 6
```

`craw_prog_info.py`의 명령행 문법은 다음과 같다.

``` shell-session
$ ./crawl_prog_info.py -h
usage: crawl_prog_info.py [-h] --main-cat MAINCATNAME [--sub-cat SUBCATNAME]
                          --output-file OUTPUTFILENAME
                          [--min-rating MINRATING]

Crawl TV program information from http://movie.daum.net

optional arguments:
  -h, --help            show this help message and exit
  --main-cat MAINCATNAME
                        program main category
  --sub-cat SUBCATNAME  program sub-category
  --output-file OUTPUTFILENAME
                        output file name
  --min-rating MINRATING
                        minimum rating

Contact Hwanho Lee <hanwho633@naver.com> for reporting bugs and suggestions.
Copyright (c) 2014 by Hwanho Lee
```

`--main-cat`과 `--sub-cat` 인자는 TV 프로그램의 주분류와 부분류로서 다음 포털의 서비스에서 사용하는 분류체계를 그대로 사용한다. 이 분류체계의 자세한 내용은 `tv-star-now/tvinfo/proginfo.py`에서 확인할 수 있다.

### 초기 데이터 적재

위에서 수집한 초기 데이터를 MongoDB에 적재한다.

* 방송 일정(schedule) 적재

``` shell-session
$ ./insert_schedule.py --schedule-files schedule.20140927.*.txt
```

`insert_schedule.py`의 명령행 문법은 다음과 같다.

``` shell-session
$ ./insert_schedule.py -h
usage: insert_schedule.py [-h] [--host HOST] [--port PORT] --schedule-files
                          SCHEDULEFILES [SCHEDULEFILES ...]

Insert crawled TV schedule information into MongoDB

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           MongoDB host
  --port PORT           MongoDB port
  --schedule-files SCHEDULEFILES [SCHEDULEFILES ...]
                        schedule information file names

Contact Hwanho Lee <hanwho633@naver.com> for reporting bugs and suggestions.
Copyright (c) 2014 by Hwanho Lee
```

`--host`의 기본값은 `localhost`이며 `--port`의 기본값은 27017이다. `--schedule-files` 인자로 방송 일정 파일 여러 개를 지정할 수 있다.


* 프로그램 정보(program information) 적재

``` shell-session
$ ./insert_prog_info.py --prog-files programinfo.140927.txt
```

`insert_prog_info.py`의 명령행 문법은 다음과 같다.

``` shell-session
$ ./insert_prog_info.py -h
usage: insert_prog_info.py [-h] [--host HOST] [--port PORT] --prog-files
                           PROGINFOFILES [PROGINFOFILES ...]

Insert crawled TV program information into MongoDB

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           MongoDB host
  --port PORT           MongoDB port
  --prog-files PROGINFOFILES [PROGINFOFILES ...]
                        program information file names

Contact Hwanho Lee <hanwho633@naver.com> for reporting bugs and suggestions.
Copyright (c) 2014 by Hwanho Lee
```

이 스크립트의 사용법은 위와 같다.

### API 서버 구동

``` shell-session
$ ./apiserver.py --server-host [도메인명 혹은 IP 주소] >& mylog.log &
```

위와 같이 실행하면 시스템에서 API 서버가 백그라운드에서 구동되며, port는 5000이 기본값이다. 로그 메시지는 `mylog.log` 파일에 기록된다.

`apiserver.py`의 명령행 문법은 다음과 같다.

``` shell-session
$ ./apiserver.py -h
usage: apiserver.py [-h] [--mongo-host MONGOHOST] [--mongo-port MONGOPORT]
                    --server-host SERVERHOST [--server-port SERVERPORT]

Serve TV program episode and schedule information in REST style

optional arguments:
  -h, --help            show this help message and exit
  --mongo-host MONGOHOST
                        MongoDB host
  --mongo-port MONGOPORT
                        MongoDB port
  --server-host SERVERHOST
                        API server address
  --server-port SERVERPORT
                        API server port

Contact Hwanho Lee <hanwho633@naver.com> for reporting bugs and suggestions.
Copyright (c) 2014 by Hwanho Lee
```

`--mongo-host`와 `--mongo-port`의 의미는 위 스크립트의 `--host`와 `--port`와 같다. `--server-host`로 시스템이 구동되는 서버의 도메인명이나 IP 주소를 지정한다. `--server-port`로 기본값 5000이 아닌 포트 값을 지정하는 것도 가능하다.

### 동작 확인 및 실험

웹브라우저로 http://[도메인명 혹은 IP 주소]:5000에 접속하면 API 서비스에서 지원되는 자료 접근 방법을 볼 수 있으며, 직접 실험도 가능하다.
