# coding:utf-8
import os
import re

from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import Action, FluentIcon, RoundMenu

from zjb.dos.data import Data
from zjb.main.api import DTB, DTBModel, Project, Subject, Workspace

from .._global import GLOBAL_SIGNAL, get_workspace, open_workspace
from ..common.config_path import sync_recent_config
from ..common.utils import show_error
from ..pages.new_dynamics_page import NewDynamicsPage
from .input_name_dialog import (
    DTBCreationDialog,
    DTBModelCreationDialog,
    EntityCreationBase,
    dialog_workspace,
)


class NewEntityMenu(RoundMenu):
    """标题栏 New 按钮的下拉菜单 及列表的右键菜单"""

    def __init__(self, item: [Project, Subject, DTBModel, DTB] = None, window=None):
        super().__init__()
        self._item = item
        self._window = window
        self.action_workspace = Action(
            FluentIcon.FOLDER_ADD, "New Workspace", triggered=self._new_workspace
        )
        self.action_project = Action(
            FluentIcon.FOLDER_ADD, "New Project", triggered=self._new_project
        )
        self.action_subject = Action(
            FluentIcon.PEOPLE, "New Subject", triggered=self._new_subject
        )
        self.action_dtb_model = Action(
            FluentIcon.IOT, "New DTB Model", triggered=self._new_dtb_model
        )
        self.action_dtb = Action(FluentIcon.ALBUM, "New DTB", triggered=self._new_dtb)
        self.action_dynamic_model = Action(
            FluentIcon.ROBOT, "New Dynamic Model", triggered=self._new_dynamic_model
        )
        self.action_delete = Action(
            FluentIcon.DELETE, "Delete", triggered=self._delete_entity
        )

        if isinstance(self._item, Project):
            # 从列表右键点击一个 Project 打开菜单
            self.addAction(self.action_project)
            self.addAction(self.action_subject)
            self.addAction(self.action_dtb_model)
            self.addAction(self.action_dtb)
            if not isinstance(self._item, Workspace):
                self.addAction(self.action_delete)
        elif self._item == None:
            # 从标题栏点击 New 按钮，打开菜单
            self.setActionState(get_workspace())
            self.addAction(self.action_workspace)
            self.addAction(self.action_project)
            self.addAction(self.action_subject)
            self.addAction(self.action_dtb_model)
            self.addAction(self.action_dtb)
            self.addAction(self.action_dynamic_model)
        else:
            # 从列表右键点击一个 非Project的实体
            self.addAction(self.action_delete)

    def getTips(self, str):
        """获取创建实体失败的通用提示"""
        return (
            f"!!Failed to create {str} due to incorrect or incomplete input information"
        )

    def setActionState(self, workspace: Workspace):
        """修改按钮状态 没有打开工作空间的时候，禁用除了 Workspace 之外的操作"""
        if workspace == None:
            self.action_project.setDisabled(True)
            self.action_subject.setDisabled(True)
            self.action_dtb_model.setDisabled(True)
            self.action_dtb.setDisabled(True)
            self.action_dynamic_model.setDisabled(True)
        else:
            self.action_project.setDisabled(False)
            self.action_subject.setDisabled(False)
            self.action_dtb_model.setDisabled(False)
            self.action_dtb.setDisabled(False)
            self.action_dynamic_model.setDisabled(False)

    def _new_workspace(self):
        """点击 Workspace 按钮，新建Workspace"""
        workspace_name = dialog_workspace(parent=self._window)
        if workspace_name == "canel":
            return
        elif not workspace_name == False:
            w_path = QFileDialog.getExistingDirectory(self.window(), "New Workspace")
            if w_path:
                workspace_path = f"{w_path}/{workspace_name}"
                os.mkdir(workspace_path)
                sync_recent_config(workspace_name, workspace_path)
                open_workspace(workspace_path)
        else:
            show_error(
                self.getTips("Workspace"),
                self._window,
            )

    def _new_project(self):
        """点击 Project 按钮， 新建 Project"""
        title = "Choose a parent Project \nAnd name your Project:"
        w = EntityCreationBase(title, "Project", self._item, self._window)
        _getdata = False
        w.exec()
        if w.getflag() == "canel":
            _getdata = "canel"
        else:
            name = w.lineEdit.gettext().strip()
            if re.match(r"^.+$", name):
                _getdata = {"Project": w.getData["Project"], "name": name}

        if _getdata == "canel":
            return
        elif not _getdata == False:
            parent_project: Project = _getdata["Project"]
            name = _getdata["name"]
            new_project = parent_project.add_project(name)
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(new_project, parent_project)
        else:
            show_error(
                self.getTips("Project"),
                self._window,
            )

    def _new_subject(self):
        """点击 Subject 按钮，新建 Subject"""
        title = "Choose a parent Project \nAnd name your Subject:"
        w = EntityCreationBase(title, "Subject", self._item, self._window)
        _getdata = False
        w.exec()
        if w.getflag() == "canel":
            _getdata = "canel"
        else:
            name = w.lineEdit.gettext().strip()
            if re.match(r"^.+$", name):
                _getdata = {"Project": w.getData["Project"], "name": name}

        if _getdata == "canel":
            return
        elif not _getdata == False:
            parent_project: Project = _getdata["Project"]
            name = _getdata["name"]
            new_subject = parent_project.add_subject(name)
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(new_subject, parent_project)
        else:
            show_error(
                self.getTips("Subject"),
                self._window,
            )

    def _new_dtb_model(self):
        """点击 DTBModel 按钮，新建 DTBModel"""
        title = "Choose an Atlas and a Dynamic Model \nAnd name your DTBModel:"
        w = DTBModelCreationDialog(title, "DTBModel", self._item, self._window)
        _getdata = False
        w.exec()
        if w.getflag() == "canel":
            _getdata = "canel"
        else:
            name = w.lineEdit.gettext().strip()
            name_res = re.match(r"^.+$", name)
            if (
                name_res == None
                or w.getData["Atlas"] == None
                or w.getData["DynamicModel"] == None
            ):
                _getdata = False
            else:
                _getdata = {
                    "Project": w.getData["Project"],
                    "Atlas": w.getData["Atlas"],
                    "DynamicModel": w.getData["DynamicModel"],
                    "name": name,
                }

        if _getdata == "canel":
            return
        elif not _getdata == False:
            parent_project: Project = _getdata["Project"]
            select_atlas = _getdata["Atlas"]
            select_dynamics = _getdata["DynamicModel"]
            name = _getdata["name"]
            new_dtb_model = parent_project.add_model(
                name, select_atlas, select_dynamics
            )
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(
                new_dtb_model, parent_project
            )
        else:
            show_error(
                self.getTips("DTBModel"),
                self._window,
            )

    def _new_dtb(self):
        """点击 DTB 按钮，新建 DTB"""
        title = "Choose a Subject and a DTB Model\nAnd name your DTB:"
        w = DTBCreationDialog(title, "DTB", self._item, self._window)
        _getdata = False
        w.exec()
        if w.getflag() == "canel":
            _getdata = "canel"
        else:
            name = w.lineEdit.gettext().strip()
            name_res = re.match(r"^.+$", name)
            if (
                name_res == None
                or w.getData["Subject"] == None
                or w.getData["DTBModel"] == None
                or w.getData["Connectivity"] == None
            ):
                _getdata = False
            else:
                _getdata = {
                    "Project": w.getData["Project"],
                    "Subject": w.getData["Subject"],
                    "DTBModel": w.getData["DTBModel"],
                    "Connectivity": w.getData["Connectivity"],
                    "name": name,
                }

        if _getdata == "canel":
            return
        elif not _getdata == False:
            parent_project: Project = _getdata["Project"]
            select_subject = _getdata["Subject"]
            select_model = _getdata["DTBModel"]
            select_connectivity = _getdata["Connectivity"]
            name = _getdata["name"]
            new_dtb = parent_project.add_dtb(
                name, select_subject, select_model, select_connectivity
            )
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(new_dtb, parent_project)
        elif _getdata == False:
            show_error(
                self.getTips("DTB"),
                self._window,
            )

    def _new_dynamic_model(self):
        """点击按钮， 进入新建 dynamic model 界面"""
        GLOBAL_SIGNAL.dynamicModelUpdate.emit("New Dynamic Model", "copy")
        GLOBAL_SIGNAL.requestAddPage.emit(
            "New Dynamic Model",
            lambda _: NewDynamicsPage("New Dynamic Model", None, self._window),
        )

    def _delete_entity(self):
        """删除实体"""
        GLOBAL_SIGNAL.dtbListUpdate[Data].emit(self._item)
