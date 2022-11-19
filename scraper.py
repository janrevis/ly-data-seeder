from cmath import e
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv
import time
import json
import re
from lib.OSClient import OSClient
from lib.farmers_market_mapping import create_mapping, farmers_market_mapping

DATE_PATTERN = re.compile("^(\w+)\s*\/?\s*(\w*).*$")
TIME_PATTERN = re.compile("(\w+):(\w+)\s+(AM|PM|am|pm)")

def get_market_count(driver):
  node = WebDriverWait(driver, 10) \
    .until(
      EC.presence_of_element_located(
        (By.XPATH, '//div[contains(text(), "National_Farmers_Market_Directory")]')
      )
    )
  pattern = re.compile("\d\d+")
  match = re.search(pattern, node.text)
  return int(match.group(0))


month_map = {
  "january": 1,
  "february": 2,
  "march": 3,
  "april": 4,
  "may": 5,
  "june": 6,
  "july": 7,
  "august": 8,
  "september": 9,
  "october": 10,
  'octobsr': 10,
  "november": 11,
  "december": 12,
  "jan": 1,
  "feb": 2,
  "mar": 3,
  "apr": 4,
  "may": 5,
  "jun": 6,
  "jul": 7,
  "aug": 8,
  "sept": 9,
  "oct": 10,
  "nov": 11,
  "dec": 12
}

def build_media(marketData):
  media = {}
  if marketData[2].text != "":
    media["website"] = marketData[2].text
  if marketData[3].text != "":
    media["facebook"] = marketData[3].text
  if marketData[4].text != "":
    media["twitter"] = marketData[4].text
  if len(media) == 0:
    return None
  return media

def build_range_end(date):
  match = re.match(DATE_PATTERN, date)
  month = None
  date = None
  try:
    month = int(match.group(1))
  except:
    month = month_map[match.group(1).lower()]
  try:
    date = match.group(2)
    if date == '':
      date = 1
  except:
    date = 1
  return {
    "month": month,
    "date": int(date)
  }

def buildTimes(hours):
  hourSlots = hours.split(";")
  days = {}
  for slot in hourSlots:
    key = slot[0: slot.index(":")]
    value = slot[slot.index(":") + 1:]
    matches = re.findall(TIME_PATTERN, value)
    if len(matches) == 2:
      days[key] = {
        "start": {
          "hours": int(matches[0][0]) 
            if matches[0][2].upper() == "AM" else int(matches[0][0]) + 12,
          "minutes": int(matches[0][1])
        },
        "end": {
          "hours": int(matches[1][0]) 
            if matches[0][2].upper() == "AM" else int(matches[1][0]) + 12,
          "minutes": int(matches[1][1])
        }
      }
    return days


def build_hours(season, hours):
  if season != "" and hours != "":
    built = { "hours": buildTimes(hours)}
    seasonRange = season.split(" to ")
    if len(seasonRange) < 2:
      built["yearRound"] = True
    else:
      built["start"] = build_range_end(seasonRange[0])
      built["end"] = build_range_end(seasonRange[1])
    return built
  return None
  

def process_market(registeredRows, row):
  market = {
    "usda_id": row[0].text,
    "name": row[1].text,
    "address": {
      "street": row[7].text,
      "city": row[8].text,
      "state": row[10].text,
      "postal": row[11].text,
    },    
  }
  media = build_media(row)
  if media != None:
    market["media"] = media
  season1 = build_hours(row[12].text, row[13].text)
  season2 = build_hours(row[14].text, row[15].text)
  season3 = build_hours(row[16].text, row[17].text)
  season4 = build_hours(row[18].text, row[19].text)

  if season1 != None:
    market["season1"] = season1
  if season2 != None:
    market["season2"] = season1
  if season3 != None:
    market["season3"] = season1
  if season4 != None:
    market["season4"] = season1
  market["location"] = {
    "x": float(row[20].text),
    "y": float(row[21].text)
  }
  registeredRows[row[0].text] = market
registeredMarkets = {}
client = OSClient()
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
url = "https://www.arcgis.com/home/item.html?id=f2753f1d27e14fffb97b3f2eabd6813c&sublayer=0#data"
driver.get(url)
marketCount = get_market_count(driver)
time.sleep(5)
scroller = WebDriverWait(driver, 10) \
  .until(
    EC.presence_of_element_located(
      (By.CLASS_NAME, "dgrid-scroller")
    )
  )
current = 0
while len(registeredMarkets) < marketCount:
  rows = driver.find_elements(By.XPATH, '//*[contains(@id, "dgrid_0-row-")]')
  for i in range(len(rows)):
    marketRow = rows[i].find_elements(By.XPATH, ".//td/div")
    process_market(registeredMarkets, marketRow)
  scrollToPos = rows[len(rows) - 1].location['y']
  driver.execute_script(
    'arguments[0].scrollIntoView()', rows[len(rows) - 1]
  )
  print("market count: {}, regstered markets {}"
    .format(marketCount, len(registeredMarkets)))
  time.sleep(2)
driver.close()
print(registeredMarkets)
jsonFile = open("market-data.json", "w") 
jsonFile.write(json.dumps(registeredMarkets, indent=2))
jsonFile.close()
