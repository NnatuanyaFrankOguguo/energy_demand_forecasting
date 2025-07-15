# %%
import logging
import os

#This makes sure every module (e.g., fetchers, transformers) logs to one central .log file.
# Color log format
class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: "\033[0;37m[DEBUG] %(message)s\033[0m",   # Gray
        logging.INFO: "\033[0;36m[INFO] %(message)s\033[0m",     # Cyan
        logging.WARNING: "\033[0;33m[WARN] %(message)s\033[0m",  # Yellow
        logging.ERROR: "\033[0;31m[ERROR] %(message)s\033[0m",   # Red
        logging.CRITICAL: "\033[1;41m[CRITICAL] %(message)s\033[0m",  # Red BG
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Setup logger
def get_logger(name="default"):
    logger = logging.getLogger(name)
    
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("logs/pipeline.log")
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
    return logger
# %%
