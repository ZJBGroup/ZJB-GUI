# coding: utf-8
import json
import os


# 获取本地配置文件路径，若是路径下没有 ZJBGUI 的目录则创建
def get_local_config_path():
    if "APPDATA" in os.environ:
        confighome = os.environ["APPDATA"]
    elif "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ["XDG_CONFIG_HOME"]
    else:
        confighome = os.path.join(os.environ["HOME"], ".config")

    localConfigPath = os.path.join(confighome, "ZJBGUI")
    if not os.path.exists(localConfigPath):
        os.makedirs(localConfigPath)

    return localConfigPath


def sync_recent_config(name, path, worker_count="get", state="add"):
    """更新最近打开的工作空间的配置文件

    Parameters
    ----------
    name : str
        工作空间文件名称
    path : str
        工作空间路径，本页面所有 path 都包含文件名自身
    worker_count : str, optional
        该工作空间中Worker的数量，当取 get 时，表示调用该方法返回指定工作空间的 worker_count, by default "get"
    state : str, optional
        取 add 的时候，表示插入一条信息，取 del 的时候，表示没找到，删除这条信息, by default "add"

    Returns
    -------
    _worker_count
        当输入的 worker_count 为 get 的时候，返回指定工作空间的 worker_count 否则返回 None
    """
    _worker_count = worker_count
    configPath = f"{get_local_config_path()}/recent_workspace.json"

    if _worker_count == "get" and not state == "del":
        # 这时表示 打开一个工作空间需要获取 该工作空间的 worker_count
        default_count = 5 if os.cpu_count() > 5 else os.cpu_count()
        with open(configPath, "r") as f:
            recent_workspace = json.load(f)
        for item in recent_workspace:
            if path == item["path"]:
                # 配置文件中 包含 该路径的数据
                if "worker_count" in item and type(item["worker_count"]) == int:
                    # 能查找到路径下的数据，且 worker_count 是 int 类型
                    _worker_count = item["worker_count"]
                else:
                    # 路径下找不到数据，或者 worker_count 的数据类型不是 int 类型，都改为默认值
                    _worker_count = default_count
                break
        else:
            # 配置文件中 不包含 该路径的数据
            _worker_count = default_count

    # 打开配置文件，删除旧的数据，插入新的数据
    data = {"name": name, "path": path, "worker_count": _worker_count}
    recent_workspace = []
    with open(configPath, "r") as f:
        recent_workspace = json.load(f)
        for item in recent_workspace:
            if data["path"] == item["path"]:
                recent_workspace.remove(item)
                break
        if state == "add":
            recent_workspace.insert(0, data)
    with open(configPath, "w") as f:
        data_str = json.dumps(recent_workspace)
        f.write(data_str)

    return _worker_count if worker_count == "get" else None
