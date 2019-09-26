"""
A lightweight steam account manager and switcher.

Usage:
    steam-acolyte [options]
    steam-acolyte [options] store
    steam-acolyte [options] switch <USER>
    steam-acolyte [options] start <USER>

Options:
    -r ROOT, --root ROOT        Steam root path
"""

from steam_acolyte import __version__
from steam_acolyte.steam import Steam

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from docopt import docopt

import sys


def main(args=None):
    opts = docopt(__doc__, args, version=__version__)
    try:
        steam = Steam(opts['--root'])
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1

    if opts['store']:
        steam.store_login_cookie()
    elif opts['switch']:
        steam.switch_user(opts['<USER>'])
    elif opts['start']:
        steam.switch_user(opts['<USER>'])
        steam.run()
        steam.store_login_cookie()
    else:
        run_gui(steam)


def run_gui(steam):
    from steam_acolyte.window import create_login_dialog
    import signal
    app = QApplication([])
    sys.excepthook = except_handler
    # Setup handling of KeyboardInterrupt (Ctrl-C) for PyQt:
    # By default Ctrl-C has no effect in PyQt. For more information, see:
    # https://riverbankcomputing.com/pipermail/pyqt/2008-May/019242.html
    # https://docs.python.org/3/library/signal.html#execution-of-python-signal-handlers
    # http://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-console
    signal.signal(signal.SIGINT, interrupt_handler)
    safe_timer(50, lambda: None)
    steam.login_window = create_login_dialog(steam)
    steam.login_window.show()
    return app.exec_()


def except_handler(*args, **kwargs):
    import traceback
    traceback.print_exception(*args, **kwargs)
    QApplication.quit()


def interrupt_handler(signum, frame):
    """Handle KeyboardInterrupt: quit application."""
    QApplication.quit()


def safe_timer(timeout, func, *args, **kwargs):
    """
    Create a timer that is safe against garbage collection and overlapping
    calls. See: http://ralsina.me/weblog/posts/BB974.html
    """
    def timer_event():
        try:
            func(*args, **kwargs)
        finally:
            QTimer.singleShot(timeout, timer_event)
    QTimer.singleShot(timeout, timer_event)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))