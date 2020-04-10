import logging
import sys
import os
import subprocess as sb

def setup_logging():
    file_handler = logging.FileHandler("log.log")
    stream_handler = logging.StreamHandler(sys.stdout)

    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logging.basicConfig(
        level=logging.DEBUG, # TODO level=get_logging_level(),
        # format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            file_handler,
            stream_handler
        ]
    )

def mark_yourself_ready():
    hostname = os.environ['HOSTNAME']
    data_share_path = os.environ['DATA_SHARE_PATH']
    cmd = "touch {}/{}_ready.txt".format(data_share_path, hostname)

    logging.info("Marking as ready")
    sb.call([cmd], shell=True)

def log_info(msg):
    logging.info(msg)

def log_debug(*msgs):
    logging.debug(__get_print_statement(*msgs))


def __get_print_statement(*msgs):
    print_statement = ""
    for msg in msgs:
        print_statement = print_statement + str(msg) + " "
    return print_statement

def log_warning(msg):
    logging.warning(msg)

def log_critical(msg):
    logging.critical(msg)