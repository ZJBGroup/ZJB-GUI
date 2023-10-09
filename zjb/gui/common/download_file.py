# coding: utf-8
import os
from urllib.request import urlopen

import requests
from PyQt5.QtCore import QObject, pyqtSignal
from tqdm import tqdm


class DownLoadFile(QObject):
    _downLoadFinished = pyqtSignal(str)

    def __init__(self, url, dst, parent=None):
        super().__init__(parent)
        self.url = url
        self.dst = dst

    def download_from_url(self):
        """
        @param: url to download file
        @param: dst place to put the file
        :return: bool
        """
        # 获取文件长度

        try:
            file_size = int(urlopen(self.url).info().get("Content-Length", -1))
        except Exception as e:
            print(e)
            print("错误，访问url: %s 异常" % self.url)
            return False

        # 文件大小
        if os.path.exists(self.dst):
            first_byte = os.path.getsize(self.dst)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size

        header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
        pbar = tqdm(
            total=file_size,
            initial=first_byte,
            unit="B",
            unit_scale=True,
            desc=self.url.split("/")[-1],
        )

        # 访问url进行下载
        req = requests.get(self.url, headers=header, stream=True)
        try:
            with open(self.dst, "ab") as f:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        pbar.update(1024)
        except Exception as e:
            print(e)
            return False

        pbar.close()
        self._downLoadFinished.emit("ok")
