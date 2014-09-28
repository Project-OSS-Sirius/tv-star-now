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

* 프로그램 정보(program information) 수집

프로그램 정보는 방송 프로그램과 에피소드, 그리고 출연자 정보를 포함한다. 데모를 위해 연예/오락 범주 프로그램들에 대한 정보만 수집한다.

``` shell-session
$ ./crawl_prog_info.py --main-cat 연예/오락 --sub-cat 연예/오락 --output-file programinfo.20140927.txt --min-rating 6
```

### 초기 데이터 적재

위에서 수집한 초기 데이터를 MongoDB에 적재한다.

* 방송 일정(schedule) 적재

``` shell-session
$ ./tv-star-now/insert_schedule.py --schedule-files schedule.20140927.*.txt
```

* 프로그램 정보(program information) 적재

``` shell-session
$ ./tv-star-now/insert_prog_info.py --prog-files programinfo.140927.txt
```

### API 서버 구동

``` shell-session
$ ./apiserver.py --server-host [도메인명 혹은 IP 주소]
```

위와 같이 실행하면 시스템에서 API 서버가 구동되며, port는 5000이 기본값이다.

### 동작 확인 및 실험

웹브라우저로 http://[도메인명 혹은 IP 주소]:5000에 접속하면 API 서비스에서 지원되는 자료 접근 방법을 볼 수 있으며, 직접 실험도 가능하다.
