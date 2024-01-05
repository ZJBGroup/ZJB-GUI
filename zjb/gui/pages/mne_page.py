from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    MessageBoxBase,
    SmoothScrollArea,
    TitleLabel,
    TransparentPushButton,
    PrimaryPushButton,
)

from zjb.main.api import MNEsimSeries
from .base_page import BasePage
from ..widgets.mpl_widget import MplWidget


class RawArrayPage(BasePage):
    def __init__(self, mne_sim_series: MNEsimSeries):
        super().__init__(mne_sim_series._gid.str, "MNE Data", FluentIcon.FIT_PAGE)
        self.data = mne_sim_series.rawarray

        self._setup_ui()

    def _setup_ui(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(TitleLabel("MNE Series"))

        self.btn_ssp = PrimaryPushButton(f"SSP projections")
        self.btn_ssp.clicked.connect(self._ssp_projections)
        self.hBoxLayout.addWidget(self.btn_ssp)

        self.btn_channels = PrimaryPushButton(f"Channels series")
        self.btn_channels.clicked.connect(self._plot_channels)
        self.hBoxLayout.addWidget(self.btn_channels)

        self.btn_sensors = PrimaryPushButton(f"Sensor locations")
        self.btn_sensors.clicked.connect(self._plot_sensors)
        self.hBoxLayout.addWidget(self.btn_sensors)

        self.btn_power_spectra = PrimaryPushButton(f"Power Spectra")
        self.btn_power_spectra.clicked.connect(self._power_spectra)
        self.hBoxLayout.addWidget(self.btn_power_spectra)

        self.hBoxLayout.addStretch()

        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.scrollArea = SmoothScrollArea(self)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QFormLayout(self.scrollWidget)
        self.scrollLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        important_keys = [
            "acq_pars",
            "bads",
            "ch_names",
            "chs",
            "description",
            "dig",
            "experimenter",
            "nchan",
            "sfreq",
        ]

        for key in list(self.data.info.keys()):
            if key in important_keys:
                btn_info = self._create_data_button(key, self.data.info[key])
                self.scrollLayout.addRow(BodyLabel(key + ": "), btn_info)

        self.spacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        # self.scrollLayout.addItem(self.spacerItem)

    def _create_data_button(self, info_key, data):
        info_content = data
        if len(str(info_content)) <= 50:
            btn_info = TransparentPushButton(str(info_content))
        else:
            btn_info = TransparentPushButton(info_key)

        btn_info.setMaximumSize(10000, 30)
        btn_info.clicked.connect(
            lambda: self._show_info_data(info_key, str(info_content))
        )
        return btn_info

    def _show_info_data(self, name, data):
        w = ShowDataDialog(name, data, self)
        w.exec()

    def _ssp_projections(self):
        self.btn_ssp.setEnabled(False)
        self.scrollLayout.addRow(BodyLabel("Plot topographic maps of SSP projections:"))

        c = self.data.plot_projs_topomap(show=False)
        canvas = FigureCanvas(c)
        mplWidget = MplWidget()
        mplWidget.setMinimumSize(1000, 300)
        mplWidget.vertical_layout.addWidget(canvas)
        self.scrollLayout.addWidget(mplWidget)

    def _plot_channels(self):
        self.btn_channels.setEnabled(False)
        self.scrollLayout.addRow(BodyLabel("Plot Channel signals"))

        c = self.data.plot(show=False)
        canvas = FigureCanvas(c)
        mplWidget = MplWidget()
        mplWidget.setMinimumSize(1000, 700)
        mplWidget.vertical_layout.addWidget(canvas)
        self.scrollLayout.addWidget(mplWidget)

    def _plot_sensors(self):
        self.btn_sensors.setEnabled(False)
        self.scrollLayout.addRow(BodyLabel("Plot Sensor locations"))

        c = self.data.plot_sensors(show=False)
        canvas = FigureCanvas(c)
        mplWidget = MplWidget()
        mplWidget.setMinimumSize(1000, 500)
        mplWidget.vertical_layout.addWidget(canvas)
        self.scrollLayout.addWidget(mplWidget)

    def _power_spectra(self):
        self.btn_power_spectra.setEnabled(False)
        self.scrollLayout.addRow(BodyLabel("Plot Power Spectra"))

        c = self.data.plot_psd(show=False)
        canvas = FigureCanvas(c)
        mplWidget = MplWidget()
        mplWidget.setMinimumSize(1000, 700)
        mplWidget.vertical_layout.addWidget(canvas)
        self.scrollLayout.addWidget(mplWidget)


class ShowDataDialog(MessageBoxBase):
    def __init__(self, name, data, parent=None):
        super().__init__(parent=parent)
        self.info_key = name
        self.info_data = data
        self._setup_ui()

    def _setup_ui(self):
        self.viewLayout.addWidget(TitleLabel(self.info_key))
        self.viewLayout.addWidget(BodyLabel(f"{self.info_data}"))

        self.cancelButton.hide()
