import logging
from PySide2.QtGui import QIcon, QKeySequence, QKeyEvent
from PySide2.QtCore import QUrl, Qt, QEvent
from PySide2.QtWidgets import QMainWindow, QShortcut, QApplication
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile, QWebEnginePage

USER_AGENT = 'Roku/DVP-23.0 (23.0.0.99999-02)'
WINDOW_CLOSE_ERROR = "Scripts may close only the windows that were opened by them."

class WebEnginePage(QWebEnginePage):
    def __init__(self, window, profile, webview):
        QWebEnginePage.__init__(self, profile, webview)
        self.parent_window = window
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):  
        if (level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel) and \
            WINDOW_CLOSE_ERROR.casefold() in message.casefold():
            self.parent_window.close()

        if (level == QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel):
            logging.info(f"js: {message}")
        elif (level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel):
            logging.warn(f"js: {message}")
        else: # QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel
            logging.error(f"js: {message}")
            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube on TV")
        self.setWindowIcon(QIcon.fromTheme("com.webyfy.yttv"))

        # Create a QShortcut for the XF86Back key
        self.xf86back_shortcut = QShortcut(QKeySequence('Back'), self)
        # Connect the shortcut to a function that emits an escape key press
        self.xf86back_shortcut.activated.connect(lambda: self.fake_key_press(Qt.Key_Escape))

        webview = QWebEngineView()
        webview.settings().setAttribute(QWebEngineSettings.ShowScrollBars, False)
        webview.setContextMenuPolicy(Qt.NoContextMenu)
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(USER_AGENT)
        webpage = WebEnginePage(self, profile, webview)
        webpage.windowCloseRequested.connect(self.close)
        webview.setPage(webpage)
        # webview.load(QUrl("https://www.youtube.com/tv"))
        webview.load(QUrl("https://duck.com"))

        self.setCentralWidget(webview)

    def fake_key_press(self,
                       key: Qt.Key,
                       modifier: Qt.KeyboardModifier = Qt.NoModifier) -> None:
        """Send a fake key event."""
        press_evt = QKeyEvent(QEvent.KeyPress, key, modifier, 0, 0, 0)
        release_evt = QKeyEvent(QEvent.KeyRelease, key, modifier,
                                0, 0, 0)
        QApplication.postEvent(self, press_evt)
        QApplication.postEvent(self, release_evt)