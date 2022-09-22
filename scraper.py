from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import json

from lib.OSClient import OSClient
from lib.farmers_market_mapping import create_mapping, farmers_market_mapping

client = OSClient()
client.delete_index("farmers-markets")
if not client.has_index("farmers-markets"):
  ret = client.create_index("farmers-markets", farmers_market_mapping)
else:
  client.put_mapping("farmers-markets", farmers_market_mapping)
csvfile = open("./farmersmarket_2022-918214156.csv")
reader = csv.reader(csvfile, delimiter=',', quotechar='"')
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
markets = {}
firstRow = True
for row in reader:
  if firstRow:
    firstRow = False
    continue
  entry = {
    "usdaId": row[0],
    "name": row[2],
    "address": row[3],
    "x": row[25],
    "y": row[26],
  }
  print("get entry {}".format(row[0]))
  url = "https://www.usdalocalfoodportal.com/fe/flisting/?lid={}&directory_type=farmersmarket".format(row[0])
  driver.get(url)
  time.sleep(2)
  times = []
  try:
    WebDriverWait(driver, 10) \
      .until(
        EC.presence_of_element_located(
          (By.XPATH, "//div[contains(@class, 'otherinfo')]")
        )
      )
    container = driver.find_element(By.XPATH, "//div[contains(@class, 'otherinfo')]")
    blocks = container.find_elements(By.XPATH, "./div[not(@class)]")
    hours = []
    for block in blocks:
      try:
        season = block.find_element(By.XPATH, ".//div")
        times = block.find_element(By.XPATH, ".//li")
        if not season.text.startswith("Available Products"):
          hours.append({
            "season": season.text, 
            "times": times.text
          })
        else:
          print("skipping products: {}".format(season))
      except:
        print("not found")
    entry["data"] = {
      "openHours": hours
    }
    markets[row[0]] = entry
    print(entry)
    client.add_doc("farmers-markets", entry)
  except Exception as e: 
    print(e)
  # target = open(r"markets.json", "w+")
  # target.write(json.dumps(markets)) 

driver.close()