#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Copyright (c) 2021 anoduck

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------------
# Jeezus this code is a fucking mess...

import requests
import shutil
import argparse
import os
import platform
import sys

#For pathlib
from pathlib import *

# For loading config.py
from . import config

# Custom Imports for time banning.
import time
import traceback
from random import randint
from retrying import retry
from furl import furl
from selenium.webdriver.remote.errorhandler import ErrorHandler

# For Social Analyzer
# from importlib import import_module
# SocialAnalyzer = import_module("social-analyzer").SocialAnalyzer(silent=True)

# For webdriver and friends
import yaml
from ratelimit import limits
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.common.exceptions import ErrorInResponseException, TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------------------------------------
# -------------------------------------------------------------


# ## Global Variables

# In[114]:


# Global Variables
driver = webdriver.Firefox()
opts = Options()
opts.add_argument(
    '--user-agent=Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'  # noqa: E501
    )
opts.add_argument("--headless")
opts.add_argument("--no-sandbox")
opts.add_argument("--lang=en-US")
opts.add_argument("--dns-prefetch-disable")
# opts.add_argument("--start-maximized")

# For requests library
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}  # noqa: E501

# Makes sure slower connections work as well
driver.implicitly_wait(25)

# whether to download photos or not
download_uploaded_photos = True
download_friends_photos = False

# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick,
# else if its false then it will open each photo to download it
# and it will take much more time
friends_small_size = False
photos_small_size = False

total_scrolls = 2500
current_scrolls = 0
scroll_time = 20

old_height = 0
facebook_https_prefix = "https://"
facebook_link_body = "mbasic.facebook.com/"

# Reducing these values now that a scroll time period has been added
# to avoid rate limit. Actually did not change them.

# Values for rate limiting | lower is slower!
# Last worked at: low=10,high=25,time=600
# Failed at: low=3,high=10,time=300
rtqlow = 10
rtqhigh = 25
# You don't really need to change these at all.
rltime = 600
rhtime = 900

# Traversal speed is solely controlled by this variable
# Vales for time sleep in secs
# Last worked at: min=25,max=40
# Failed at: min=20, max=40
tsmin = 15
tsmax = 30

# For gender scraping | Binary only, either "Male", "Female", or "All"
desired_gender = "Female"

# Setup webdriverwait variable
wait = WebDriverWait(driver, 47)

# CHROMEDRIVER_BINARIES_FOLDER = "bin"
Firefox(executable_path="/usr/local/bin/geckodriver")

# =========================================================================

# ## Config
# In[ ]:

# -------------------------------------
#  _____              __ _
# /  __ \            / _(_)
# | /  \/ ___  _ __ | |_ _  __ _
# | |    / _ \| '_ \|  _| |/ _` |
# | \__/\ (_) | | | | | | | (_| |
#  \____/\___/|_| |_|_| |_|\__, |
#                           __/ |
#                          |___/
# -------------------------------------

def load_config():
    if os.path.exists("config.py"):
        Firefox(executable_path=config.driver)
        desired_gender = config.desired_gender
        username = config.username
        password = config.password
        input_file = config.input_file
# ## Boolean

# In[ ]:

#########################################
#     ___           _                   #
#    | _ ) ___  ___| |___ __ _ _ _      #
#    | _ \/ _ \/ _ \ / -_) _` | ' \     #
#    |___/\___/\___/_\___\__,_|_||_|    #
#                                       #
#########################################


def to_bool(x):
    if x in ["False", "0", 0, False]:
        return False
    elif x in ["True", "1", 1, True]:
        return True
    else:
        raise argparse.ArgumentTypeError("Boolean value expected")

# ----------------------------------------------------------------
# ______     _
# | ___ \   | |
# | |_/ /___| |_ _ __ _   _
# |    // _ \ __| '__| | | |
# | |\ \  __/ |_| |  | |_| |
# \_| \_\___|\__|_|   \__, |
#                      __/ |
#                     |___/
# -----------------------------------------------------------------

def retry_on_timeout(exception):
    """ Return True if exception is Timeout """
    return isinstance(exception, TimeoutException)
    
def retry_on_NoSuchElement(exception):
    return isinstance(exception, NoSuchElementException)
    
def retry_response(exception):
    return isinstance(exception, ErrorInResponseException)

