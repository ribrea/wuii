import time
from selenium import webdriver
from selenium.webdriver.common.by import By

CHROME_DRIVER = './chromedriver'
LOGIN_URL = 'https://www.instagram.com/accounts/login/'
PROFILE_URL = lambda x: f'https://www.instagram.com/{x}/'
FOLLOWERS_URL = lambda x: f'https://www.instagram.com/{x}/followers/'
POST_URL = lambda x: f"https://www.instagram.com/p/{x}/"


class wuii:
    def __init__(self, username, password, chrome_driver_path, cookie=None):
        self.username = username
        self.password = password
        self.cookie = cookie
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        self._followers = None
        self._followings = None

    def login(self):
        self._init_driver()

        self.driver.get(LOGIN_URL)

        self._accept_cookies()

        # LOGIN
        self.driver.find_element("name", "username").send_keys(self.username)
        self.driver.find_element("name", "password").send_keys(self.password)

        self.driver.find_element(By.XPATH, "//form[@id='loginForm']/div/div[3]/button").click()
        time.sleep(5)

        # SAVE COOKIE
        self.driver.find_element(By.CLASS_NAME, "y3zKF").click()
        time.sleep(5)
        self.cookie = self.driver.get_cookies()

        self._skip_notification()

        return self.cookie

    def profile(self):
        self._init_driver()

        self.driver.get(PROFILE_URL(self.username))

        self._add_cookies()
        self.driver.refresh()
        self.driver.get(PROFILE_URL(self.username))

        time.sleep(1000)

    def followers(self):
        self._init_driver()

        self.driver.get(FOLLOWERS_URL(self.username))

        self._add_cookies()
        self.driver.refresh()

        self.driver.find_element(By.XPATH,
                                 '//*[@id="react-root"]/div/div/section/main/div/header/section/ul/li[2]/a').click()
        time.sleep(3)

        scroll = self.driver.find_element(By.CSS_SELECTOR, '.isgrP')

        self._scroll_till_end(scroll)

        a = scroll.find_elements(By.TAG_NAME, 'a')

        self._followers = [x.get_attribute("title") for x in a if x.text != '']

        return self._followers

    def followings(self):
        self._init_driver()

        self.driver.get(FOLLOWERS_URL(self.username))

        self._add_cookies()
        self.driver.refresh()

        self.driver.find_element(By.XPATH,
                                 '//*[@id="react-root"]/div/div/section/main/div/header/section/ul/li[3]/a').click()
        time.sleep(3)

        scroll = self.driver.find_element(By.CSS_SELECTOR, '.isgrP')

        self._scroll_till_end(scroll)

        a = scroll.find_elements(By.TAG_NAME, 'a')

        self._followings = [x.get_attribute("title") for x in a if x.text != '']

        return self._followings

    def _init_driver(self):
        if not self.driver:
            self.driver = webdriver.Chrome(executable_path=self.chrome_driver_path)

    def _accept_cookies(self):
        self._init_driver()

        self.driver.find_element(By.CLASS_NAME, "bIiDR").click()
        time.sleep(5)

    def _skip_notification(self):
        self._init_driver()

        self.driver.find_element(By.CLASS_NAME, "HoLwm").click()
        self.driver.close()

    def _add_cookies(self):
        self._init_driver()

        if self.cookie is None:
            self.login()

        return [self.driver.add_cookie(cookie_dict=x) for x in self.cookie]

    def _scroll_till_end(self, box):
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            time.sleep(2)
            ht = self.driver.execute_script(""" 
                   arguments[0].scrollTo(0, arguments[0].scrollHeight);
                   return arguments[0].scrollHeight; """, box)

    def _scroll_till_end_page(self):
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            time.sleep(2)
            ht = self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight); return '
                                            'document.body.scrollHeight;')

    def dont_follow_you(self):
        if not self._followings:
            self._followings = self.followings()
        if not self._followers:
            self._followers = self.followers()

        return list(set(self._followings) - set(self._followers))

    def dont_you_fallow(self):
        if not self._followings:
            self._followings = self.followings()
        if not self._followers:
            self._followers = self.followers()

        return list(set(self._followers) - set(self._followings))

    def follow(self, profile):
        self._init_driver()

        self.driver.get(PROFILE_URL(profile))
        self._add_cookies()
        self.driver.get(PROFILE_URL(profile))

        time.sleep(3)
        self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/section/main/div/header/section/div[1]/div['
                                           '1]/div/div/div/span/span[1]/button').click()

    def unfollow(self, profile):
        self._init_driver()

        self.driver.get(PROFILE_URL(profile))
        self._add_cookies()
        self.driver.get(PROFILE_URL(profile))

        time.sleep(3)
        self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/section/main/div/header/section/div[1]/div['
                                           '1]/div/div[2]/div/span/span[1]/button').click()
        time.sleep(2)
        self.driver.find_element(By.CLASS_NAME, 'mt3GC').click()

    def get_profile_pic(self, profile):
        self._init_driver()

        self.driver.get(PROFILE_URL(profile))
        self._add_cookies()
        self.driver.get(PROFILE_URL(profile))

        time.sleep(3)
        img = self.driver.find_element(By.XPATH,
                                       '//*[@id="react-root"]/div/div/section/main/div/header/div/div/span/img')

        return img.get_attribute("src")

    def get_all_post(self, profile):
        self._init_driver()

        self.driver.get(PROFILE_URL(profile))
        self._add_cookies()
        self.driver.get(PROFILE_URL(profile))

        self._scroll_till_end_page()

        post_box = self.driver.find_element(By.XPATH,
                                            '//*[@id="react-root"]/div/div/section/main/div/div[3]/article/div[1]/div')

        posts = post_box.find_elements(By.TAG_NAME, "img")

        return [x.get_attribute("src") for x in posts]

    def get_a_post(self, post_id):
        self._init_driver()

        self.driver.get(POST_URL(post_id))
        self._add_cookies()
        self.driver.get(POST_URL(post_id))

        img = self.driver.find_element(By.XPATH,
                                       '//*[@id="react-root"]/div/div/section/main/div/div[1]/article/div/div[''1'
                                       ']/div/div/div[1]/img')
        return img.get_attribute("src")
