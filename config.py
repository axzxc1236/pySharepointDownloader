# Show debug message
debug = True
# if logfile is a string (e.g. "log.txt"), saves log to file
logfile = "log.txt"

# A browser user-agent, you can replace it with your own.
# You can see your user agent string at https://www.whatismybrowser.com/detect/what-is-my-user-agent/
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"

# If encounter an error, how long does this program wait to try again (in seconds)
# default value is 300 seconds (5 minutes)
retry_wait_time = 300

# How many files does downloader download at the same time
# 2 connections already saturated my connections at 500Mbps Internet
simultaneous_transfers = 2

"""
    How to configure tasks:
    tasks object is a list of objects
    [task1, task2, task3, task4.....]
    each task object then needs to be in this strcture:
    {
    "link": "https://xxxxxx.....",
    "downloadTo": "C:\\sharepoint",
    "password": None
    }
    * If your link doesn't have a password, write your password as
            "password": None
        NOT LIKE THE INCORRECT EXAMPLE BELOW!
            "password": "None"
    * If your "downloadTo" or "password" includes a back slash (\), you must either (NOT BOTH)
        (1) write every "\" as "\\"
        (2) prepend a "r" before first double column
            e.g.    "downloadTo": r"C:\sharepoint"
    * If your "downloadTo" or "password" includes a double column, you must write every "\" as "\\"
      (Technically you can use single quote to make a string... but not everyone knows how to Python)
"""

# Valid configuration example (links are made with Microsoft develoepr program which expires after October 1st 2023)
"""
tasks = [
{
  "link": "https://7sbvpw-my.sharepoint.com/:f:/g/personal/dfkfmg23345_7sbvpw_onmicrosoft_com/EpK4iQ5Sf0lFnh1PbRCEJWUBsm1v9vB5GwXh6gfSvTV94A?e=KLwXE1",
  "downloadTo": "/tmp/test",
  "password": None
},
{
  "link": "https://7sbvpw-my.sharepoint.com/:f:/g/personal/dfkfmg23345_7sbvpw_onmicrosoft_com/EkTE5VeR6IZCszmq3qRrS00B1FS4mNkDTCKeFWmbTVk3mg?e=1T16BH",
  "downloadTo": "/tmp/test_password_protected",
  "password": "Oh no.... I put a password on Github how will I live with this"
}
]
"""
# Above is configuration example, you want to modify texts below!

tasks = []
