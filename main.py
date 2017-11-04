import argparse
import datetime
import io
import tempfile
from urllib.parse import urljoin
from selenium.webdriver import PhantomJS
from bs4 import BeautifulSoup
from PIL import Image
from get_tweepy import get_api


def get_now_string():
    '''現在時刻を表す文字列を取得する'''
    now = datetime.datetime.now()
    return '{t.month}/{t.day}({week}) {t.hour}:{t.minute:02d}'.format(
        t=now, week='月火水木金土日'[now.weekday()])


def tweet(status, img_path=None):
    '''画像ありまたは画像なしのツイートをする'''
    if img_path is None:
        api.update_status(status=status)
    else:
        api.update_with_media(img_path, status=status)


def tweet_for_date(date, url):
    '''週ごとの予約ページを開き、スクリーンショット付きツイートをする'''
    br.get(url)
    print(url)

    # ウィンドウを表示を調整する
    br.set_window_size(1024, 1500)
    br.execute_script("$('.timeTableData').css('overflow-x', 'hidden')")

    # スクリーンショットは「戻る」ボタンの直上で切り取る
    tmp_path = tempfile.mktemp('.png')
    bottom = br.find_element_by_css_selector('.btn.back').location['y']
    img = Image.open(io.BytesIO(br.get_screenshot_as_png()))
    crop = img.crop((0, 165, 1024, bottom))
    crop.save(tmp_path)

    # スクリーンショット付きツイートをする
    status = '「{date}」\nの空席状況です♪\n予約はこちらからどうぞ↓\nhttp://cafereserve.animate.co.jp/store?fair_id=129\n#プリリズカフェ [{now}時点]'.format(
        now=get_now_string(),
        date=date,
    )
    tweet(status, img_path=tmp_path)


def main():
    # レインボーライブカフェの日程一覧ページを開く
    url = 'http://cafereserve.animate.co.jp/store?fair_id=129'
    br.get(url)
    s = BeautifulSoup(br.page_source, 'lxml')

    # 各日程ごとにツイートする
    trs = s.select('.shopSelect tbody tr')
    for tr in trs:
        date = tr.select('th')[0].text.replace('\n', '')
        btn = tr.select('.btn')[0]

        # 満席の場合 "close" が含まれる
        if 'close' in btn['class']:
            status = '現在「{date}」\nの予約は満席です！\n#プリリズカフェ [{now}時点]'.format(
                date=date,
                now=get_now_string())
            tweet(status)
        else:
            date_url = urljoin(url, btn['href'])
            tweet_for_date(date, date_url)


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        api = get_api('sakuramochi_pre')
    else:
        api = get_api('prism_cafe_bot')
    br = PhantomJS()

    main()
