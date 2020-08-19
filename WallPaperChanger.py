#!/usr/local/bin/python3

# Pull image from a list of random categories using Unsplash's API (you need an account/API key). Download the image and set it as a background.
# Next time the script runs, it will delete the previous image downloaded. Script can be run as
# cronjob (if you want your background to change X mins) or ran manually
from AppKit import NSWorkspace, NSScreen
from Foundation import NSURL
import requests
import json
import logging
from time import strftime
import os
import glob
import random

def wallpaper_change(image_path):
    picture_path = NSURL.fileURLWithPath_(image_path)
    options = {} # Required, leaving it empty for defaults

    workspace = NSWorkspace.sharedWorkspace() 
    screens = NSScreen.screens() # Get 

    for screen in screens:
        (result, error) = workspace.setDesktopImageURL_forScreen_options_error_(
                    picture_path, screen, options, None)

unsplash_url = "https://api.unsplash.com/"
unsplash_status = requests.get(unsplash_url)
time_stamp = strftime("%I%M%S_%m%d%y")

def image_download(image_content):
    for img_file in glob.glob("PATH_TO_REMOVE_SAVED_TEMP_IMAGE*"):
        os.remove(img_file)

    image_path = "PATH_TO_TEMP_SAVED_IMAGE" + time_stamp + ".jpg"
    with open(image_path, "wb") as img:
        img.write(image_content)
    wallpaper_change(image_path)

if (unsplash_status.status_code == 200):
    with open("PATH_TO_API_KEY_JSON") as api_file:
        client_id = (json.load(api_file))["client_id"]
        search_query_list = random.choice(["wallpaper", "city", "nature", "sky", "night"])
        unsplash_image = requests.get(unsplash_url + "search/photos?page=1&query=" + search_query_list, params={"client_id":client_id}).json()["results"][random.randrange(0,9)]["urls"]["raw"]
        image = requests.get(unsplash_image)
        image_download(image.content)
else:
    logging.basicConfig(filename="PATH_TO_SAVE_ERROR_LOGS" + time_stamp + ".log", format='%(asctime)s %(message)s', filemode="w")
    logger=logging.getLogger() 
    logger.error(unsplash_status.status_code)
    logger.error(unsplash_status.text)
    logger.error(unsplash_status.reason)