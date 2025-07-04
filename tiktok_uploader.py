"""
tiktok_uploader.py
Automated TikTok video uploader using Selenium.
- Upload a video to TikTok
- Set caption
- Requires manual login for first use
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def upload_to_tiktok(video_path, caption):
    '''
    Upload a video to TikTok with a caption using Selenium automation.
    '''
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=selenium")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.tiktok.com/upload")
        time.sleep(10)
        upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
        upload_input.send_keys(video_path)
        time.sleep(10)
        caption_box = driver.find_element(By.XPATH, '//textarea')
        caption_box.clear()
        caption_box.send_keys(caption)
        time.sleep(2)
        post_button = driver.find_element(By.XPATH, '//button[contains(text(),"Post")]')
        post_button.click()
        time.sleep(10)
    except Exception as e:
        print(f"Error during TikTok upload: {e}")
    finally:
        driver.quit()
