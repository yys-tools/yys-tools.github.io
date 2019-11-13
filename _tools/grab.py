
import os
import re
import requests
# import time
from bs4 import BeautifulSoup

URL = 'http://cc.koncoo.com/yys/'
DATA_DIR = "_data"
content = requests.get(URL).content
soup = BeautifulSoup(content, features="lxml")

monsters = soup.body.form.find_all('span', class_=re.compile('label label-.*'))
monsters = [monster.get_text() for monster in monsters]
monsters = sorted(set(monsters))

print(monsters)

decoded_content = content.decode("utf-8")
view_state = re.compile(r'id="__VIEWSTATE" value="(.+)" />').findall(decoded_content)[0]
event_validation = re.compile(r'id="__EVENTVALIDATION" value="(.+)" />').findall(decoded_content)[0]

monsters_data = {}
if not os.path.isdir(DATA_DIR):
  os.mkdir(DATA_DIR)
if not os.path.isdir(os.path.join(DATA_DIR, "monsters")):
  os.mkdir(os.path.join(DATA_DIR, "monsters"))

for monster in monsters:
  print("Parsing %s" % monster)
  headers = {
    "Content-Type": "application/x-www-form-urlencoded"
  }
  data = {
    'txtName': monster,
    '__EVENTTARGET': 'lnkSearch',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': view_state,
    '__EVENTVALIDATION': event_validation,
  }

  html1 = requests.post(URL, headers=headers, data=data).content
  soup1 = BeautifulSoup(html1, features="lxml")

  # has_table = False
  # while not has_table:
  #   try:
  #     table = soup1.find_all("table", class_="table table-hover table-striped")[0]
  #   except IndexError:
  #     print("Retrying to grab table ...")
  #     time.sleep(2.0)
  #     continue
  #   has_table = True

  try:
    table = soup1.find_all("table", class_="table table-hover table-striped")[0]
  except IndexError:
    print("Empty table")
    continue

  table = table.tbody
  monster_data = []
  monster_filname = os.path.join(DATA_DIR, "monsters", "%s.csv" % monster)
  with open(monster_filname, "w") as fp:
    for row in table.find_all("tr"):
      g = [item.get_text().strip() for item in row.find_all("td")]
      fp.write('%s, %s, %s, %s\n' % (g[0], g[1], g[2], g[3]))
      monster_data.append(g)
  monsters_data[monster] = monster_data
