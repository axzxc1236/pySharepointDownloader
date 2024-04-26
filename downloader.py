import logging, traceback, re, subprocess
import requests # 3rd party librart
from secrets import token_hex
from shutil import which
from time import sleep
from typing import Optional
from pathlib import Path
from urllib.parse import parse_qs, urlparse

class EmptyTasksException(Exception):
    pass

class InvalidLinkException(Exception):
    pass

class RateLimitException(Exception):
    pass

class PasswordRequiredException(Exception):
    pass

class InvalidPasswordException(Exception):
    pass

class CannotContinueException(Exception):
    pass

htmlFormPattern = re.compile(r'<input type="hidden" name="([^"]*)" id="\1" value="([^"]*)" \/>')
hostURLPattern = re.compile(r'https:\/\/.*\.sharepoint\.com')
passwordPostURLPattern = re.compile(r'action="([^"]*)"')
webAbsoluteUrlPattern = re.compile(r'"webAbsoluteUrl":"([^"]+)"')

class Downloader:
    def __init__(self,
                 user_agent: str,
                 retry_wait_time: int,
                 tasks: list,
                 simultaneous_transfers: int):
        self.skippedTasks = 0
        self.completedTasks = 0
        self.user_agent = user_agent
        self.retry_wait_time = retry_wait_time
        self.headers = {
            "User-Agent": user_agent
        }      
        if len(tasks) == 0:
            raise EmptyTasksException("Task list is empty")
        for task in tasks:
            if "sharepoint.com" not in task["link"]:
                raise InvalidLinkException(f"'{task['link']}' is not a sharepoint.com link.")
            elif "onedrive.aspx" in task["link"]:
                raise InvalidLinkException(f"'{task['link']}' contains 'onedrive.aspx', this link is not usable for this program, you need to put in a link that redirects you to the link.")
            Path(task['downloadTo']).mkdir(parents=True, exist_ok=True)
        self.tasks = tasks
        self.simultaneous_transfers = simultaneous_transfers
    
    def run(self):
        taskIndex = 0
        numberOfTasks = len(self.tasks)
        while taskIndex < numberOfTasks:
            try:
                logging.info(f"Running task {taskIndex + 1}/{numberOfTasks}")
                task = self.tasks[taskIndex]
                session = requests.session()
                response = session.get(task["link"], headers=self.headers, timeout=20)
                if response.status_code == 429:
                    raise RateLimitException()
                elif response.status_code > 299:
                    raise CannotContinueException(f"While reading file list, program encountered unknown HTTP response code {response.status_code}")
                if "You've received a link to a folder that requires a password" in response.text or 'input id="txtPassword"' in response.text or 'input name="txtPassword"' in response.text:
                    if password := task["password"]:
                        # Extract post url
                        if (host := hostURLPattern.match(task["link"])) and (formAction := passwordPostURLPattern.search(response.text)):
                            passwordSubmitUrl = host.group(0) + formAction.group(1).replace("amp;","")
                        else:
                            raise CannotContinueException("Link has required password, but program failed to find password submit url")
                        
                        # Extract html form
                        payload = {}
                        for match in htmlFormPattern.finditer(response.text):
                            payload[match.group(1)] = match.group(2)
                        payload["__EVENTTARGET"] = "btnSubmitPassword"
                        payload["__EVENTARGUMENT"] = ""
                        payload["txtPassword"] = task["password"]
                        logging.debug(f"Password submit url: {passwordSubmitUrl}")
                        # logging.debug(f"Password submit payload: {payload}")
                        response = session.post(passwordSubmitUrl, headers=self.headers, data=payload, timeout=20)
                        if response.status_code == 429:
                            raise RateLimitException()
                        elif response.status_code > 299:
                            raise CannotContinueException(f"While reading file list, program encountered unknown HTTP response code {response.status_code}")
                        if "You've received a link to a folder that requires a password" in response.text or 'input id="txtPassword"' in response.text:
                            raise InvalidPasswordException()
                    else:
                        raise PasswordRequiredException("Password is required but a password is not given, skipping task")
                
                cookies = response.cookies
                if "FedAuth" not in cookies:
                    raise CannotContinueException("Downloader failed to get cookie from Sharepoint")
                
                params = parse_qs(urlparse(response.url).query)
                if "id" not in params:
                    raise CannotContinueException("Can't determine webdav endpoint")
                
                if match := webAbsoluteUrlPattern.search(response.text):
                    webdavEndpoint = match.group(1) + "/" + "/".join(params["id"][0].split("/")[3:])
                    logging.debug(f"webdav Endpoint: {webdavEndpoint}")
                
                with open("sharepoint_rclone.conf", mode="w", encoding="utf8") as f:
                    f.write("[webdav]\n")
                    f.write("type = webdav\n")
                    f.write(f"url = {webdavEndpoint}\n")
                    f.write("vendor = other\n")
                    f.write(f"headers = Cookie,FedAuth={cookies['FedAuth']}")
                rclone = subprocess.run([which("rclone"), "--config", "sharepoint_rclone.conf", "copy", "--progress", "--transfers", str(self.simultaneous_transfers), "webdav:", task['downloadTo']])
                if rclone.returncode != 0:
                    logging.info(f"rclone exited with status code {rclone.returncode} which indicates an error, sleep for {self.retry_wait_time} seconds")
                    sleep(self.retry_wait_time)
                else:
                    self.completedTasks += 1
                    taskIndex += 1
            except PasswordRequiredException:
                logging.info("Password is required but no password is given, skip to next task.")
                taskIndex += 1
                self.skippedTasks += 1
            except InvalidPasswordException:
                logging.info(f"Password is required and the password given is invalid, skip to next task.")
                taskIndex += 1
                self.skippedTasks += 1
            except RateLimitException:
                logging.info(f"Link given is currently rate limited, sleep for {self.retry_wait_time} seconds.")
                sleep(self.retry_wait_time)
            except CannotContinueException as e:
                logging.info(f"Downloader encountered a problem that can't be solved: {e}")
                logging.info("Skip to next task.")
                taskIndex += 1
                self.skippedTasks += 1
            except Exception as e:
                logging.info(f"Enountered an unknown error {e} while running task, sleep for {self.retry_wait_time} seconds.")
                logging.debug(traceback.format_exc())
                sleep(self.retry_wait_time)
