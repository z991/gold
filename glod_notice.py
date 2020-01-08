import requests
import time
import os
import sys
import configparser
from datetime import datetime
from dingtalkchatbot.chatbot import DingtalkChatbot

url = "https://www.g-banker.com/price/query/"


def send_dingding(message):
    """
    利用钉钉推送公交信息
    :param message:
    :return:
    """
    webhook = "钉钉机器人的webhood"
    xiaoding = DingtalkChatbot(webhook)
    xiaoding.send_text(msg=message, is_at_all=True)


def daemon():
    # create - fork 1
    try:
        pid = os.fork()
        if pid > 0:
            return pid
    except OSError as error:
        pass
        return -1
    # it separates the son from the father
    # os.chdir('/opt/pbx')
    os.setsid()
    os.umask(0)
    # create - fork 2
    try:
        pid = os.fork()
        if pid > 0:
            return pid
    except OSError as error:
        return -1
    sys.stdout.flush()
    sys.stderr.flush()
    si = open("/dev/null", 'r')
    so = open("/dev/null", 'a+')
    se = open("/dev/null", 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    main()

    return 0


def main():
    while True:
        conf = configparser.ConfigParser()
        conf.read("cfg.ini")
        max_price = conf.get("gold", "max_price")
        min_price = conf.get("gold", "min_price")
        max_price = int(max_price)
        min_price = int(min_price)

        now = datetime.now()
        week = now.weekday()
        actual_week = week + 1
        hour = now.hour
        min = now.minute
        if actual_week in range(1, 6):  # 在周一到周五
            if hour > 0:  # 如果小时 在凌晨一点以后
                if hour < 18 or (hour < 19 and min < 30):  # 当前如果小于18点30
                    time.sleep(5)
                    response = requests.post(url=url, json={"queryFlag": 3})
                    result = response.json()
                    realtime_price = result.get("data", {}).get("realtime_price")
                    price_str = str(realtime_price / 100)
                    if realtime_price > max_price:
                        message = f"当前黄金价格为{price_str}元， 可以卖出了"
                        send_dingding(message)

                    if realtime_price < min_price:
                        message = f"当前黄金价格为{price_str}元， 可以买点了"
                        send_dingding(message)


if __name__ == '__main__':
    main()
