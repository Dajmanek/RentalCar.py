from enum import Enum
from controllers import *
from PyQt5 import QtWidgets


class WindowType(Enum):
    MAIN = 0
    LISTS = 1
    CLIENT = 2
    CLIENT_EDIT = 3
    CAR = 4
    CAR_EDIT = 5


class HistoryEntry:

    def __init__(self, window_type: WindowType, *args):
        self.window_type = window_type
        self.args = args


class App(QtWidgets.QApplication):

    def __init__(self):
        super(App, self).__init__([])
        # DATA
        self.car_storage = Storage()
        self.client_storage = Storage()

        # GUI INIT
        self.opened_window = None
        self.history = []
        self.controllers = {
            WindowType.MAIN.value: MainController(self),
            WindowType.LISTS.value: ListsController(self),
            WindowType.CLIENT.value: ClientController(self),
            WindowType.CLIENT_EDIT.value: ClientEditController(self),
            WindowType.CAR.value: CarController(self),
            WindowType.CAR_EDIT.value: CarEditController(self)
        }

        # GUI SHOW
        self.controllers[WindowType.MAIN.value].show()
        self.open(WindowType.LISTS)

    def clear_history(self):
        self.history.clear()

    def get_back(self) -> HistoryEntry:
        history_len = len(self.history)
        if history_len == 0:
            return HistoryEntry(WindowType.LISTS)
        if history_len > 1:
            del self.history[history_len - 1]
        return self.history[len(self.history) - 1]

    def back(self) -> bool:
        history_entry = self.get_back()
        return self._open(history_entry.window_type, False, *history_entry.args)

    def open(self, window_type: WindowType, *args) -> bool:
        return self._open(window_type, True, *args)

    def _open(self, window_type: WindowType, history: bool = True, *args) -> bool:
        if window_type.value == WindowType.MAIN.value:
            return False
        controller = self.controllers.get(window_type.value)
        if controller is None:
            return False
        if self.opened_window is not None:
            if self.opened_window.value == window_type.value:
                return False
            if opened := self.controllers.get(self.opened_window.value) is None:
                opened.close()
        if history:
            self.history.append(HistoryEntry(window_type, *args))
        self.opened_window = window_type
        self.controllers[WindowType.MAIN.value].insert_content(controller)
        controller.setup(*args)
        return True


if __name__ == '__main__':
    app = App()
    app.exec_()