# ---------------------------------------------------------
###################################################################
#      ___      _ _               __      __    _ _               #
#     / __|__ _| | |___ _ _ _  _  \ \    / /_ _| | |_____ _ _     #
#    | (_ / _` | | / -_) '_| || |  \ \/\/ / _` | | / / -_) '_|    #
#     \___\__,_|_|_\___|_|  \_, |   \_/\_/\__,_|_|_\_\___|_|      #
#                           |__/                                  #
###################################################################
# ----------------------------------------------------------

@retry(retry_on_exception=retry_response, stop_max_attempt_number=5)
@retry(retry_on_exception=retry_on_timeout, stop_max_attempt_number=7)
@retry(retry_on_exception=retry_on_NoSuchElement, stop_max_attempt_number=3)
@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def gallery_walker():
    list_number = str(randint(1, 99999))
    image_file = "/tmp/image_url" + list_number + ".txt"
    phset = False
    while phset is False:
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//td/div/a")))
        photos_links = driver.find_elements_by_xpath("//td/div/a")  # noqa: E501
        for i in photos_links:
            image_link = i.get_attribute("href")
            q = open(image_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
            q.writelines(image_link)
            q.write("\n")
            q.close()
        try:
            gallery_set = driver.find_element_by_xpath("//table/tbody/tr/td/div/span/div/a").get_attribute("href")  # noqa: E501
            print("Trying next page...")
            driver.get(gallery_set)
        except TimeoutException:
            print("Timeout Session Occurred ~ Retrying")
        except NoSuchElementException:
            print("reached end of set")
            phset = True
            print("Downing scraped photos")
            with open(image_file) as rfile:
                for line in rfile:
                    driver.get(line)
                    print("Getting  " + line)
                    get_fullphoto()
                else:
                    if os.path.exists(image_file):
                        print("Cleaning...")
                        os.remove(image_file)
                    else:
                        print("The file does not exist")
        except ErrorInResponseException:
            traceback.print_exception


############################################################################
#   ___  _ _                       _____       _ _           _             #
#  / _ \| | |                     /  __ \     | | |         | |            #
# / /_\ \ | |__  _   _ _ __ ___   | /  \/ ___ | | | ___  ___| |_ ___  _ __ #
# |  _  | | '_ \| | | | '_ ` _ \  | |    / _ \| | |/ _ \/ __| __/ _ \| '__|#
# | | | | | |_) | |_| | | | | | | | \__/\ (_) | | |  __/ (__| || (_) | |   #
# \_| |_/_|_.__/ \__,_|_| |_| |_|  \____/\___/|_|_|\___|\___|\__\___/|_|   #
#                                                                          #
############################################################################

@retry(retry_on_exception=retry_on_timeout, stop_max_attempt_number=7)
@retry(retry_on_exception=retry_on_NoSuchElement, stop_max_attempt_number=3)
@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def album_collector(photo_albums_links):
    alurl_num = str(randint(1, 9999))
    alurl_file = "/tmp/album_url" + alurl_num + ".txt"
    for b in photo_albums_links:
        album_link = b.get_attribute("href")
        print("Opening  " + album_link)
        k = open(alurl_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
        k.writelines(album_link)
        k.write("\n")
        k.close()
    with open(alurl_file) as kfile:
        for line in kfile:
            driver.get(line)
            print("Opening album  " + line)
            album_walker()

################################################################
#       _   _ _                __      __    _ _               #
#      /_\ | | |__ _  _ _ __   \ \    / /_ _| | |_____ _ _     #
#     / _ \| | '_ \ || | '  \   \ \/\/ / _` | | / / -_) '_|    #
#    /_/ \_\_|_.__/\_,_|_|_|_|   \_/\_/\__,_|_|_\_\___|_|      #
#                                                              #
################################################################


@retry(retry_on_exception=retry_on_timeout, stop_max_attempt_number=7)
@retry(retry_on_exception=retry_on_NoSuchElement, stop_max_attempt_number=3)
# @limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def album_walker():
    print("Walking the album")
    album_number = str(randint(1, 9999))
    album_file = "/tmp/album_image_url" + album_number + ".txt"
    alset = False
    while alset is False:
        album_photos_links = driver.find_elements_by_xpath("//article/div/section/div/a")  # noqa: E501
        print("Writing Image links...")
        for s in album_photos_links:
            album_image_link = s.get_attribute("href")
            v = open(album_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
            v.writelines(album_image_link)
            v.write("\n")
            v.close()
        try:
            album_nextpage = driver.find_element_by_xpath("//article/div/div/div/a").get_attribute("href")  # noqa: E501
            driver.get(album_nextpage)
            print("Trying next page in album...")
        except NoSuchElementException:
            print("Downing scraped photos")
            with open(album_file) as ai_file:
                for line in ai_file:
                    driver.get(line)
                    print("Getting  " + line)
                    get_fullphoto()
                else:
                    alset = True
    if alset is True:
        print("Cleaning...")
        if os.path.exists(album_file):
            os.remove(album_file)
        else:
            print("The file does not exist")


# --------------------------------------------------------
###############################################################
#              _      __      _ _        _        _           #
#     __ _ ___| |_   / _|_  _| | |  _ __| |_  ___| |_ ___     #
#    / _` / -_)  _| |  _| || | | | | '_ \ ' \/ _ \  _/ _ \    #
#    \__, \___|\__| |_|  \_,_|_|_| | .__/_||_\___/\__\___/    #
#    |___/                         |_|                        #
###############################################################
# ---------------------------------------------------------

@retry(retry_on_exception=retry_on_timeout, stop_max_attempt_number=5)
@retry(retry_on_exception=retry_on_NoSuchElement, stop_max_attempt_number=3)
# @limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def get_fullphoto():
    try:
        full_Size_Url = driver.find_element_by_xpath(
            "//a[text()='View Full Size']").get_attribute("href")
        driver.get(full_Size_Url)
        time.sleep(3)
        image_number = str(randint(1, 9999))
        image_name = "photo" + image_number + ".jpg"
        img_url = driver.current_url
        try:
            with requests.get(img_url, stream=True, allow_redirects=True) as r:  # noqa: E501
                with open(image_name, "wb") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        except TimeoutException:
            print("Timeout Occurred")
    except NoSuchElementException:
        print("No full size url element found")

# ****************************************************************************
# *                              Clean File Sets                             *
# ****************************************************************************

def clean_file_sets():
    if os.path.exists("/tmp/album_url.txt"):
        os.remove("/tmp/album_url.txt")
    elif os.path.exists("/tmp/image_url"+ '*' + ".txt"):
        os.remove("/tmp/image_url.txt")
    elif os.path.exists("/tmp/album_image_url.txt"):
        os.remove("/tmp/album_image_url.txt")
    else:
        print("Clean")


# ---------------------------------------------------------

# #### Identifying images notes:
# //article/div/div/div/a

# Script needs to do the following in order:
# 1. Locate the image link on the profile page or open it automatically
# 2. Walk through and return all images found
# 3. Locate and click on the "Next" button to get to the next page
# 4. repeat 2-3 until "next" button disappears.
# 5. Return the results.

# -------------------------------------------------------------

# -------------------------------------------------------------

##########################################################################################  # noqa: E501
#      ____      _                      __ _ _        ____  _           _                #  # noqa: E501
#     / ___| ___| |_   _ __  _ __ ___  / _(_) | ___  |  _ \| |__   ___ | |_ ___  ___     #  # noqa: E501
#    | |  _ / _ \ __| | '_ \| '__/ _ \| |_| | |/ _ \ | |_) | '_ \ / _ \| __/ _ \/ __|    #  # noqa: E501
#    | |_| |  __/ |_  | |_) | | | (_) |  _| | |  __/ |  __/| | | | (_) | || (_) \__ \    #  # noqa: E501
#     \____|\___|\__| | .__/|_|  \___/|_| |_|_|\___| |_|   |_| |_|\___/ \__\___/|___/    #  # noqa: E501
#                     |_|                                                                #  # noqa: E501
##########################################################################################  # noqa: E501

# --------------------------------------------------------------
# DONE: prevent infinite loop of scraping photos.

@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
@retry(retry_on_exception=retry_on_timeout, stop_max_attempt_number=7)
@retry(retry_on_exception=retry_on_NoSuchElement, stop_max_attempt_number=3)
def get_profile_photos(userid_profile_link):
    driver.get(userid_profile_link)
    url = driver.current_url
    userid_profile_link = create_original_link(url)
    render_phrase = 'Scraping photos =  ' + str(userid_profile_link)
    print(render_phrase)
    try:
        photos_url = driver.find_element_by_xpath("//a[text()='Photos']").get_attribute("href")  # noqa: E501
    except NoSuchElementException:
        try:
            profile_link = driver.find_element_by_xpath(
                "//div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/a[1]").get_attribute("href")
            driver.get(profile_link)
            photos_url = driver.find_element_by_xpath(
                "//a[text()='Photos']").get_attribute("href")
        except NoSuchElementException:
            print("No Photo Element Found")
    try:
        driver.get(photos_url)
        pp_element = "//div/section/ul/li/table/tbody/tr/td/span/a"
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, pp_element)))
        albums_on_pp = driver.find_elements_by_xpath(pp_element)
        if albums_on_pp and albums_on_pp[0].is_displayed():
            print("Albums on Photo page")
            internal_albums = True
        else:
            print("Albums not found on photos page")
            internal_albums = False
        pvoid_link = driver.find_element_by_xpath("//div[1]/section/a[text()='See All']").get_attribute("href")  # noqa: E501
        wait.until(EC.visibility_of_all_elements_located(
            (By.XPATH, "//section/a[text()='See All']")))
        photos_view = driver.find_elements_by_xpath("//section/a[text()='See All']")
        for j in photos_view:
            try:
                pv_link = j.get_attribute("href")
                driver.get(pv_link)
                gallery_walker()
            except NoSuchElementException:
                print("Got a funky Reference There")
                continue
        # Move to albums
        print("Working on albums now")
        if internal_albums is True:
            try:
                driver.get(photos_url)
                see_all_albums = driver.find_element_by_xpath(
                    "//div[2]/div/div[2]/div[3]/section[2]/a")
                albums_link = see_all_albums.get_attribute("href")
                driver.get(albums_link)
                photo_albums_links = driver.find_elements_by_xpath(
                    "//li/table/tbody/tr/td/span/a")
                album_collector(photo_albums_links)
            except NoSuchElementException:
                print("'See More Albums' element not found. Scraping directly from photos url:")
                pial = "//div[2]/div/div[2]/div[2]/section/ul/li/table/tbody/tr/td/span/a"
                photo_albums_links = driver.find_elements_by_xpath(pial)
                album_collector(photo_albums_links)
            except StaleElementReferenceException:
                print("Found a stale element in album links")
        else:
            print("Generating albums page...")
            f1 = furl(pvoid_link)
            int_fb_id = f1.args.popvalue('owner_id')
            account_id = int_fb_id.strip()
            f2 = furl(userid_profile_link)
            userid = f2.pathstr.strip("/")
            back_album_url = "albums/?owner_id="
            album_page_url = facebook_https_prefix + facebook_link_body + userid + "/" + back_album_url + account_id  # noqa: E501
            print(album_page_url)
            driver.get(album_page_url)
            try:
                no_album_page = driver.find_element_by_xpath("//span[text()='The page you requested was not found.']")
                if no_album_page and no_album_page.is_displayed():
                    print("Album page not found")
            except NoSuchElementException:
                try:
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//span/a")))  # noqa: E501
                    photo_albums_links = driver.find_elements_by_xpath("//span/a")  # noqa: E501
                    album_collector(photo_albums_links)
                except NoSuchElementException:
                    print("No more albums found")
                    clean_file_sets()
    except TimeoutException:
        print("Photo page timed out")
        e = open("error_log.txt", "a", newline="\n")
        e.writelines("Timeout error occurred while scrpaing " + userid_profile_link)
        e.write("\n")
        e.close()
    except StaleElementReferenceException:
        print("Found a reference to a stale Element in photo scrape (general error)")
    except NoSuchElementException:
        print("Fuck!! No Photos Found!")
        print(traceback.format_exc())
        clean_file_sets()
    


