from qfluentwidgets import InfoBar, InfoBarIcon


def _show_message(icon: InfoBarIcon, title: str, content: str, parent):
    InfoBar(
        icon=icon, title=title, content=content, duration=2000, parent=parent
    ).show()


def show_success(content: str, parent, title="Success"):
    _show_message(InfoBarIcon.SUCCESS, title, content, parent)


def show_info(content: str, parent, title="Info"):
    _show_message(InfoBarIcon.INFORMATION, title, content, parent)


def show_warning(content: str, parent, title="Warning"):
    _show_message(InfoBarIcon.WARNING, title, content, parent)


def show_error(content: str, parent, title="Error"):
    _show_message(InfoBarIcon.ERROR, title, content, parent)
