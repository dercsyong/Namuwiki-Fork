import random
import time
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from ppadb.client import Client as AdbClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

worker = "ffffffff"
worker1 = "ffff"

client = MongoClient('mongodb://DB/')
db = client.fork
coll = db.documents
sub_coll = db.backlinks

def foundWrongDocu(tag):
    try:
        for i in tag:
            if i.text=='문서를 찾을 수 없습니다.' or i.text=='해당 문서를 찾을 수 없습니다.' or i.text=='해당 리비전이 존재하지 않습니다.' or i.text=='CAPTCHA 인증이 실패했습니다.':
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
    if text=='문서를 찾을 수 없습니다.' or text=='해당 문서를 찾을 수 없습니다.' or text=='해당 리비전이 존재하지 않습니다.' or text=='CAPTCHA 인증이 실패했습니다.':
        return text
    else:
        return None

dCHK = False
dCNT = 0
bSRL = None
while(1):
    while(dCHK==False):
        try:
            adb = AdbClient(host="127.0.0.1", port=5037)
            devices = adb.devices()
            i = None
            if len(devices)>0:
                if len(devices)>1:
                    print('please select device')
                    for device in devices:
                        print(device.get_serial_no())
                    if bSRL is not None:
                        worker = bSRL
                    else:
                        print('input : ', end='')
                        worker = input()
                else:
                    if bSRL is not None:
                        worker = bSRL
                    else:
                        worker = devices[0].get_serial_no()
                for device in devices:
                    if device.get_serial_no()==worker:
                        serial = worker
                        bSRL = worker
                        i = device
                        break
                i.shell("am force-stop com.android.chrome")
                i.shell("settings put system screen_brightness 0")
            options = webdriver.ChromeOptions()
            options.add_experimental_option('androidDeviceSerial', serial)
            options.add_experimental_option('androidPackage', 'com.android.chrome')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            #driver = webdriver.Chrome('./chromedriver', options=options)
            driver.implicitly_wait(5)
            dCHK = True
        except:
            dCHK = False
            dCNT = dCNT + 1
            try:
                driver.quit()
            except:
                pass
            print('adb', dCNT, "count..")
            sleep(1)
    worker1 = worker[:4]
    print('device selected :', worker)
    while(dCHK):
        print(worker, end=" | ")
        try:
            end = time.time()
            test = end - start
            if test<15:
                test = 15 - test
                if test<0:
                    test = 0
                #test = random.uniform(test, 15)
                #print('sleep', test, 'sec', end=" | " )
                sleep(test)
        except:
            pass
        dCNT = 0
        try:
            skipThis = False
            row = coll.find_one({'status':13})
            if row is None:
                row = coll.find_one({'status':12})
                if row is None:
                    row = coll.find_one({'status':None})
                    if row is None:
                        sleep(10)
                        print('nothing')
                        continue
            else:
                skipThis = True
            if row['title'][:3]=="파일:" or row['title'][:3]=="분류:" or row['title'][:5]=="나무위키:" or row['title'][:4]=="휴지통:" or row['title'][:3]=="더미:" or row['title'][:5]=="위키운영:":
                coll.delete_one({"_id":row['_id']})
                print(row['title'], 'namespace')
                continue

            start = time.time()
            print(row['title'], end=" ")
            coll.update_one({"_id":row['_id']}, {"$set": {"status":0, "worker":worker1}})
            driver.get('https://namu.wiki/raw/'+row['title'])
            try:
                t = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.TAG_NAME, 'h1'))).text
                sleepTime = 0
            except:
                t = ''
                sleepTime = random.uniform(10,15)
            sleep(sleepTime)
            while driver.find_element(By.TAG_NAME, 'body').get_attribute('class')=='no-js':
                driver.delete_all_cookies()
                driver.refresh()
                sleepTime = random.uniform(2,4)
                sleep(sleepTime)
            whatrev = ''
            raw = ''
            if t=="비정상적인 트래픽 감지":
                print('captcha')
                input()
                continue
            try:
                if t=='오류':
                    try:
                        try:
                            vData = foundDataValue(driver.find_element(By.ID, "app"))
                        except:
                            vData = foundDataValue(driver.find_element(By.TAG_NAME, "article"))
                        if len(vData)>0:
                            raw = foundWrongDocuSpeed(vData)
                        else:
                            raw = foundWrongDocu(driver.find_element(By.TAG_NAME, "article").find_elements(By.TAG_NAME, "div"))
                    except:
                        pass
                if t!='오류' or raw==None or raw=="":
                    try:
                        raw = driver.find_element(By.ID, "app").find_elements(By.TAG_NAME, "h1")[0].text
                    except:
                        try:
                            raw = driver.find_element(By.TAG_NAME, "article").find_elements(By.TAG_NAME, "h1")[0].text
                        except:
                            pass
            except:
                pass
            if raw is None or raw=="오류" or raw=="해당 문서를 찾을 수 없습니다." or raw=="문서를 찾을 수 없습니다." or raw=="" or raw=="해당 리비전이 존재하지 않습니다.":
                coll.update_one({"_id":row['_id']}, {"$set": {"status":3, "reason":"not found"}})
                print('delete', end=" | ")
                end = time.time()
                print(f"{end - start:.5f} sec")
                continue
            raw = ''
            try:
                try:
                    whatrev = driver.find_element(By.ID, "app").find_elements(By.TAG_NAME, "h1")[0].find_elements(By.TAG_NAME, "small")[0].text[2:].split(' ')[0]
                except:
                    whatrev = ''
                raw = driver.find_element(By.ID, "app").find_element(By.TAG_NAME, "textarea").text
            except:
                try:
                    vData = foundDataValue(driver.find_element(By.TAG_NAME, "article"))
                    if len(vData)>0:
                        raw = foundWrongDocuSpeed(vData)
                    else:
                        raw = foundWrongDocu(driver.find_element(By.TAG_NAME, "article").find_elements(By.TAG_NAME, "div"))
                except:
                    coll.update_one({"_id":row['_id']}, {"$unset": {"status":1, "worker":1}})
                    try:
                        print('result : captcha test')
                        device.shell("am force-stop com.android.chrome")
                        device.shell("settings put system screen_brightness 0")
                        driver.quit()
            
                        del adb
                        del devices
                        del device
                        dCHK = False
                    except:
                        pass
                    continue
            if raw==None:
                coll.update_one({"_id":row['_id']}, {"$set": {"status":None, "reason":"raw none"}})
                print('result : none error', end=" | ")
            elif raw=="문서를 찾을 수 없습니다." or raw=="":
                coll.update_one({"_id":row['_id']}, {"$set": {"status":3, "reason":"not found"}})
                print('result : delete', end=" | ")
            elif raw=="해당 리비전이 존재하지 않습니다.":
                coll.update_one({"_id":row['_id']}, {"$set": {"status":3, "reason":"rev"}})
                print('result : rev error', end=" | ")
            elif raw=="CAPTCHA 인증이 실패했습니다.":
                coll.update_one({"_id":row['_id']}, {"$set": {"status":None, "reason":"captcha"}})
                print('result : captcha error', end=" | ")
            else:
                if raw[:9]!="#redirect" and raw[:5]!="#넘겨주기":
                    try:
                        if skipThis:
                            pass
                        else:
                            sub_coll.update_one({"title":row['title']}, {"$set": {"status":None, "where":serial, "date":time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}}, upsert=True)
                    except:
                        pass
                try:
                    coll.update_one({"_id":row['_id']}, {"$set": {"rev":int(whatrev), "status":1, "raw":raw, "fork_date":str(datetime.now()).split('.')[0]}})
                    print('result : fork', end=" | ")
                except:
                    try:
                        coll.update_one({"_id":row['_id']}, {"$unset": {"status":1, "worker":1}})
                    except:
                        pass
                    print('result : db error', end=" | ")
            end = time.time()
            print(f"{end - start:.5f} sec")
        except:
            try:
                coll.update_one({"_id":row['_id']}, {"$unset": {"status":1, "worker":1}})
            except:
                pass
            print('result : browser error')
            driver.quit()
            del adb
            del devices
            del device
            dCHK = False
