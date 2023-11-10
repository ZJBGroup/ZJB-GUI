# coding:utf-8
import os
import sys

from qfluentwidgets import BoolValidator, ConfigItem, QConfig, qconfig


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """Config of application"""

    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())


cfg = Config()

if "APPDATA" in os.environ:
    confighome = os.environ["APPDATA"]
elif "XDG_CONFIG_HOME" in os.environ:
    confighome = os.environ["XDG_CONFIG_HOME"]
else:
    confighome = os.path.join(os.environ["HOME"], ".config")
configPath = os.path.join(confighome, "ZJBGUI/config.json")

qconfig.load(configPath, cfg)
