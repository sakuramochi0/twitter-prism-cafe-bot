import datetime
import io
import tempfile
from selenium.webdriver import PhantomJS
from PIL import Image
from get_tweepy import get_api


tmp_path = tempfile.mktemp('.png')
url = 'http://cafereserve.animate.co.jp/vacancy?group_id=11166'

api = get_api('rl_cafe_reserve')
br = PhantomJS()

# open reserve page
br.get(url)

# adjust prresentation
br.set_window_size(1024, 1500)
br.execute_script("$('.timeTableData').css('overflow-x', 'hidden')")

# save screenshot
img = Image.open(io.BytesIO(br.get_screenshot_as_png()))
crop = img.crop((0, 165, 1024, 1066))
crop.save(tmp_path)

# tweet image
now = datetime.datetime.now()
date = '{t.month}/{t.day}({week}) {t.hour}:{t.minute:02d}'.format(t=now, week='月火水木金土日'[now.weekday()])
status = '{}現在の空席状況です♪'.format(date)
api.update_with_media(tmp_path, status=status)
