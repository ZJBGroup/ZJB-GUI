"""Assets资源模块, 包括所依赖的公共资源列表及相关接口
"""
import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, TypeAlias

import requests

from .common.download_file import DownLoadFile

if TYPE_CHECKING:
    PathType: TypeAlias = "str | os.PathLike[str]"

ZJB_HOME = Path(os.environ.get("ZJB_HOME", os.path.expanduser("~/ZJB")))
"""ZJB家目录, 默认为`~/ZJB`, 如果存在同名环境变量 则使用环境变量的值"""
ASSETS_DIR = ZJB_HOME / "assets"
"""资源目录"""

ASSETS_RAW_SITE = "http://raw.githubusercontent.com/ZJBGroup/ZJB-Assets/main/"
"""资源下载站点"""
ASSETS_RAW_MIRROR = "http://23.227.194.15/raw/ZJBGroup/ZJB-Assets/main/"
"""资源下载镜像站点"""


class AssetInfo(NamedTuple):
    """资源信息"""

    name: str
    """资源名称"""
    size: int
    """资源大小(bytes)"""
    md5: str
    """资源md5值"""

    def path(self):
        return ASSETS_DIR / self.name

    def url(self, base_url: str = ASSETS_RAW_SITE):
        return base_url + self.name

    def exists(self):
        return self.path().exists()

    def check_size(self):
        return self.exists() and os.path.getsize(self.path()) == self.size

    def check_md5(self):
        return self.exists() and _md5sum(self.path()) == self.md5


ASSETS = [
    AssetInfo("images/welcome.gif", 47736626, "a8bdd9f92986e7336bbf5c6c4e71b3e6"),
    AssetInfo(
        "workspaces/workspace_basic.zip", 3268074, "4d972034409e0087ce5c142704e5ca57"
    ),
]


def _md5sum(path: "PathType", bs: int = 65535):
    """计算路径为`path`的文件的md5值, `bs`为分块读取的块大小"""
    hash = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(bs), b""):
            hash.update(block)
    return hash.hexdigest()


def missing_assets(md5=False):
    """生成所有缺失的资源

    Parameters
    ----------
    md5 : bool, optional
        检查MD5, by default False

    Yields
    ------
    AssetInfo
        缺失的资源信息
    """
    for asset in ASSETS:
        if asset.check_size():
            if not md5 or asset.check_md5():
                continue
        yield asset


def download_assets():
    """下载所有缺失资源"""
    base_url = ""
    for asset in missing_assets():
        if not base_url:
            base_url = ASSETS_RAW_MIRROR if _check_mirror() else ASSETS_RAW_SITE
        os.makedirs(asset.path().parent, exist_ok=True)
        DownLoadFile(asset.url(base_url), asset.path()).download_from_url()


def _check_mirror():
    """测试镜像是否可用"""
    try:
        requests.get(ASSETS_RAW_MIRROR, timeout=10)
        return True
    except:
        return False


os.makedirs(ASSETS_DIR, exist_ok=True)
