from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import FluentIcon, isDarkTheme, qconfig
from qtconsole import styles
from qtconsole.manager import QtKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from .._global import GLOBAL_SIGNAL, get_workspace
from .base_page import BasePage


class JupyterPage(BasePage):
    _ROUTER_KEY = "jupyter"

    def __init__(self, parent=None):
        super().__init__(self._ROUTER_KEY, "Jupyter", FluentIcon.TILES, parent)

        self._setup_ui()
        self._start()
        self.destroyed.connect(self._shutdown)

        self._init()

    def _update_style(self, theme=None):
        if isDarkTheme():
            self.widget.style_sheet = styles.default_dark_style_template % {
                "bgcolor": "rgba(255, 255, 255, 0.0605)",
                "fgcolor": "white",
                "select": "#555",
            }
            self.widget.syntax_style = styles.default_dark_syntax_style
        else:
            self.widget.style_sheet = styles.default_light_style_template % {
                "bgcolor": "rgba(255, 255, 255, 0.7)",
                "fgcolor": "black",
                "select": "#ccc",
            }
            self.widget.syntax_style = styles.default_light_syntax_style

    def _setup_ui(self):
        self.vboxLayout = QVBoxLayout(self)

        self.widget = RichJupyterWidget()
        self._update_style()
        self.vboxLayout.addWidget(self.widget)

        qconfig.themeChanged.connect(self._update_style)

    def _start(self):
        self.km = QtKernelManager()
        self.km.start_kernel()

        self.client = self.km.client()
        self.client.start_channels()
        self.widget.kernel_manager = self.km
        self.widget.kernel_client = self.client

    def _init(self):
        ws = get_workspace()
        if ws:
            self.client.execute(
                f"""\
from zjb.doj.lmdb_job_manager import LMDBJobManager
from zjb.main.api import Workspace

ws = Workspace.from_manager(LMDBJobManager(path="{ws.manager.path}"))
""",
                silent=True,
            )

    def _shutdown(self):
        self.client.stop_channels()
        self.km.shutdown_kernel()

    @classmethod
    def open(cls):
        GLOBAL_SIGNAL.requestAddPage.emit(cls._ROUTER_KEY, lambda _: cls())
