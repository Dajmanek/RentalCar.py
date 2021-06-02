from main import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray
import time_util


def _build_container() -> QtWidgets.QWidget:
    container = QtWidgets.QWidget()
    container.setLayout(QtWidgets.QVBoxLayout())
    container.layout().setContentsMargins(0, 0, 0, 0)
    container.layout().setSpacing(0)
    return container


def _clear(parent: QtWidgets.QWidget):
    while item := parent.layout().itemAt(0):
        if isinstance(item, QtWidgets.QSpacerItem):
            parent.layout().removeItem(item)
            continue
        item.widget().setParent(None)


def _open_window(app: App, window_type: WindowType, *args):
    app.open(window_type, *args)


def insert_content(parent: QtWidgets.QWidget, content: QtWidgets.QWidget):
    _clear(parent)
    parent.layout().addWidget(content)


def build_main_car_list(app: App, car_set=None) -> QtWidgets.QWidget:
    if car_set is None:
        car_set = set()

    container = _build_container()

    for car in car_set:
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setMinimumHeight(100)
        widget.setMaximumHeight(100)
        widget.layout().setContentsMargins(10, 0, 10, 0)
        widget.layout().setSpacing(10)
        widget.setProperty("class", "listLine")
        container.layout().addWidget(widget)
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        widget.mouseReleaseEvent = lambda event, _app = app, _car = car: _open_window(_app, WindowType.CAR, _car)

        image_label = QtWidgets.QLabel()
        image_label.setMinimumSize(150, 90)
        image_label.setMaximumSize(150, 90)
        if car.image is None:
            pixmap = QPixmap('resources/img/no_image.png')
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(car.image))
        image_label.setPixmap(pixmap.scaledToHeight(90))

        widget.layout().addWidget(image_label)
        name_label = QtWidgets.QLabel(car.brand + " " + car.model)
        name_label.setProperty("class", "labelBold")
        widget.layout().addWidget(name_label)
        widget.layout().addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                      QtWidgets.QSizePolicy.Minimum))

        price_widget = QtWidgets.QWidget()
        price_widget.setLayout(QtWidgets.QHBoxLayout())
        price_widget.layout().setContentsMargins(0, 0, 0, 0)
        price_label = QtWidgets.QLabel("Cena")
        price_label.setProperty("class", "labelBold")
        price_widget.layout().addWidget(price_label)
        price_label_content = QtWidgets.QLabel(str(car.price) + " zł/h")
        price_label_content.setProperty("class", "label")
        price_widget.layout().addWidget(price_label_content)
        widget.layout().addWidget(price_widget)

    container.layout().addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding))
    return container


