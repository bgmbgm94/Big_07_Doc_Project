import logging
import os
from datetime import datetime
import pytz
import time

# 로그 디렉토리 및 파일 설정
log_directory = "logs"
log_filename = "chatbot_server.log"
os.makedirs(log_directory, exist_ok=True)
log_filepath = os.path.join(log_directory, log_filename)

class KSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        utc_dt = datetime.fromtimestamp(record.created, pytz.utc)
        kst_dt = utc_dt.astimezone(pytz.timezone('Asia/Seoul'))
        if datefmt:
            s = kst_dt.strftime(datefmt)
        else:
            t = kst_dt.timetuple()
            s = time.strftime("%Y-%m-%d %H:%M:%S", t)
            s = "%s,%03d" % (s, record.msecs)
        return s

# 로깅 설정
formatter = KSTFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(log_filepath)
file_handler.setFormatter(formatter)

logger = logging.getLogger("app_logger")
logger.addHandler(file_handler)

# 로그 레벨 설정
logger.setLevel(logging.INFO)

