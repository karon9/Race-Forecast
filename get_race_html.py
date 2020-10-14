"""
race_urlディレクトリに含まれるURLを利用して、htmlを取得する
"""
import datetime
import pytz

# now_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

import requests
from bs4 import BeautifulSoup

import time
import os
from os import path
import csv

OWN_FILE_NAME = path.splitext(path.basename(__file__))[0]
RACR_URL_DIR = "race_url"
RACR_HTML_DIR = "race_html"

#  直近のデータを取得したいならnow_datetime.yearなどを代入
now_year = 2020
now_month = 6

import logging

logger = logging.getLogger(__name__)  # ファイルの名前を渡す


def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def get_race_html(session):
    # 去年までのデータ
    for year in range(2008, now_year):
        for month in range(1, 13):
            get_race_html_by_year_and_mon(year, month, session)
    # 今年のデータ
    for year in range(now_year, now_year + 1):
        for month in range(1, now_month + 1):
            get_race_html_by_year_and_mon(year, month, session)


def get_race_html_by_year_and_mon(year, month, session):
    with open(RACR_URL_DIR + "/" + str(year) + "-" + str(month) + ".txt", "r") as f:
        save_dir = RACR_HTML_DIR + "/" + str(year) + "/" + str(month)
        my_makedirs(save_dir)
        urls = f.read().splitlines()

        file_list = os.listdir(save_dir)  # get all file names

        # 取得すべき数と既に保持している数が違う場合のみ行う
        if len(urls) != len(file_list):
            logger.info("getting htmls (" + str(year) + " " + str(month) + ")")
            for url in urls:
                list = url.split("/")
                race_id = list[-2]
                save_file_path = save_dir + "/" + race_id + '.html'
                if not os.path.isfile(save_file_path):  # まだ取得していなければ取得
                    response = session.get(url)
                    response.encoding = response.apparent_encoding  # https://qiita.com/nittyan/items/d3f49a7699296a58605b
                    html = response.text
                    time.sleep(1)
                    with open(save_file_path, 'w') as file:
                        file.write(html)
                        print(f"finished {url}")
            logging.info("saved " + str(len(urls)) + " htmls (" + str(year) + " " + str(month) + ")")
        else:
            logging.info("already have " + str(len(urls)) + " htmls (" + str(year) + " " + str(month) + ")")


def login__netkeiba():
    with open("login_id.csv") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        USER = str(l[0][1])
        PASS = str(l[1][1])

    # セッションを開始
    session = requests.session()

    # ログイン
    login_info = {
        "login_id": USER,
        "pswd": PASS,
        "pid": "login",
        "action": "auth",
    }

    # action
    url_login = "https://regist.netkeiba.com/account/?pid=login"
    session.post(url_login, data=login_info)
    race = session.get("https://db.netkeiba.com/race/200806010801/")
    race.encoding = race.apparent_encoding
    html = race.text
    save_file_path = os.getcwd() + "/test.html"
    with open(save_file_path, 'w') as file:
        file.write(html)
    return session


if __name__ == '__main__':
    session = login__netkeiba()
    get_race_html(session)
