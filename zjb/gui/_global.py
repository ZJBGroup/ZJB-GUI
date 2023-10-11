from PyQt5.QtCore import QObject, pyqtSignal

from zjb.doj.lmdb_job_manager import LMDBJobManager
from zjb.main.manager.workspace import Workspace


class _GlobalSignal(QObject):
    # 全局工作空间发生变化
    workspaceChanged = pyqtSignal([], [Workspace])


GLOBAL_SIGNAL = _GlobalSignal()


"""
Workspace相关
"""

_workspace = None


def get_workspace() -> "Workspace | None":
    """获取全局工作空间

    Returns
    -------
    Workspace | None
        全局工作空间或None(未打开任何工作空间)
    """
    global _workspace
    return _workspace


def open_workspace(path: str):
    """打开一个工作空间作为全局工作空间

    Parameters
    ----------
    path : str
        要打开的工作空间的路径
    """
    global _workspace

    jm = LMDBJobManager(path=path)
    _workspace = Workspace.from_manager(jm)
    GLOBAL_SIGNAL.workspaceChanged[Workspace].emit(_workspace)


def close_workspace():
    """关闭全局工作空间"""
    global _workspace

    GLOBAL_SIGNAL.workspaceChanged.emit()
    _workspace = None
