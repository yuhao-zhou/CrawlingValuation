import re
import time
import urllib
import requests
from bs4 import BeautifulSoup
from os import path
from selenium import webdriver
import pandas as pd
from datetime import datetime

def strip_all(s):
    return re.sub("[^\d\.,]", "", s)

def logfile(log_info):
    log_path = path.join(path.dirname(path.abspath(__file__)), 'log_valuation.txt') # though the directory is relative, better use the absolute
    with open(log_path, "a") as file:
        file.write(log_info + '\n')  # append file

wait = 60
try:
    logfile('program started on ' + str(datetime.today()))  # update log

    today = datetime.today().date()  # use for saved data

    # prepare csv file for index, valuation, and guru
    csv_path_index = path.join(path.dirname(path.abspath(__file__)), 'morningstar_index.csv')  # though the directory is relative, better use the absolute
    df_index = pd.read_csv(csv_path_index)

    csv_path_val = path.join(path.dirname(path.abspath(__file__)), 'morningstar_val.csv')
    df_val = pd.read_csv(csv_path_val)

    csv_path_guru = path.join(path.dirname(path.abspath(__file__)), 'guru.csv')
    df_guru = pd.read_csv(csv_path_guru)



    # open morningstar webpage
    url = "https://www.morningstar.co.uk/uk/Markets/global-market-barometer.aspx"  # use for pdf download link
    options = webdriver.ChromeOptions()  # suppress chrome popping
    options.add_argument('-headless')
    options.add_argument('window-size=1920x1080') # need set window size for clickable things
    options.add_argument('--no-sandbox') # Bypass OS security model
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    time.sleep(wait)  # conservative waiting for web loading

    # click the options required for visiting the website
    browser.find_elements_by_xpath("//*[contains(text(), 'I am a financial professional')]")[0].click()
    browser.find_elements_by_id("_evidon-accept-button")[0].click()
    time.sleep(wait)
    browser.find_element_by_xpath("//input[@value='Grid']").click()
    time.sleep(wait)
    soup = BeautifulSoup(browser.page_source, features="lxml")


    # record the index today
    country_string_lst = soup.find_all(string = re.compile('^Morningstar '))

    index_dic = {"Date":today}
    for c in country_string_lst:
        country = c.split()[1]  # get country name

        # extract column value
        try:
            index = strip_all(c.parent.parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text)
            index_dic[country] = index

        # abandon extra tags
        except:
            pass
    print(index_dic)
    df_index = df_index.append(index_dic, ignore_index=True)
    df_index.to_csv(csv_path_index, index=False)
    print(df_index)

    # record the valuation today
    browser.find_element_by_xpath("//input[@value='Valuation']").click()
    time.sleep(wait)

    soup = BeautifulSoup(browser.page_source, features="lxml")
    country_string_lst = soup.find_all(string = re.compile('^Morningstar '))

    val_dic = {"Date":today}
    for c in country_string_lst:
        country = c.split()[1]
        try:
            val = strip_all(c.parent.parent.next_sibling.next_sibling.next_sibling.next_sibling.text)
            val_dic[country] = val
        except:
            pass
    print(val_dic)
    df_val = df_val.append(val_dic, ignore_index=True)
    df_val.to_csv(csv_path_val,index=False)
    print(df_val)
    browser.quit()

    # open guru webpage
    url = "https://www.gurufocus.com/global-market-valuation.php"  # use for pdf download link
    options = webdriver.ChromeOptions()  # suppress chrome popping
    options.add_argument('-headless')
    options.add_argument('window-size=1920x1080') # need set window size for clickable things
    options.add_argument('--no-sandbox') # Bypass OS security model
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    time.sleep(wait)  # conservative waiting for web loading
    browser.find_elements_by_id("cboxClose")[0].click()
    time.sleep(wait)
    soup = BeautifulSoup(browser.page_source, features="lxml")

    lst = soup.find_all(class_ = re.compile('^date$'))
    del lst[0]

    guru_dic = {"Date":today}
    for item in lst:
        growth = item.text
        country = item.parent.parent.previous_sibling.text
        guru_dic[country] = growth

    df_guru = df_guru.append(guru_dic, ignore_index=True)
    print(df_guru)

    df_guru.to_csv(csv_path_guru,index=False)

    browser.quit()

except Exception as e:
    logfile('program error on' + str(datetime.today()) + str(e))  # update log


finally:
    logfile('program finished on' + str(datetime.today()))  # update log

