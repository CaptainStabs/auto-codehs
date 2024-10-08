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
from bs4 import BeautifulSoup
import pyperclip as pc
from _configs import url, configs

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

    def get_answer(self, can_copy_paste):
        # print("Is exercise: " + str(self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[1]/h2/text()')))
        solution_url = self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[2]/div/iframe').get_attribute("src")
        file_list = self.driver.find_element_by_xpath('//*[@id="panels"]/div[1]/div[4]/div/div/ul')
        file_objects = file_list.find_elements_by_tag_name("li")
        # print("file_objects: " + str(file_objects))
        # print("file_objects: " + str(len(file_objects.text)))

        try:
            self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[1]/div[2]/button').click()

        except exceptions.ElementNotInteractableException:
            logging.error("ElementNotInteractableException for assignment modal")

        for i, file in enumerate(file_objects):
            # i is list index, file is file
            # html indexes start at 1, so we need to start on 1 as well
            i += 1
            logging.info("Getting answers...")
            parsed_url = parse.urlparse(solution_url)

            url_path = str(parsed_url[2]).split('/')

            new_path = "/".join(parsed_url[2].split('/')[:-1]) + f"/{file.text}"
            # print(new_path)

            solution_url = "https://" + str('/'.join(parsed_url[1:2])) + new_path

            if "html" not in file.text:
                answer = requests.request("GET", solution_url).text
                print(answer)

            else:
                # To get the
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(solution_url)
                answer = self.driver.page_source
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

                # Clean the answer removing the items in list
                # (Answer is marked as incorrect if there is a noscript or script in it)
                soup = BeautifulSoup(answer, 'html.parser')

                # For non-bootstrap unit
                '''
                for data in soup(["noscript", "script", "grammarly-desktop-integration"]):
                    data.decompose()

                '''

                # For bootstrap unit
                for data in soup(["noscript", "grammarly-desktop-integration"]):
                    data.decompose()

                answer = str(soup)
                # print("Answer: " + str(answer))

            logging.info("Got answer... selecting file...")
            try:
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="panels"]/div[1]/div[4]/div/div/ul/li[{i}]')))

            except exceptions.TimeoutException:
                logging.error("Timeout waiting for first file to be clickable")
            try:
                self.driver.find_element_by_xpath(f'//*[@id="panels"]/div[1]/div[4]/div/div/ul/li[{i}]').click()

            except exceptions.ElementNotInteractableException:
                logging.error("ElementNotInteractableException on file")
            except exceptions.ElementClickInterceptedException:
                logging.error("ElementClickInterceptedException on file. Is probably nothing to worry about")

            logging.info("Typing answer")
            times_looped = 0

            while times_looped < 70:
                try:
                    answer_box = self.driver.find_element_by_xpath('//*[@id="ace-editor"]/textarea')
                    # Using .clear method was not reliable enough
                    # Clear the answer box before typing answer
                    answer_box.send_keys(Keys.CONTROL + "a")
                    answer_box.send_keys(Keys.DELETE)

                    if can_copy_paste:
                        # Pasting from clipboard is faster
                        pc.copy(answer)
                        answer_box.send_keys(Keys.CONTROL + "v")

                    else:
                        answer_box.send_keys(answer)

                    times_looped = 101

                except exceptions.ElementNotInteractableException:
                    times_looped += 1

                except exceptions.StaleElementReferenceException:
                    # Exception caused by assignment being finished
                    logging.exception("StaleElementReferenceException on answer box")
                    times_looped = 101

    def scrape(self, url, configs):
        # Probably unpythonic, but w/e
        student_number = configs["student_number"]
        section_number = configs["section_number"]
        assignment_number = configs["assignment_number"]
        end_number = configs["end_number"]
        can_copy_paste = configs["can_copy_paste"]

        actions = ActionChains(self.driver)

        self.driver.get(url)

        self.login(configs["sign_in_with_google"])

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

            # This convoluted code will need to be untangled, it's ugly.
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
                    # This is the module overview page.
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

                    # Click on CodeHS video provider
                    self.driver.find_element_by_xpath('//*[@id="video-types"]/button[1]').click()

                    WebDriverWait(self.driver, 900).until(EC.presence_of_element_located((By.XPATH, '//*[@id="codehsvideo_html5_api"]')))

                    while not post_video_screen.is_displayed():
                        try:
                            self.driver.execute_script('document.getElementsByTagName("video")[0].currentTime += 30;')
                            # logging.info("Skipping 30 seconds")

                        except Exception as E:
                            logging.error(E)

                    # Sets the display="none" to blank to force screen to show
                    # thus making it interactable
                    # self.driver.execute_script("arguments[0].style.display = '';", post_video_screen)

                    WebDriverWait(self.driver, 9000).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="done-button"]')))
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
                            while times_looped < 50:
                                try:
                                    next_button = self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/button[1]').click()
                                    time.sleep(0.5)
                                    # Fewer variables if I just pretend
                                    # that 101 = True for found
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    times_looped = 51

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
                        if "Example" in self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div/div/h2').text:
                            logging.info("Is Example (Second Type)")
                            times_looped = 0
                            while times_looped < 50:
                                try:
                                    example_modal_button = self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div/div/button')
                                    self.driver.execute_script("arguments[0].click();", example_modal_button)

                                    next_button = self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/button[1]').click()
                                    self.driver.execute_script("arguments[0].click();", next_button)

                                    times_looped = 51

                                except exceptions.StaleElementReferenceException:
                                    print("StaleElementReferenceException example button")
                                    times_looped += 1

                                except exceptions.JavascriptException:
                                    logging.info("JavascriptException example button")
                                    times_looped += 1

                                except exceptions.ElementClickInterceptedException:
                                    break

                            type_found = True
                    except exceptions.NoSuchElementException:
                        logging.info("Example header not found")
                        pass


                if not type_found:
                    # try:
                    if "Exercise" in self.driver.page_source:
                        if not type_found:
                            try:
                                self.get_answer(can_copy_paste)
                                frq = False

                            except exceptions.NoSuchElementException:
                                logging.error("NoSuchElementException on get_answer")
                                frq = True

                        if not frq:
                            try:
                                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="panels"]/div[3]/div/div[1]/button[1]')))
                            except exceptions.TimeoutException:
                                pass

                            tries = 0
                            while tries < 30:
                                try:
                                    submit_continue_btn = self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/button[1]')
                                    self.driver.execute_script("arguments[0].click();", submit_continue_btn)
                                    time.sleep(0.5)
                                    tries = 91

                                except exceptions.ElementNotInteractableException:
                                    logging.error("ElementNotInteractableException on submit button")
                                    tries += 1
                                except exceptions.JavascriptException:
                                    logging.error("JavascriptException on submit button")
                                    tries += 1
                                except exceptions.NoSuchElementException:
                                    logging.error("NoSuchElement on submit button")
                                    tries += 1

                            tries = 0
                            while tries < 30:
                                try:
                                    submit_correct_button = self.driver.find_element_by_xpath('//*[@id="submit-correct"]')
                                    self.driver.execute_script("arguments[0].click();", submit_correct_button)
                                    time.sleep(0.5)
                                    tries = 91

                                except exceptions.ElementNotInteractableException:
                                    logging.error("ElementNotInteractableException on submit correct button")
                                    tries += 1

                                except exceptions.JavascriptException:
                                    logging.error("JavascriptException, submit-correct")
                                    tries += 1

                                except exceptions.NoSuchElementException:
                                    logging.error("NoSuchElementException, submit correct")
                                    tries += 1
                            tries = 0
                            while tries < 30:
                                try:
                                    continue_anyways_btn = self.driver.find_element_by_xpath('//*[@id="continue-anyways-btn"]')
                                    self.driver.execute_script("arguments[0].click();", continue_anyways_btn)
                                    tries = 91

                                except exceptions.ElementNotInteractableException:
                                    logging.error("ElementNotInteractableException on continue anyways button")
                                    tries += 1

                                except exceptions.JavascriptException:
                                    logging.error("JavascriptException, continue anyways btn")
                                    tries += 1

                                except exceptions.NoSuchElementException:
                                    logging.error("NoSuchElementException on continue anyways button")
                                    tries += 1

                            time.sleep(2)

                            type_found = True

                        else:
                            logging.info("Is an FRQ assignment, skipping...")

                            try:
                                self.driver.find_element_by_xpath('//*[@id="directions-modal"]/div[1]/div[2]/button').click()

                            except exceptions.ElementNotInteractableException:
                                logging.error("ElementNotInteractableException for assignment modal")

                            except Exception as e:
                                logging.error(e)

                            tries = 0
                            while tries < 30:
                                try:
                                    submit_continue_btn = self.driver.find_element_by_xpath('//*[@id="submit-button"]')
                                    self.driver.execute_script("arguments[0].click();", submit_continue_btn)
                                    time.sleep(0.5)
                                    tries = 91

                                except exceptions.ElementNotInteractableException:
                                    logging.error("ElementNotInteractableException on submit button")
                                    tries += 1
                                except exceptions.JavascriptException:
                                    logging.error("JavascriptException on submit button")
                                    tries += 1
                                except exceptions.NoSuchElementException:
                                    logging.error("NoSuchElement on submit button")
                                    tries += 1

                                except exceptions.StaleElementReferenceException:
                                    logging.error("StaleElementReferenceException")
                                    tries += 1

                    # except exceptions.NoSuchElementException:
                    #     logging.error("No Exercise header element")
                    #     pass

                if not type_found:
                    try:
                        if "badge-description" in self.driver.page_source or "badge-details clearfix incomplete" in self.driver.page_source:
                            try:
                                self.driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/a').click()
                                time.sleep(0.5)
                            except exceptions.StaleElementReferenceException:
                                logging.error("StaleElementReferenceException on badge continue button")

                                type_found = True

                    except exceptions.NoSuchElementException:
                        logging.info("Is not a badge page")
                        pass

                if not type_found:
                    try:
                        if "Example Program" in self.driver.page_source:
                            try:
                                self.driver.find_element_by_xpath('//*[@id="panels"]/div[3]/div/div[1]/button[1]').click()
                                time.sleep(0.5)
                            except:
                                pass

                            type_found = True
                    except exceptions.NoSuchElementException:
                        logging.info("Is not an example page")

                if not type_found:
                    try:
                        self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[3]/a').click()
                        type_found = True
                        time.sleep(3)
                    except:
                        logging.info("Not lightbulb page thing")

                if not type_found:
                    try:
                        self.driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/a').click()
                    except:
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

    def login(self, use_google_auth):

        if use_google_auth:
            # Google login button
            self.driver.find_element_by_xpath('//*[@id="login-form"]/form/div[1]').click()




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

            logging.info("Typing Email")
            email_box.send_keys(email)
            email_box.send_keys(Keys.ENTER)

            # Check if there is a captcha, and if so, wait for user to fill it out
            # (Removes the pressure from the user to finish the captcha before loop finishes)
            if self.check_exists_by_xpath('//*[@id="captchaimg"]'):
                WebDriverWait(self.driver, 900).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))

            found = False
            times_looped = 0
            WebDriverWait(self.driver, 900).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))
            password_box = self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input')

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
                    worked = True
                    break

            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/form/div[1]')))

            except:
                pass

            try:
                self.driver.find_element_by_xpath('//*[@id="login-form"]/form/div[1]').click()
            except:
                pass

        else:
            self.driver.find_element_by_xpath('//*[@id="login-email"]').send_keys(email)
            self.driver.find_element_by_xpath('//*[@id="login-password"]').send_keys(password)
            self.driver.find_element_by_xpath('//*[@id="login-submit"]').click()

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except exceptions.NoSuchElementException:
            return False
        return True


if __name__ == '__main__':
    # url = "https://codehs.com/student/1758629/section/234939/"
    #
    # configs = {
    #     "student_number":"1758629",
    #     "section_number":"234939",
    #     "assignment_number":"50244601",
    #     "end_number":"50244518",
    #     "can_copy_paste": True,
    #     "sign_in_with_google": True,
    # }

    x = WebDriver()
    x.scrape(url, configs)
