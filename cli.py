import config, logging, platform, shutil
from downloader import Downloader

level = logging.DEBUG if config.debug else logging.INFO

if config.logfile:
    logging.basicConfig(
        level=level,
        format="%(asctime)s: %(message)s", handlers=[
            logging.FileHandler(config.logfile),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(
        level=level,
        format="%(asctime)s: %(message)s"
    )

# If not exists, prompt user to install rclone
if not shutil.which("rclone"):
    logging.critical("'rclone' is not found in PATH, please download rclone and add it to PATH, see https://rclone.org/downloads/")
    exit(1)

downloader = Downloader(
    user_agent = config.user_agent,
    retry_wait_time = config.retry_wait_time,
    tasks = config.tasks,
    simultaneous_transfers = config.simultaneous_transfers
)

downloader.run()

logging.info(f"Completed {downloader.completedTasks} tasks, skipped {downloader.skippedTasks} tasks")