def build_main_client_list(app: App, client_set=None) -> QtWidgets.QWidget:
    if client_set is None:
        client_set = set()

    container = _build_container()

    for client in client_set:
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setMinimumHeight(60)
        widget.setMaximumHeight(60)
        widget.layout().setContentsMargins(10, 0, 10, 0)
        widget.layout().setSpacing(50)
        widget.setProperty("class", "listLine")
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        container.layout().addWidget(widget)
        widget.mouseReleaseEvent = lambda event, _app=app, _client=client: _open_window(_app, WindowType.CLIENT,
                                                                                        _client)

        # IMAGE
        image_label = QtWidgets.QLabel()
        image_label.setMinimumSize(40, 40)
        image_label.setMaximumSize(40, 40)
        pixmap = QPixmap('resources/img/user.png')
        # pixmap.loadFromData(QByteArray(app.user_image))
        image_label.setPixmap(pixmap.scaled(40, 40))
        widget.layout().addWidget(image_label)

        # LEFT CONTENT
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(QtWidgets.QVBoxLayout())
        left_widget.layout().setSpacing(6)
        left_widget.setMinimumWidth(300)
        widget.layout().addWidget(left_widget)

        # -> FIRST LINE
        left_top_widget = QtWidgets.QWidget()
        left_top_widget.setLayout(QtWidgets.QHBoxLayout())
        left_top_widget.layout().setContentsMargins(0, 0, 0, 0)
        left_top_widget.layout().setSpacing(6)
        left_widget.layout().addWidget(left_top_widget)

        name_label = QtWidgets.QLabel("Imię i nazwisko:")
        name_label.setProperty("class", "labelListBold")
        left_top_widget.layout().addWidget(name_label)
        name_content_label = QtWidgets.QLabel(client.first_name + " " + client.last_name)
        name_content_label.setProperty("class", "labelList")
        left_top_widget.layout().addWidget(name_content_label)
        left_top_widget.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # -> SECOND LINE
        left_bottom_widget = QtWidgets.QWidget()
        left_bottom_widget.setLayout(QtWidgets.QHBoxLayout())
        left_bottom_widget.layout().setContentsMargins(0, 0, 0, 0)
        left_bottom_widget.layout().setSpacing(6)
        left_widget.layout().addWidget(left_bottom_widget)

        tel_label = QtWidgets.QLabel("Nr telefonu:")
        tel_label.setProperty("class", "labelListBold")
        left_bottom_widget.layout().addWidget(tel_label)
        tel_content_label = QtWidgets.QLabel(client.phone_number)
        tel_content_label.setProperty("class", "labelList")
        left_bottom_widget.layout().addWidget(tel_content_label)
        left_bottom_widget.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # RIGHT CONTENT
        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(QtWidgets.QVBoxLayout())
        right_widget.layout().setSpacing(6)

        # -> FIRST LINE
        right_top_widget = QtWidgets.QWidget()
        right_top_widget.setLayout(QtWidgets.QHBoxLayout())
        right_top_widget.layout().setContentsMargins(0, 0, 0, 0)
        right_top_widget.layout().setSpacing(6)
        right_widget.layout().addWidget(right_top_widget)

        rented_label = QtWidgets.QLabel("Wypożyczonych samochodów:")
        rented_label.setProperty("class", "labelListBold")
        right_top_widget.layout().addWidget(rented_label)
        rented_content_label = QtWidgets.QLabel((str(len(client.rented_cars))))
        rented_content_label.setProperty("class", "labelList")
        right_top_widget.layout().addWidget(rented_content_label)
        right_top_widget.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # -> SECOND LINE
        right_bottom_widget = QtWidgets.QWidget()
        right_bottom_widget.setLayout(QtWidgets.QHBoxLayout())
        right_bottom_widget.layout().setContentsMargins(0, 0, 0, 0)
        right_bottom_widget.layout().setSpacing(6)
        right_widget.layout().addWidget(right_bottom_widget)

        to_pay_label = QtWidgets.QLabel("Do zapłaty:")
        to_pay_label.setProperty("class", "labelListBold")
        right_bottom_widget.layout().addWidget(to_pay_label)
        to_pay_content_label = QtWidgets.QLabel(f"{client.to_pay():.02f} zł")
        to_pay_content_label.setProperty("class", "labelList")
        right_bottom_widget.layout().addWidget(to_pay_content_label)
        right_bottom_widget.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        widget.layout().addWidget(right_widget)

        # RIGHT SPACER
        widget.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

    container.layout().addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding))
    return container


