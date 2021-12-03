# -*-coding:utf-8 -*

from PyQt5.QtGui import QIcon
import PyQt5.QtWebEngineWidgets # must be included before creating a QApplication
from PyQt5.QtWidgets import QApplication
from MainWindow import *
import logging
from logging.handlers import RotatingFileHandler
import sys
import ctypes
from pathlib import Path

log_level = logging.DEBUG

root_logger = logging.getLogger()
root_logger.setLevel(log_level)
console_log_format = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] - %(message)s')
console_log_handler = logging.StreamHandler(sys.stdout)
console_log_handler.setLevel(log_level)
console_log_handler.setFormatter(console_log_format)
root_logger.addHandler(console_log_handler)

file_log_path = Path(os.path.expandvars("%APPDATA%")) / Path('CDItiquettes/logs') / "CDItiquettes.log.txt"
file_log_path.parent.mkdir(parents=True, exist_ok=True)
file_rotation_handler = RotatingFileHandler(
    file_log_path, maxBytes=1*1024*1024, backupCount=5)
root_logger.addHandler(file_rotation_handler)

qt_log_level = logging.WARNING
qt_loggers = [logging.getLogger(
    name) for name in logging.root.manager.loggerDict if "PyQt5" in name]
for one_qt_logger in qt_loggers:
    one_qt_logger.setLevel(qt_log_level)

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Unhandled exception", exc_info=(
        exc_type, exc_value, exc_traceback))
    sys.exit(-1)

if __name__ == '__main__':

    # Let's log exception in log:
    sys.excepthook = handle_unhandled_exception

    try:
        logging.info("")
        logging.info("")
        logging.info(
            "###########################################################")
        logging.info(
            "###########################################################")
        logging.info(
            "####                  Start of tool                    ####")
        logging.info(
            "###########################################################")
        logging.info(
            "###########################################################")
        logging.info("")
        logging.info("")

        app = QApplication(sys.argv)

        # set icon to app
        app.setWindowIcon(QIcon(str(Path("__file__").parent / "barcode.ico")))
        # the 2 next lines so the icon appear in the windows taskbar
        myappid = u'cdi.stickers'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except:
        logging.exception("Fatal error in main")
