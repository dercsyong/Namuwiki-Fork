import random
import time
import subprocess
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

worker = "w1"

def foundWrongDocu(tag):
    try:
        for i in tag:
            if i.text=='문서를 찾을 수 없습니다.' or i.text=='해당 리비전이 존재하지 않습니다.':
                return i.text
            else:
                continue
        return None
    except:
        return None

def foundDataValue(tag):
    try:
        vData = []
        soup = BeautifulSoup(tag.get_attribute('outerHTML'), 'html.parser').article.attrs
        for i in soup:
            if i[:7]=='data-v-':
                vData.append(i)
        return vData
    except:
        return []

def foundWrongDocuSpeed(vData):
    text = None
    try:
        text = driver.find_element(By.XPATH, """//div[@"""+vData[0]+"""]/div[@"""+vData[1]+"""]""").text
    except:
        try:
            text = driver.find_element(By.XPATH, """//div[@"""+vData[1]+"""]/div[@"""+vData[0]+"""]""").text
        except:
            text = None
    if text=='문서를 찾을 수 없습니다.' or text=='해당 리비전이 존재하지 않습니다.':
        return text
    else:
        return None

try:
    subprocess.Popen(r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --incognito --remote-debugging-port=9222 --user-data-dir="D:\chtemp"') 
except:
    pass
while(1):
    client = MongoClient('mongodb://DB/')
    db = client.fork
    coll = db.documents
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    while(1):
        print(worker, end=" | ")
        row = coll.find_one({'status':12})
        if row is None:
            sleep(10)
            print('nothing')
            continue
        if row['title'][:3]=="파일:" or row['title'][:3]=="분류:" or row['title'][:5]=="나무위키:" or row['title'][:4]=="휴지통:" or row['title'][:3]=="더미:":
            coll.delete_one({"title":row['title'], "status":None})
            print(row['title'], 'namespace')
            continue

        start = time.time()
        print(row['title'], end=" ")
        coll.update_one({"title":row['title'], "status":12}, {"$set": {"status":0, "worker":worker}})
        driver.get('https://namu.wiki/history/'+row['title'])
        sleepTime = random.uniform(2,4)
        sleep(sleepTime)
        raw = ''
        try:
            raw = driver.find_element_by_id("app").find_elements_by_tag_name("h1")[0].text
        except:
            pass
        if raw=="오류":
            vData = foundDataValue(driver.find_element_by_tag_name("article"))
            if len(vData)>0:
                raw = foundWrongDocuSpeed(vData)
                if raw=="문서를 찾을 수 없습니다.":
                    coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":3, "reason":"not found"}})
                    print('delete', end=" | ")
                    end = time.time()
                    print(f"{end - start:.5f} sec")
                    continue
        whatrev = ''
        try:
            url = driver.find_element_by_tag_name("article").find_elements_by_tag_name("ul")[0].find_elements_by_tag_name("li")[0].find_elements_by_tag_name("a")[4].get_attribute('href').split('&oldrev=')[0]+'&oldrev=1'
            whatrev = driver.find_element_by_tag_name("article").find_elements_by_tag_name("ul")[0].find_elements_by_tag_name("li")[0].find_elements_by_tag_name("a")[4].get_attribute('href').split('?rev=')[1].split('&oldrev=')[0]
            driver.get(url)
        except:
            coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":13}})
            print('fail', end=" | ")
            end = time.time()
            print(f"{end - start:.5f} sec")
            continue
        sleepTime = random.uniform(2,4) #randint(2,4)
        sleep(sleepTime)
        raw = ''
        skipFirst = True
        try:
            try:
                raw = driver.find_element_by_id("app").find_elements_by_tag_name("h1")[0].text
            except:
                pass
            if raw=="오류":
                vData = foundDataValue(driver.find_element_by_tag_name("article"))
                if len(vData)>0:
                    raw = foundWrongDocuSpeed(vData)
                    if raw is not None and raw!='':
                        abc()
            raw = ''
            try:
                raws = driver.find_element_by_id("app").find_elements_by_tag_name("table")[0].find_elements_by_tag_name("tr")
                for i in range(len(raws)):
                    if skipFirst:
                        skipFirst = False
                        continue
                    soup = BeautifulSoup(raws[i].get_attribute('innerHTML'), 'html.parser')
                    try:
                        try:
                            if soup.th.nextSibling.nextSibling.nextSibling.nextSibling['class'][0]=='skip':
                                coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":13}})
                                raws = ''
                                raw = '포크불가'
                                break
                        except:
                            pass
                        try:
                            if soup.th.nextSibling.nextSibling['class'][0]=='skip':
                                coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":13}})
                                raws = ''
                                raw = '포크불가'
                                break
                        except:
                            pass
                        try:
                            if soup.th.nextSibling.nextSibling.nextSibling.nextSibling['class'][0]=='delete':
                                continue
                        except:
                            pass
                        try:
                            if soup.th.nextSibling.nextSibling['class'][0]=='delete':
                                continue
                        except:
                            pass
                        raw = raw + soup.th.nextSibling.nextSibling.nextSibling.nextSibling.text + "\n"
                    except:
                        try:
                            raw = raw + soup.th.nextSibling.nextSibling.text + "\n"
                        except:
                            print('error!')
                            break
                if raw!='포크불가':
                    raw = raw[:-1]
            except:
                try:
                    vData = foundDataValue(driver.find_element_by_tag_name("article"))
                    if len(vData)>0:
                        raw = foundWrongDocuSpeed(vData)
                    else:
                        raw = foundWrongDocu(driver.find_element_by_tag_name("article").find_elements_by_tag_name("div"))
                except:
                    coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$unset": {"status":1, "worker":1}})
                    print('captcha')
                    try:
                        driver.quit()
                        driver = webdriver.Chrome('./chromedriver.exe')
                        driver.implicitly_wait(5)
                    except:
                        pass
                    continue
        except:
            pass
        if raw==None:
            coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":3, "reason":"raw none"}})
            print('none error', end=" | ")
        elif raw=="문서를 찾을 수 없습니다." or raw=='':
            coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":3, "reason":"not found"}})
            print('delete', end=" | ")
        elif raw=="해당 리비전이 존재하지 않습니다.":
            coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"status":3, "reason":"rev"}})
            print('rev error', end=" | ")
        elif raw=="포크불가":
            print('fail', end=" | ")
        else:
            try:
                coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$set": {"rev":int(whatrev), "status":1, "raw":raw, "fork_date":str(datetime.now()).split('.')[0]}})
                print('fork', end=" | ")
            except:
                try:
                    coll.update_one({"title":row['title'], "status":0, "worker":worker}, {"$unset": {"status":1, "worker":1}})
                except:
                    pass
                print('db error', end=" | ")
        end = time.time()
        print(f"{end - start:.5f} sec")