# ****************************************************************************
# *                               Friend Walker                              *
# ****************************************************************************


def friend_walker():
    fi_url = driver.current_url
    ff = furl(fi_url)
    f_id = ff.pathstr.strip("/friends")
    friend_list = driver.find_elements_by_xpath("//div[2]/div/div/div[2]/div/table/tbody/tr/td[2]/a")  # noqa: E501
    for x in friend_list:
        friend_url = x.get_attribute("href")
        friend_name = x.text
        friend_file = f_id + "-" + "friends" + ".txt"
        u = open(friend_file, "a", encoding="utf-8", newline="\n")
        u.writelines(friend_name)
        u.write("\t")
        u.writelines(friend_url)
        u.write("\n")
        u.close()
        friend_url_file = "friend_urls.txt"
        k = open(friend_url_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
        k.writelines(friend_url)
        k.write("\n")
        k.close()


# ------------------------------------------------------
#  _____      _    ______    _                _
# |  __ \    | |   |  ___|  (_)              | |
# | |  \/ ___| |_  | |_ _ __ _  ___ _ __   __| |___
# | | __ / _ \ __| |  _| '__| |/ _ \ '_ \ / _` / __|
# | |_\ \  __/ |_  | | | |  | |  __/ | | | (_| \__ \
#  \____/\___|\__| \_| |_|  |_|\___|_| |_|\__,_|___/
# -------------------------------------------------------

# -------------------------------------------------------------
# ****************************************************************************
# *                                Get Friends                               *
# ****************************************************************************
# -------------------------------------------------------------
# DONE: create a variable that is userid_profile_link and friends_id combined for images
# DONE: Add a loop with a limitation of redundancy

@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
@retry(retry_on_exception=retry_on_timeout, stop_max_attempt_number=5)
def get_friends(userid_profile_link):
    driver.get(userid_profile_link)
    url = driver.current_url
    userid_profile_link = create_original_link(url)
    print("Getting friends of " + userid_profile_link)
    try:
        friend_page = driver.find_element_by_xpath("//div[2]/div/div/div/div[4]/a[2]").get_attribute("href")  # noqa: E501
    except NoSuchElementException:
        url = driver.find_element_by_xpath(
            "//div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/a[1]").get_attribute("href")
        profile_link = create_original_link(url)
        driver.get(profile_link)
        friend_page = driver.find_element_by_xpath("//div[2]/div/div/div/div[4]/a[2]").get_attribute("href")  # noqa: E501
    try:
        driver.get(friend_page)
        print("Getting " + friend_page)
        scroll()
        time.sleep(5)
        friend_walker()
        friend_list_end = False
        while friend_list_end is False:
            try: 
                more_friends = driver.find_element_by_xpath(
                    '//div[2]/div/div[1]/div[3]/a').get_attribute("href")
                driver.get(more_friends)
                scroll()
                time.sleep(3)
                friend_walker()
            except NoSuchElementException:
                try:
                    more_friends_again = driver.find_element_by_xpath(
                        '//div[2]/div/div[1]/div[2]/a').get_attribute("href")
                    driver.get(more_friends_again)
                    scroll()
                    time.sleep(3)
                    friend_walker()
                except NoSuchElementException:
                    scroll()
                    time.sleep(3)
                    friend_walker()
                    time.sleep(5)
                    print("Friend Scraping: Completed!")
                    friend_list_end = True
    except NoSuchElementException:
        print("Did not find any friends")
        friend_list_end = True
        print(traceback.format_exc())
    except TimeoutException:
        print("A Timeout has occurred, we will retry again.")


# ---------------------------------------------------------------------------------
# ______ _               _                     _____ _               _
# |  _  (_)             | |                   /  __ \ |             | |
# | | | |_ _ __ ___  ___| |_ ___  _ __ _   _  | /  \/ |__   ___  ___| | _____ _ __
# | | | | | '__/ _ \/ __| __/ _ \| '__| | | | | |   | '_ \ / _ \/ __| |/ / _ \ '__|
# | |/ /| | | |  __/ (__| || (_) | |  | |_| | | \__/\ | | |  __/ (__|   <  __/ |
# |___/ |_|_|  \___|\___|\__\___/|_|   \__, |  \____/_| |_|\___|\___|_|\_\___|_|
#                                       __/ |
#                                      |___/
# ----------------------------------------------------------------------------------

# def dir_check():
#     p = PurePath(os.cwd())
    
    

# ------------------------------------------------------------------------
#    ____                _             ____
#   / ___| ___ _ __   __| | ___ _ __  / ___|  ___ _ __ __ _ _ __   ___ _ __
#  | |  _ / _ \ '_ \ / _` |/ _ \ '__| \___ \ / __| '__/ _` | '_ \ / _ \ '__|
#  | |_| |  __/ | | | (_| |  __/ |     ___) | (__| | | (_| | |_) |  __/ |
#   \____|\___|_| |_|\__,_|\___|_|    |____/ \___|_|  \__,_| .__/ \___|_|
#                                                          |_|
# -------------------------------------------------------------------------

# ****************************************************************************
# *                                Get Gender                                *
# ****************************************************************************

@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def friend_gender_scraper(ids):
    for userid_profile_link in ids:
        fdud = furl(userid_profile_link)
        dud = fdud.pathstr
        print("Bad id reference: " + dud)
        fuid = dud.strip("%0A")
        print("Good id reference: " + fuid)
        time.sleep(2)
        print("Profile is: " + fuid)
        fgCWD = os.getcwd()
        fupath = fgCWD + fuid
        if os.path.exists(fgCWD + fuid + "/" + "friend_urls.txt") is True:
            print("Desired path exists")
            os.chdir(fupath)
            with open("friend_urls.txt") as ofile:
                for line in ofile:
                    url = line
                    friend_url = create_original_link(url)
                    driver.get(friend_url)
                    print('Scraping Gender' + str(friend_url))
                    if desired_gender == "Female":
                        try:
                            sheila = driver.find_element_by_xpath(
                                "//div[text()='Female']")
                            if sheila and sheila.is_displayed():
                                friend_scrape_file = "friends_to_scrape.txt"
                                b = open(friend_scrape_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
                                b.writelines(friend_url)
                                b.write("\n")
                                b.close()
                        except NoSuchElementException:
                            continue
                    elif desired_gender == "Male":
                        try:
                            bruce = driver.find_element_by_xpath(
                                "//div[text()='Male']")
                            if bruce and bruce.is_displayed():
                                friend_scrape_file = "friends_to_scrape.txt"
                                b = open(friend_scrape_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
                                b.writelines(friend_url)
                                b.write("\n")
                                b.close()
                        except NoSuchElementException:
                            continue
                    elif desired_gender == "All":
                        friend_scrape_file = "friends_to_scrape.txt"
                        b = open(friend_scrape_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
                        b.writelines(friend_url)
                        b.write("\n")
                        b.close()
                    else:
                        print("Unable to determine desired gender")
                        print(traceback.format_exc())
                    # Now Scrape Results
                    print("Scraping Friends of gender: " + desired_gender)
                    with open("friends_to_scrape.txt") as fts:
                        for userid_profile_link in fts:
                            frud = furl(userid_profile_link)
                            frud_id = frud.pathstr
                            friend_id = frud_id.strip("%0A")
                            CWD = os.getcwd()
                            folder = CWD + friend_id
                            if os.path.exists(folder):
                                print("Folder already exists")
                                continue
                            else:
                                print("Folder to be created: " + folder)
                                time.sleep(3)
                                create_folder(folder)
                                os.chdir(folder)
                                # Perform the secondary scrape
                                print("Now performing scraping of second level...")
                                print("Scraping  " + userid_profile_link)
                                time.sleep(2)
                                get_profile_photos(userid_profile_link)
                                get_friends(userid_profile_link)
        else:
            print("Friend url list does not exist in directory: " + fgCWD + fuid)


# ## Page Scrolls

# In[117]:


# -------------------------------------------------------------

################################################################
#     ____                    ____                 _ _         #
#    |  _ \ __ _  __ _  ___  / ___|  ___ _ __ ___ | | |___     #
#    | |_) / _` |/ _` |/ _ \ \___ \ / __| '__/ _ \| | / __|    #
#    |  __/ (_| | (_| |  __/  ___) | (__| | | (_) | | \__ \    #
#    |_|   \__,_|\__, |\___| |____/ \___|_|  \___/|_|_|___/    #
#                |___/                                         #
################################################################

# -------------------------------------------------------------

# get page height.

def check_height():
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height

# -------------------------------------------------------------

# helper function: used to scroll the page


def scroll():
    global old_height
    current_scrolls = 0

    while True:
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script(
                "return document.body.scrollHeight")
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(
                lambda driver: check_height()
            )
            current_scrolls += 1
        except TimeoutException:
            break

    return



# ## Defining the scraping process

# -----------------------------------------------------------------------------
#####################################################
#      ___       _           _     _       _        #
#     / _ \ _ __(_) __ _    | |   (_)_ __ | | __    #
#    | | | | '__| |/ _` |   | |   | | '_ \| |/ /    #
#    | |_| | |  | | (_| |_  | |___| | | | |   <     #
#     \___/|_|  |_|\__, (_) |_____|_|_| |_|_|\_\    #
#                  |___/                            #
#####################################################
# -----------------------------------------------------------------------------
# DONE:


def create_original_link(url):
    if url.find(".php") != -1:
        original_link = (
            facebook_https_prefix + facebook_link_body + ((url.split("="))[1])
        )

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + ((url.split("/"))[-1].split("?")[0])
        )
    elif url.find("_tab") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + (url.split("?")[0]).split("/")[-1]
        )
    else:
        original_link = url

    return original_link


# ## Read and Run

# In[ ]:


# -----------------------------------------------------------------------------

#  ___             _   ___                _     __       ___
# | _ \___ __ _ __| | |_ _|_ _  _ __ _  _| |_  / _|___  | _ \_  _ _ _
# |   / -_) _` / _` |  | || ' \| '_ \ || |  _| > _|_ _| |   / || | ' \
# |_|_\___\__,_\__,_| |___|_||_| .__/\_,_|\__| \_____|  |_|_\\_,_|_||_|
#                              |_|

# -----------------------------------------------------------------------------
def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


# In[ ]:


##########################################################################
#     ___                          _   _         _        _    _ _       #
#    / __| __ _ _ __ _ _ __  ___  | |_| |_  __ _| |_   __| |_ (_) |_     #
#    \__ \/ _| '_/ _` | '_ \/ -_) |  _| ' \/ _` |  _| (_-< ' \| |  _|    #
#    |___/\__|_| \__,_| .__/\___|  \__|_||_\__,_|\__| /__/_||_|_|\__|    #
#                     |_|                                                #
##########################################################################


# ****************************************************************************
# *                       Start scraping profiles Here                       *
# ****************************************************************************

# ****************************************************************************
# *                               Main function                              *
# ****************************************************************************


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "data")
    create_folder(folder)
    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for userid_profile_link in ids:

        time.sleep(randint(tsmin, tsmax))
        driver.get(userid_profile_link)
        url = driver.current_url
        userid_profile_link = create_original_link(url)
        print(url)
        print("\nScraping:", userid_profile_link)

        try:
            target_dir = os.path.join(folder, userid_profile_link.split("/")[-1])
            create_folder(target_dir)
            os.chdir(target_dir)
        except Exception:
            print("Some error occurred in creating the profile directory.")
            continue

        ccwd = os.getcwd()
        print("Current Working Directory at the beginning of scrape is: " + ccwd)
        
        # This defines what gets scraped
        # -------------------------------
        clean_file_sets()
        get_profile_photos(userid_profile_link)
        get_friends(userid_profile_link)
        os.chdir("../")
    # The get gender relevant friends
    friend_gender_scraper(ids)

    print("\nProcess Completed.")
    os.chdir("../..")
    return


# ## Login

# In[ ]:


# -----------------------------------------------------------------------------

############################################################
#     _                      _               ___           #
#    | |    ___   __ _  __ _(_)_ __   __ _  |_ _|_ __      #
#    | |   / _ \ / _` |/ _` | | '_ \ / _` |  | || '_ \     #
#    | |__| (_) | (_| | (_| | | | | | (_| |  | || | | |    #
#    |_____\___/ \__, |\__, |_|_| |_|\__, | |___|_| |_|    #
#                |___/ |___/         |___/                 #
############################################################

# -----------------------------------------------------------------------------


def safe_find_element_by_id(driver, elem_id):
    try:
        return driver.find_element_by_id(elem_id)
    except NoSuchElementException:
        return None


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def login(email, password):
    """ Logging into our own profile """

    try:
        global driver

        try:
            platform_ = platform.system().lower()

        except Exception:
            print(
                "Kindly replace the Firefox Web Driver with the latest one from "  # noqa: E501
                "http://geckodriver.chromium.org/downloads "
                "and also make sure you have the latest Firefox Browser version."  # noqa: E501
                "\nYour OS: {}".format(platform_)
            )
            exit(1)

        fb_path = facebook_https_prefix + facebook_link_body
        driver.get(fb_path)
        driver.maximize_window()

        # filling the form
        driver.find_element_by_name("email").send_keys(email)
        driver.find_element_by_name("pass").send_keys(password)

        # Facebook new design
        driver.find_element_by_xpath("//input[@value='Log In']").click()
        WebDriverWait(driver, 7)
        driver.find_element_by_xpath("//body[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[3]/a[1]").click()  # noqa: E501

    except Exception:
        print("There is something wrong with logging in.")
        print(sys.exc_info()[0])
        exit(0)


# ## CLI Errors

# In[ ]:


# -----------------------------------------------------------------------------
'''
######  ##       ####
##    ## ##        ##
##       ##        ##
##       ##        ##
##       ##        ##
##    ## ##        ##
######  ######## ####

######## ########  ########   #######  ########
##       ##     ## ##     ## ##     ## ##     ##
##       ##     ## ##     ## ##     ## ##     ##
######   ########  ########  ##     ## ########
##       ##   ##   ##   ##   ##     ## ##   ##
##       ##    ##  ##    ##  ##     ## ##    ##
######## ##     ## ##     ##  #######  ##     ##
'''
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scraper(**kwargs):
    with open("credentials.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(stream=ymlfile)

    if ("password" not in cfg) or ("email" not in cfg):
        print(
            "Your email or password is missing. Kindly write them in credentials.txt"  # noqa: E501
        )
        exit(1)

    global ids
    ids = [
        facebook_https_prefix + facebook_link_body + line.split("/")[-1]
        for line in open("input.txt", newline="\n")
    ]

    if len(ids) > 0:
        print("\nStarting Scraping...")

        login(cfg["email"], cfg["password"])
        scrap_profile(ids)
        # driver.close() # -> Suspect of creating two browser windows
    else:
        print("Input file is empty.")


# -------------------------------------------------------------

#####################################################
#      ____ _     ___   _   _ _____ _     ____      #
#     / ___| |   |_ _| | | | | ____| |   |  _ \     #
#    | |   | |    | |  | |_| |  _| | |   | |_) |    #
#    | |___| |___ | |  |  _  | |___| |___|  __/     #
#     \____|_____|___| |_| |_|_____|_____|_|        #
#                                                   #
#####################################################

# -------------------------------------------------------------
# Does not work any longer | will remove in the future
# -------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    # PLS CHECK IF HELP CAN BE BETTER / LESS AMBIGUOUS
    ap.add_argument(
        "-dup",
        "--uploaded_photos",
        help="download users' uploaded photos?",
        default=True,
    )
    ap.add_argument(
        "-dfp", "--friends_photos",
        help="download users' photos?", default=True
    )
    ap.add_argument(
        "-fss",
        "--friends_small_size",
        help="Download friends pictures in small size?",
        default=True,
    )
    ap.add_argument(
        "-pss",
        "--photos_small_size",
        help="Download photos in small size?",
        default=True,
    )
    ap.add_argument(
        "-ts",
        "--total_scrolls",
        help="How many times should I scroll down?",
        default=2500,
    )
    ap.add_argument(
        "-st", "--scroll_time",
        help="How much time should I take to scroll?", default=8
    )
    ap.add_argument(
        "-cln",
        "--clean",
        help="Clean scraper files",
        default=True,
    )

    args = vars(ap.parse_args())
    print(args)


# ## More Global Variables

# In[ ]:


# ---------------------------------------------------------

######################################################
#      ____ _       _           _                    #
#     / ___| | ___ | |__   __ _| |                   #
#    | |  _| |/ _ \| '_ \ / _` | |                   #
#    | |_| | | (_) | |_) | (_| | |                   #
#     \____|_|\___/|_.__/ \__,_|_|                   #
#                                                    #
#    __     __         _       _     _               #
#    \ \   / /_ _ _ __(_) __ _| |__ | | ___  ___     #
#     \ \ / / _` | '__| |/ _` | '_ \| |/ _ \/ __|    #
#      \ V / (_| | |  | | (_| | |_) | |  __/\__ \    #
#       \_/ \__,_|_|  |_|\__,_|_.__/|_|\___||___/    #
#                                                    #
######################################################

# ---------------------------------------------------------

# whether to download photos or not
download_uploaded_photos = to_bool(args["uploaded_photos"])
download_friends_photos = to_bool(args["friends_photos"])

total_scrolls = int(args["total_scrolls"])
scroll_time = int(args["scroll_time"])

current_scrolls = 0
old_height = 0

# ## RUN!

# In[ ]:


# ****************************************************************************
# *                                    RUN                                   *
# ****************************************************************************

# get things rolling
if __name__ == "__main__":
    scraper()