def build_client_rented_cars(app: App, car_set: set = None) -> QtWidgets.QWidget:
    if car_set is None:
        car_set = set()

    container = _build_container()

    for car in car_set:
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setMinimumHeight(90)
        widget.setMaximumHeight(90)
        widget.layout().setContentsMargins(10, 1, 10, 1)
        widget.layout().setSpacing(20)
        widget.setProperty("class", "listLine")
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        container.layout().addWidget(widget)
        widget.mouseReleaseEvent = lambda event, _app=app, _car=car: _open_window(_app, WindowType.CAR, _car)

        # IMAGE
        image_label = QtWidgets.QLabel()
        image_label.setMaximumSize(140, 90)
        image_label.setMinimumSize(140, 90)
        if car.image is None:
            pixmap = QPixmap('resources/img/no_image.png')
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(car.image))
        image_label.setPixmap(pixmap.scaledToHeight(80))
        widget.layout().addWidget(image_label)

        # DATA
        data_widget = QtWidgets.QWidget()
        data_widget.setLayout(QtWidgets.QVBoxLayout())
        data_widget.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().setSpacing(0)
        widget.layout().addWidget(data_widget)

        # -> LINE 1
        data_widget_1 = QtWidgets.QWidget()
        data_widget_1.setLayout(QtWidgets.QHBoxLayout())
        data_widget_1.layout().setSpacing(6)
        data_widget_1.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().addWidget(data_widget_1)

        left_label_1 = QtWidgets.QLabel("Samochód:")
        left_label_1.setProperty("class", "labelListClientBold")
        data_widget_1.layout().addWidget(left_label_1)

        right_label_1 = QtWidgets.QLabel(car.brand + " " + car.model)
        right_label_1.setProperty("class", "labelListClient")
        data_widget_1.layout().addWidget(right_label_1)
        data_widget_1.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # -> LINE 2
        data_widget_2 = QtWidgets.QWidget()
        data_widget_2.setLayout(QtWidgets.QHBoxLayout())
        data_widget_2.layout().setSpacing(6)
        data_widget_2.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().addWidget(data_widget_2)

        left_label_2 = QtWidgets.QLabel("Data wypożyczenia:")
        left_label_2.setProperty("class", "labelListClientBold")
        data_widget_2.layout().addWidget(left_label_2)

        right_label_2 = QtWidgets.QLabel(time_util.date(car.rental_date))
        right_label_2.setProperty("class", "labelListClient")
        data_widget_2.layout().addWidget(right_label_2)
        data_widget_2.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # -> LINE 3
        data_widget_3 = QtWidgets.QWidget()
        data_widget_3.setLayout(QtWidgets.QHBoxLayout())
        data_widget_3.layout().setSpacing(6)
        data_widget_3.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().addWidget(data_widget_3)

        left_label_3 = QtWidgets.QLabel("Upłynęło:")
        left_label_3.setProperty("class", "labelListClientBold")
        data_widget_3.layout().addWidget(left_label_3)

        right_label_3 = QtWidgets.QLabel(
            time_util.get_duration_breakdown_short(time_util.current_time_mills() - car.rental_date))
        data_widget_3.layout().addWidget(right_label_3)
        data_widget_3.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # -> LINE 4
        data_widget_4 = QtWidgets.QWidget()
        data_widget_4.setLayout(QtWidgets.QHBoxLayout())
        data_widget_4.layout().setSpacing(6)
        data_widget_4.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().addWidget(data_widget_4)

        left_label_4 = QtWidgets.QLabel("Do zapłaty:")
        left_label_4.setProperty("class", "labelListClientBold")
        data_widget_4.layout().addWidget(left_label_4)

        right_label_4 = QtWidgets.QLabel(f"{car.to_pay():.2f} zł")
        right_label_4.setProperty("class", "labelListClient")
        data_widget_4.layout().addWidget(right_label_4)
        data_widget_4.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        widget.layout().addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        button = QtWidgets.QPushButton("Zwrot")
        button.mouseReleaseEvent = lambda event, _app=app, _car=car: _app.controllers.get(
            WindowType.CLIENT.value).on_click_return_car(_car)
        widget.layout().addWidget(button)

    container.layout().addItem(
        QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
    return container


def build_client_available_cars(app: App, car_set: set = None) -> QtWidgets.QWidget:
    if car_set is None:
        car_set = set()

    container = _build_container()
    for car in car_set:
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setMinimumHeight(90)
        widget.setMaximumHeight(90)
        widget.layout().setContentsMargins(10, 1, 10, 1)
        widget.layout().setSpacing(20)
        widget.setProperty("class", "listLine")
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        container.layout().addWidget(widget)
        widget.mouseReleaseEvent = lambda event, _app=app, _car=car: _open_window(_app, WindowType.CAR, _car)

        # IMAGE
        image_label = QtWidgets.QLabel()
        image_label.setMinimumSize(140, 90)
        image_label.setMaximumSize(140, 90)
        if car.image is None:
            pixmap = QPixmap('resources/img/no_image.png')
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(car.image))
        image_label.setPixmap(pixmap.scaledToHeight(80))
        widget.layout().addWidget(image_label)

        # DATA
        data_widget = QtWidgets.QWidget()
        data_widget.setLayout(QtWidgets.QVBoxLayout())
        data_widget.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().setSpacing(0)
        widget.layout().addWidget(data_widget)

        data_widget.layout().addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # -> LINE 1
        data_widget_1 = QtWidgets.QWidget()
        data_widget_1.setLayout(QtWidgets.QHBoxLayout())
        data_widget_1.layout().setSpacing(6)
        data_widget_1.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().addWidget(data_widget_1)

        left_label_1 = QtWidgets.QLabel("Samochód:")
        left_label_1.setProperty("class", "labelListClientBold")
        data_widget_1.layout().addWidget(left_label_1)

        right_label_1 = QtWidgets.QLabel(car.brand + " " + car.model)
        right_label_1.setProperty("class", "labelListClient")
        data_widget_1.layout().addWidget(right_label_1)
        data_widget_1.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # -> LINE 2
        data_widget_2 = QtWidgets.QWidget()
        data_widget_2.setLayout(QtWidgets.QHBoxLayout())
        data_widget_2.layout().setSpacing(6)
        data_widget_2.layout().setContentsMargins(0, 0, 0, 0)
        data_widget.layout().addWidget(data_widget_2)

        left_label_2 = QtWidgets.QLabel("Cena:")
        left_label_2.setProperty("class", "labelListClientBold")
        data_widget_2.layout().addWidget(left_label_2)

        right_label_2 = QtWidgets.QLabel(f"{car.price:.2f} zł")
        right_label_2.setProperty("class", "labelListClient")
        data_widget_2.layout().addWidget(right_label_2)
        data_widget_2.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        data_widget.layout().addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        widget.layout().addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        button = QtWidgets.QPushButton("Wypożycz")
        button.mouseReleaseEvent = lambda event, _app=app, _car=car: _app.controllers.get(
            WindowType.CLIENT.value).on_click_rent_car(_car)
        widget.layout().addWidget(button)

    container.layout().addItem(
        QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

    return container
