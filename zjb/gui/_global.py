import os

from PyQt5.QtCore import QObject, pyqtSignal

from zjb.doj.lmdb_job_manager import LMDBJobManager
from zjb.dos.data import Data
from zjb.main.api import Project, Workspace


class _GlobalSignal(QObject):
    # 全局工作空间发生变化
    workspaceChanged = pyqtSignal([], [Workspace])

    # 新增页面信号
    requestAddPage = pyqtSignal(str, object)

    # 作业列表发生变化
    joblistChanged = pyqtSignal()

    # dtb列表更新信号
    dtbListUpdate = pyqtSignal([Data, Project], [Data])

    # mica 效果切换信号·
    micaEnableChanged = pyqtSignal(bool)

    # dynamics 更新信号 第一个routekey 第二个为type
    dynamicModelUpdate = pyqtSignal(str, object)

    # 创建刺激的空间分布信号
    stimulationSpaceCreated = pyqtSignal(str, list)


GLOBAL_SIGNAL = _GlobalSignal()


"""
Workspace相关
"""

_workspace = None
_workspace_path = None


def get_workspace() -> "Workspace | None":
    """获取全局工作空间

    Returns
    -------
    Workspace | None
        全局工作空间或None(未打开任何工作空间)
    """
    global _workspace
    return _workspace


def get_workspace_path() -> "str | None":
    """获取工作空间路径

    Returns
    -------
    str | None
        路径名
    """
    global _workspace_path
    return _workspace_path


def open_workspace(path: str, worker_count=0):
    """打开一个工作空间作为全局工作空间

    Parameters
    ----------
    path : str
        要打开的工作空间的路径

    worker_count : int
        表示需要启动的worker数量，如果为0则表示新建一个worker
    """
    global _workspace
    global _workspace_path

    _worker_count = worker_count
    if _worker_count == 0:
        # 获取本机CPU核数，结合配置文件 配置默认的 Worker 数量
        default_count = 5
        _worker_count = (
            default_count if os.cpu_count() > default_count else os.cpu_count()
        )

    jm = LMDBJobManager(path=path)
    _workspace = Workspace.from_manager(jm)
    _workspace.name = path.split("/")[len(path.split("/")) - 1]
    _workspace.start_workers(_worker_count)
    _workspace_path = path
    GLOBAL_SIGNAL.workspaceChanged[Workspace].emit(_workspace)


def close_workspace():
    """关闭全局工作空间"""
    global _workspace

    GLOBAL_SIGNAL.workspaceChanged.emit()
    _workspace = None
