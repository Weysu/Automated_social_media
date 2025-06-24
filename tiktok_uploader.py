# youtube_to_tiktok_bot/tiktok_uploader.py
'''
Not Working for now
Need to implement youtube or tiktok
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def upload_to_tiktok(video_path, caption):
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=selenium")  # to preserve login session
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.tiktok.com/upload")
    time.sleep(10)  # wait for page and login manually if needed

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
    driver.quit()
