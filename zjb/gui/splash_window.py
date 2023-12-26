import os
import sys
from threading import Thread

import requests
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout
from qfluentwidgets.components.widgets.progress_bar import ProgressBar
from qframelesswindow import AcrylicWindow

from zjb.gui._rc import find_resource_file
from zjb.gui.assets import (
    ASSETS,
    ASSETS_RAW_MIRROR,
    ASSETS_RAW_SITE,
    AssetInfo,
    check_mirror,
    missing_assets,
)


class SplashWindow(AcrylicWindow):
    downloadData = pyqtSignal(int, float)
    beginDownloadData = pyqtSignal(str)
    finishedSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._assetCount = len(ASSETS)

        self.init_widget()
        self.init_splash_window()
        self.downloadData.connect(self.updateValue)
        self.beginDownloadData.connect(self.updateText)
        self.finishedSignal.connect(openMainWindow)

        def updateDownloadInfo():
            base_url = ""
            flag = True
            for asset in missing_assets():
                os.makedirs(asset.path().parent, exist_ok=True)
                if not base_url:
                    base_url = ASSETS_RAW_MIRROR if check_mirror() else ASSETS_RAW_SITE
                flag = self.download_asset(asset, base_url)
            if flag:
                self.already_layout()
                from zjb.gui.main import MainWindow

                self.finishedSignal.emit("ok")
            else:
                self.network_layout()

        self.download_thread = Thread(target=updateDownloadInfo, daemon=True)
        self.download_thread.start()

    def updateValue(self, val, file_size):
        """更新进度条和进度数据文字"""
        self.progressBar.setValue(int(val))
        self.progress_label.setText(f"{round((val/100)*file_size,2)}M/ {file_size}M")

    def updateText(self, val):
        """下载不同文件的时候，更新不同的文案"""
        missing_assets_length = 0
        for _ in missing_assets():
            missing_assets_length = missing_assets_length + 1
        self._peocessNum = self._assetCount - missing_assets_length + 1
        self.text_label.setText(
            f"Downloading the {self._peocessNum}/{self._assetCount} resource: {val}"
        )

    def already_layout(self):
        """顺利下载完所有资源的 提示布局"""
        self.text_label.setText(
            "Everything is ready, Zhejiang Lab Brain is starting ..."
        )
        self.text_label.setStyleSheet(
            "QLabel#textlabel{font: 22px 'Microsoft YaHei Light';margin-top:40px;height:30px}"
        )
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.hide()
        self.progress_label.hide()

    def network_layout(self):
        """因网络问题终止下载 提示布局"""
        print("网络异常")
        self.text_label.setText(
            "Network error! \n please check network connection and restart"
        )
        self.text_label.setStyleSheet(
            "QLabel#textlabel{font: 20px 'Microsoft YaHei Light';margin-top:40px;height:30px;color:red}"
        )
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.progressBar.hide()
        self.progress_label.hide()

    def init_splash_window(self):
        """初始化窗口"""
        self.titleBar.maxBtn.hide()
        self.setFixedSize(700, 400)
        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=False)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def init_widget(self):
        """初始化布局"""
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 65, 20, 10)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # logo
        self.logo_label = QLabel(self)
        self.logo_label.setFixedSize(QSize(100, 100))
        self.logo_label.setPixmap(
            QtGui.QPixmap(find_resource_file("icon/logo_black_smaller.png"))
        )
        self.logo_label.setScaledContents(True)
        self.mainLayout.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignHCenter)
        # 标题
        self.title_label = QLabel(self)
        self.title_label.setObjectName("titlelabel")
        self.title_label.setText("Zhejiang Lab Brain")
        self.title_label.setStyleSheet(
            "QLabel#titlelabel{font: 25px 'Microsoft YaHei Light';margin-top:10px}"
        )
        self.mainLayout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignHCenter)
        # 文字说明
        self.text_label = QLabel(self)
        self.text_label.setObjectName("textlabel")
        self.text_label.setFixedWidth(600)
        self.text_label.setText(
            "Some necessary files are currently being downloaded ..."
        )
        self.text_label.setStyleSheet(
            "QLabel#textlabel{margin-top:80px;margin-bottom:5px}"
        )
        self.mainLayout.addWidget(self.text_label, 0, Qt.AlignmentFlag.AlignHCenter)
        # 进度条
        self.progressBar = ProgressBar(self)
        self.progressBar.setFixedSize(600, 5)
        self.progress_label = QLabel(self)
        self.progress_label.setFixedWidth(600)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.progress_label.setText("...")
        self.mainLayout.addWidget(self.progressBar, 0, Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.addWidget(self.progress_label, 0, Qt.AlignmentFlag.AlignHCenter)

    def download_asset(self, asset: AssetInfo, base_url):
        """下载资源

        Parameters
        ----------
        asset : AssetInfo
            要下载的资源
        base_url : str
            资源站点
        """
        url = asset.url(base_url)
        dst = asset.path()
        file_size = asset.size
        file_size_m = round(file_size / 1000000, 2)
        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return True
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        try:
            req = requests.get(url, headers=header, stream=True)
            self.beginDownloadData.emit(str(dst).split("\\")[-1])
            with open(dst, "ab") as f:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        first_byte = first_byte + 1024
                        self.downloadData.emit(
                            int(first_byte * 100 / file_size), file_size_m
                        )
            return True
        except Exception as e:
            print(e)
            return False


def openMainWindow():
    from zjb.gui.main import MainWindow

    m = MainWindow()
    w.hide()
    m.show()
    w.close()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = SplashWindow()
    w.show()
    app.exec_()
