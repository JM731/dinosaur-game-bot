from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
from PIL import ImageOps
import time
import datetime

left, top, width, height = 240, 720, 320, 80
last_change = False
THRESHOLD_PERCENT = 0.7


def rgb_to_grayscale(rgb_pixel):
    r, g, b = rgb_pixel
    grayscale_value = 0.299 * r + 0.587 * g + 0.114 * b
    return int(grayscale_value)


def interval_check(start, secs):
    return datetime.datetime.now() - start > datetime.timedelta(seconds=secs)


def change_width(curr_width, curr_time):
    global start_time

    now = datetime.datetime.now()
    stop = False
    if now - start_time <= datetime.timedelta(seconds=60):
        if now - curr_time >= datetime.timedelta(seconds=1):
            curr_width += 12
            curr_time = now
    else:
        if now - curr_time >= datetime.timedelta(seconds=15):
            curr_width += 17
            curr_time = now
        if now - start_time >= datetime.timedelta(seconds=165):
            stop = True

    return curr_width, curr_time, stop


# In this function, the image is converted to a binary black and white image by setting a threshold based on
# the current background intensity, where pixels above this threshold are considered as white (background)
# and below as black (obstacles). Finally, a boolean is returned; True if there is at least one black pixel,
# False if none. This is necessary during the day-night and night-day transitions, where the background color
# changes smoothly.
def is_obstacle_present(img, bg_intensity):
    threshold_value = int(bg_intensity * THRESHOLD_PERCENT)

    threshold_img = img.point(lambda pixel: 255 if pixel > threshold_value else 0)

    return any(pixel == 0 for pixel in threshold_img.getdata())


options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.maximize_window()

driver.get("https://elgoog.im/dinosaur-game/")

time.sleep(3)

pyautogui.press("space")

start_time = datetime.datetime.now()

time.sleep(3)

current_time = datetime.datetime.now()

while True:
    try:
        if not last_change:
            width, current_time, last_change = change_width(width, current_time)

        obstacle_region_img = pyautogui.screenshot(region=(left, top, width, height))

        grayscale_img = obstacle_region_img.convert('L')

        bg = rgb_to_grayscale(pyautogui.pixel(1572, 452))

        if bg < 130:

            grayscale_img = ImageOps.invert(grayscale_img)
            bg = 255 - bg

        if is_obstacle_present(grayscale_img, bg):

            pyautogui.press("space")

    except pyautogui.FailSafeException:
        driver.close()
        driver.quit()
        break
