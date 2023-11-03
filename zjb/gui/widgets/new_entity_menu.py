# coding:utf-8
import os

from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import Action, FluentIcon, RoundMenu
from zjb.dos.data import Data
from zjb.main.api import DTB, DTBModel, Project, Subject, Workspace

from .._global import GLOBAL_SIGNAL, get_workspace, open_workspace
from ..common.config_path import sync_recent_config
from ..common.utils import show_error
from .input_name_dialog import show_dialog


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
        self.action_delete = Action(
            FluentIcon.DELETE, "Delete", triggered=self._delete_entity
        )
        self.addAction(self.action_project)
        self.addAction(self.action_subject)
        self.addAction(self.action_dtb_model)
        self.addAction(self.action_dtb)

        if isinstance(self._item, Project):
            # 从列表右键点击一个 Project 打开菜单
            self.setActionState(get_workspace())
            self.removeAction(self.action_workspace)
            self.addAction(self.action_delete)
        elif self._item == None:
            # 从标题栏点击 New 按钮，打开菜单
            self.setActionState(get_workspace())
            self.insertAction(self.action_project, self.action_workspace)
            self.removeAction(self.action_delete)
        else:
            # 从列表右键点击一个 非Project的实体
            self.removeAction(self.action_workspace)
            self.removeAction(self.action_project)
            self.removeAction(self.action_subject)
            self.removeAction(self.action_dtb_model)
            self.removeAction(self.action_dtb)
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
        else:
            self.action_project.setDisabled(False)
            self.action_subject.setDisabled(False)
            self.action_dtb_model.setDisabled(False)
            self.action_dtb.setDisabled(False)

    def _new_workspace(self):
        """点击 Workspace 按钮，新建Workspace"""
        workspace_name = show_dialog("workspace")
        if workspace_name:
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
        getdata = show_dialog("Project", project=self._item)
        if getdata:
            parent_project: Project = getdata["Project"]
            name = getdata["name"]
            new_project = parent_project.add_project(name)
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(new_project, parent_project)
        else:
            show_error(
                self.getTips("Project"),
                self._window,
            )

    def _new_subject(self):
        """点击 Subject 按钮，新建 Subject"""
        getdata = show_dialog("Subject", project=self._item)
        if getdata:
            parent_project: Project = getdata["Project"]
            name = getdata["name"]
            new_subject = parent_project.add_subject(name)
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(new_subject, parent_project)
        else:
            show_error(
                self.getTips("Subject"),
                self._window,
            )

    def _new_dtb_model(self):
        """点击 DTBModel 按钮，新建 DTBModel"""
        getdata = show_dialog("DTBModel", project=self._item)
        if getdata:
            parent_project: Project = getdata["Project"]
            select_atlas = getdata["Atlas"]
            select_dynamics = getdata["DynamicModel"]
            name = getdata["name"]
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
        getdata = show_dialog("DTB", project=self._item)
        if getdata:
            print("getdata:", getdata)
            parent_project: Project = getdata["Project"]
            select_subject = getdata["Subject"]
            select_model = getdata["DTBModel"]
            select_connectivity = getdata["Connectivity"]
            name = getdata["name"]
            new_dtb = parent_project.add_dtb(
                name, select_subject, select_model, select_connectivity
            )
            GLOBAL_SIGNAL.dtbListUpdate[Data, Project].emit(new_dtb, parent_project)
        elif getdata == False:
            show_error(
                self.getTips("DTB"),
                self._window,
            )

    def _delete_entity(self):
        """删除实体"""
        GLOBAL_SIGNAL.dtbListUpdate[Data].emit(self._item)