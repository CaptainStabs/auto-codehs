from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from selenium.common import exceptions
from _secrets import email, password, driver_path, binary_path
import requests
import logging
from urllib import parse
import time
import heartrate; heartrate.trace(browser=True, daemon=True)

class WebDriver:
    def __init__(self):
        self.PATH = driver_path
        self.options = Options()
        self.options.binary_location = binary_path
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        logging.basicConfig(level=logging.INFO)
        # self.options.add_argument("user-data-dir=C:\\Users\\lilli\\AppData\\Local\\Google\\Chrome\\User Data\\Default")

        # self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(self.PATH, options=self.options)
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        # self.location_data["location"] = "NA"
    def submit_answer(self, student_assignment_id):
        headers = {
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Cookie': '_ga=GA1.2.794132728.1634580125; _gcl_au=1.1.1689946055.1634580125; intercom-id-x13jbr4h=1ed2ef75-e889-42c5-8fda-b7959ec816c3; username=TheSFMgineer; uid=1429076; _gid=GA1.2.814236272.1636467944; csrftoken=aXsurNihSC9S6W9VRiYoiIMA8QmLGQbq;'
        }

        submit_api_url = "https://codehs.com/lms/ajax/submit_assignment"

        payload = f'method=submit_assignment&student_assignment_id={student_assignment_id}'
        submitted_answer = requests.request("POST", submit_api_url, data=payload)
        print("Submit API Response: {}".format(submitted_answer.status_code))

    def scrape(self, url):
        actions = ActionChains(self.driver)

        self.driver.get(url)

        login_chrome_button = self.driver.find_element_by_xpath('//*[@id="login-form"]/form/div[1]')
        print("Clicking")
        actions.click(login_chrome_button).perform()

        print("Looking for email box")
        found = False
        times_looped = 0

        while not found and times_looped < 10000:
            try:
                email_box = self.driver.find_element_by_xpath('//*[@id="identifierId"]')
                found = True

            except exceptions.NoSuchElementException:
                print("Couldn't find it!")
                found = False
                times_looped += 1
                print(times_looped)

            except exceptions.StaleElementReferenceException:
                print("Email button dumb error")
                times_looped += 1
                print(times_looped)
                found = False

        print("Typing Email")
        email_box.send_keys(email)
        email_box.send_keys(Keys.ENTER)
        found = False
        times_looped = 0
        while not found and times_looped < 1000:
            try:
                password_box = self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input')
                found = True

            except exceptions.NoSuchElementException:
                print("Couldn't find it!")
                found = False
                times_looped += 1
                print(times_looped)

        worked = False
        times_looped = 0
        while not worked or times_looped < 500:
            try:
                password_box.send_keys(password)
                password_box.send_keys(Keys.ENTER)
                worked = True
            except exceptions.ElementNotInteractableException:
                print("Not interactable BS")
                times_looped +=1
                print(times_looped)
                worked = False
            except exceptions.StaleElementReferenceException:
                print("Stale element error")
                break

        student_number = "1758629"
        section_number = "234939"
        assignment_number = "50244514"
        end_number = "50244630"

        finished = False
        print("Going to first assignment")
        # for assignment_number in range(50244505, 50244630):
        # print("starting loop")

        url = f"https://codehs.com/student/{student_number}/section/{section_number}/assignment/{assignment_number}/"
        self.driver.get(url)

        while not finished:
            try:
                self.driver.find_element_by_xpath('//*[@id="video-types"]')
                is_video_assignment = True
                print("Is video assignment")
            except exceptions.NoSuchElementException:
                is_video_assignment = False

            # student_assignment_id = self.driver.find_element_by_xpath(f'//*[@href="/student/{student_number}/section/{section_number}/assignment/{assignment_number}/"]')

            type_found = False

            try:
                if "Quiz" in self.driver.find_element_by_xpath('/html/body/div[4]/h1').text:
                    logging.info("Is quiz")
                    is_quiz = True
                    type_found = True
                else:
                    is_quiz = False
                    type_found = False
            except exceptions.NoSuchElementException:
                is_quiz = False

            if not is_quiz:
                try:
                    parsed_url = parse.urlparse(self.driver.current_url)

                    # This could be compressed down to one line
                    self.driver.find_element_by_xpath('//*[@id="library-main"]/div[2]/div/div/a[1]').click()
                    # url_path = str(parsed_url[2]).split('/')
                    # next_assignment_number = int(url_path[-2]) + 1
                    # print(next_assignment_number)
                    # new_path = "/".join(parsed_url[2].split('/')[:-2]) + f"/{next_assignment_number}"
                    # print(new_path)
                    #
                    #
                    # print("https://" + str('/'.join(parsed_url[1:2])) + new_path)
                    # self.driver.get("https://" + str('/'.join(parsed_url[1:2])) + new_path)
                    time.sleep(5)
                    type_found = True

                except exceptions.NoSuchElementException:
                    logging.error("NoSuchElementException, is not lesson page")

                except exceptions.StaleElementReferenceException:
                    logging.error("StaleElementReferenceException, probably not a lesson page")

                if is_video_assignment:
                    # self.submit_answer(student_assignment_id)

                    post_video_screen = self.driver.find_element_by_xpath('//*[@id="post-video-container"]')

                    # Sets the display="none" to blank to force screen to show
                    # thus making it interactable
                    self.driver.execute_script("arguments[0].style.display = '';", post_video_screen)

                    self.driver.find_element_by_xpath('//*[@id="done-button"]').click()
                    type_found = True

                if not type_found:
                    try:
                        if "Example" in self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/div[1]/span').text:
                            logging.info("Is Example")

                            # times_looped = 0
                            #
                            # while times_looped < 100:
                            #     try:
                            #         self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div/div/button')
                            #         times_looped = 101
                            #
                            #     except exceptions.StaleElementReferenceException:
                            #         logging.debug("StaleElementReferenceException on directions modal")
                            #         logging.info("StaleElementReferenceExceptiondfdasfadsf")
                            #         times_looped += 1

                            times_looped = 0
                            # Click next
                            while times_looped < 100:
                                try:
                                    next_button = self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/button[1]').click()
                                    # Fewer variables if I just pretend
                                    # that 101 = True for found
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    times_looped = 101

                                except exceptions.StaleElementReferenceException:
                                    print("StaleElementReferenceException")
                                    times_looped += 1

                                except exceptions.JavascriptException:
                                    logging.info("JavascriptException")
                                    times_looped += 1

                                except exceptions.ElementClickInterceptedException:
                                    break

                            type_found = True

                    except exceptions.NoSuchElementException:
                        logging.info("Example header not found")
                        pass
                if not type_found:
                    try:
                        if "Exercise" in self.driver.page_source:
                            # print("Is exercise: " + str(self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[1]/h2/text()')))
                            solution_url = self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[2]/div/iframe').get_attribute("src")

                            answer = requests.request("GET", solution_url)

                            try:
                                self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[1]/div[2]/button').click()

                            except exceptions.ElementNotInteractableException:
                                logging.error("ElementNotInteractableException for assignment modal")

                            answer_box = self.driver.find_element_by_xpath('//*[@id="ace-editor"]/textarea')
                            answer_box.clear()
                            answer_box.send_keys(answer.text)

                            try:
                                submit_continue_btn = self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/button[1]')
                                self.driver.execute_script("arguments[0].click();", submit_continue_btn)

                            except exceptions.ElementNotInteractableException:
                                logging.error("ElementNotInteractableException on submit button")
                            except exceptions.JavascriptException:
                                logging.error("JavascriptException on submit button")
                            except exceptions.NoSuchElementException:
                                logging.error("NoSuchElement on submit button")

                            try:
                                submit_correct_button = self.driver.find_element_by_xpath('//*[@id="submit-correct"]')
                                self.driver.execute_script("arguments[0].click();", submit_correct_button)

                            except exceptions.ElementNotInteractableException:
                                logging.error("ElementNotInteractableException on submit correct button")

                            except exceptions.JavascriptException:
                                logging.error("JavascriptException, submit-correct")

                            except exceptions.NoSuchElementException:
                                logging.error("NoSuchElementException, submit correct")

                            try:
                                continue_anyways_btn = self.driver.find_element_by_xpath('//*[@id="continue-anyways-btn"]')
                                self.driver.execute_script("arguments[0].click();", continue_anyways_btn)

                            except exceptions.ElementNotInteractableException:
                                logging.error("ElementNotInteractableException on continue anyways button")

                            except exceptions.JavascriptException:
                                logging.error("JavascriptException, continue anyways btn")

                            except exceptions.NoSuchElementException:
                                logging.error("NoSuchElementException on continue anyways button")

                            type_found = True

                    except exceptions.NoSuchElementException:
                        logging.error("No Exercise header element")
                        pass

            if is_quiz:
                # There is no next button on the quiz until you complete it,
                # so it just increments the assignment number instead
                parsed_url = parse.urlparse(self.driver.current_url)

                # This could be compressed down to one line
                url_path = str(parsed_url[2]).split('/')
                next_assignment_number = int(url_path[-2]) + 1
                print(next_assignment_number)
                new_path = "/".join(parsed_url[2].split('/')[:-2]) + f"/{next_assignment_number}"
                print(new_path)

                print("https://" + str('/'.join(parsed_url[1:2])) + new_path)
                self.driver.get("https://" + str('/'.join(parsed_url[1:2])) + new_path)
                type_found = True

            if end_number in self.driver.current_url:
                finished = True

            # print(self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/div[1]/span/text()'))

            # print("reached end of loop")
            # print(assignment_number)

url = "https://codehs.com/student/1758629/section/234939/"

x = WebDriver()
x.scrape(url)
