from main import App, WindowType
from data import *
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QPixmap
import lists_builder
import re
import os


def _set_incorrect(field: QtWidgets.QLineEdit, incorrect: bool):
    field.setProperty("class", "incorrect" if incorrect else "")
    field.style().unpolish(field)
    field.style().polish(field)


def _check_if_matches(pattern, *args) -> bool:
    result = True
    for field in args:
        if not isinstance(field, QtWidgets.QLineEdit):
            continue
        matches = bool(re.fullmatch(pattern, field.text()))
        result &= matches
        _set_incorrect(field, not matches)
    return result


def _check_if_blank(*args):
    result = False
    for field in args:
        if not isinstance(field, QtWidgets.QLineEdit):
            continue
        blank = not field.text()
        result |= blank
        _set_incorrect(field, blank)
    return result


class Controller:

    def __init__(self, app: App, name: str):
        self.app = app
        self.widget: QtWidgets.QWidget = uic.loadUi('resources/ui/' + name + '.ui')
        self.widget.setStyleSheet(open("resources/styles/style.css").read())

    def setup(self, *args):
        pass

    def close(self):
        pass


class MainController(Controller):

    def __init__(self, app: App):
        super(MainController, self).__init__(app, "main")
        self.container_widget: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "container")
        self.content = None
        self.data_file = None

        self.widget.findChild(QtWidgets.QAction, "actionOpen").triggered.connect(self.on_click_open)
        self.widget.findChild(QtWidgets.QAction, "actionSave").triggered.connect(self.on_click_save)
        self.widget.findChild(QtWidgets.QAction, "actionSaveAs").triggered.connect(self.on_click_save_as)
        self.widget.findChild(QtWidgets.QAction, "actionAddCar").triggered.connect(self.on_click_add_car)
        self.widget.findChild(QtWidgets.QAction, "actionAddClient").triggered.connect(self.on_click_add_client)

    def show(self):
        self.widget.show()

    def insert_content(self, controller: Controller = None):
        if controller is None or controller.widget is None:
            return
        if self.content is not None:
            self.content.setParent(None)
        self.content = controller.widget
        self.container_widget.layout().addWidget(self.content)

    def on_click_open(self):
        dlg = QtWidgets.QFileDialog(None, "Otwórz plik", '', "RCData files (*.rcdat)")

        if dlg.exec_():
            file_name = dlg.selectedFiles()[0]
            with open(file_name, "rb") as file:
                data = Data(file)
                data.load()

                self.app.client_storage.clear()
                self.app.client_storage.add_all(data.client_set)
                self.app.car_storage.clear()
                self.app.car_storage.add_all(data.car_set)
                if self.app.opened_window is not None and self.app.opened_window.value == WindowType.LISTS.value:
                    self.app.controllers[WindowType.LISTS.value].search()
                else:
                    self.app.clear_history()
                    self.app.open(WindowType.LISTS)

    def on_click_save(self):
        if self.data_file is None:
            self.on_click_save_as()
            return
        with open(self.data_file, "wb") as file:
            data = Data(file, self.app.car_storage.get_all(), self.app.client_storage.get_all())
            data.save()

    def on_click_save_as(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(None, 'Zapisz jako', "", "RCData files (*.rcdat)")[0]
        if not file_name:
            return
        if len(file_name) < 6 or not file_name.endswith(".rcdat"):
            file_name += ".rcdat"
        self.data_file = file_name
        self.on_click_save()

    def on_click_add_car(self):
        if self.app.opened_window is not None and (
                self.app.opened_window.value == WindowType.CAR_EDIT.value or self.app.opened_window.value == WindowType.CLIENT_EDIT.value):
            self.app.get_back()
        self.app.open(WindowType.CAR_EDIT)

    def on_click_add_client(self):
        if self.app.opened_window is not None and (
                self.app.opened_window.value == WindowType.CAR_EDIT.value or self.app.opened_window.value == WindowType.CLIENT_EDIT.value):
            self.app.get_back()
        self.app.open(WindowType.CLIENT_EDIT)


class ListsController(Controller):

    def __init__(self, app: App):
        super(ListsController, self).__init__(app, "lists")
        self.search_thread = None
        self.tab: QtWidgets.QTabWidget = self.widget.findChild(QtWidgets.QTabWidget, "tab")
        self.tab.currentChanged.connect(lambda: self.search())
        self.cars_content: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "carsContent")
        self.clients_content: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "clientsContent")
        self.search_field: QtWidgets.QLineEdit = self.widget.findChild(QtWidgets.QLineEdit, "searchField")
        self.search_field.textChanged.connect(lambda text: self.search(text))

    def setup(self, *args):
        self.search()

    def search(self, text: str = None):
        if text is None:
            text = self.search_field.text()
        if self.tab.currentIndex() == 0:
            content = lists_builder.build_main_car_list(self.app, self.app.car_storage.search_all(text))
            lists_builder.insert_content(self.cars_content, content)
        else:
            content = lists_builder.build_main_client_list(self.app, self.app.client_storage.search_all(text))
            lists_builder.insert_content(self.clients_content, content)


class ClientController(Controller):

    def __init__(self, app: App):
        super(ClientController, self).__init__(app, "client")
        self.tab: QtWidgets.QTabWidget = self.widget.findChild(QtWidgets.QTabWidget, "tab")
        self.rented_content: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "rentedContent")
        self.available_content: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "availableContent")

        self.first_name_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "firstNameLabel")
        self.last_name_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "lastNameLabel")
        self.phone_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "phoneLabel")
        self.address_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "addressLabel")
        self.rented_cars_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "rentedCarsLabel")
        self.to_pay_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "toPayLabel")

        self.widget.findChild(QtWidgets.QPushButton, "backButton").pressed.connect(self.on_click_back)
        self.widget.findChild(QtWidgets.QPushButton, "editButton").pressed.connect(self.on_click_edit)
        self.widget.findChild(QtWidgets.QPushButton, "deleteButton").pressed.connect(self.on_click_delete)

        self.client = None

    def setup(self, *args):
        if not len(args) == 1 or not isinstance(args[0], Client):
            return
        self.client: Client = args[0]

        # SET LABELS
        self.first_name_label.setText(self.client.first_name)
        self.last_name_label.setText(self.client.last_name)
        self.phone_label.setText(self.client.phone_number)

        # SET ADDRESS LABEL
        address = self.client.post_code + ", " + self.client.city
        if self.client.street is not None:
            address += "\nul. " + self.client.street
        address += " " + self.client.building_number
        if self.client.flat_number is not None:
            address += "/" + self.client.flat_number
        self.address_label.setText(address)

        self._update_data()

    def _update_data(self):
        self.rented_cars_label.setText(str(len(self.client.rented_cars)))
        self.to_pay_label.setText(f"{self.client.to_pay():0.2f} zł")

        content_rented = lists_builder.build_client_rented_cars(self.app, set(self.client.rented_cars))
        lists_builder.insert_content(self.rented_content, content_rented)

        content_available = lists_builder.build_client_available_cars(self.app, set(
            filter(lambda car: not car.is_rented(), self.app.car_storage.get_all())))
        lists_builder.insert_content(self.available_content, content_available)

    def on_click_back(self):
        self.app.back()
        print("controllers.ClientController: on_click_back")

    def on_click_edit(self):
        if self.client is None:
            self.on_click_back()
        else:
            self.app.open(WindowType.CLIENT_EDIT, self.client)

    def on_click_delete(self):
        if self.client is not None:
            for car in self.client.rented_cars:
                car.client = None
                car.rental_date = 0
            self.app.client_storage.remove(self.client)
        self.on_click_back()

    def on_click_return_car(self, car: Car):
        if car is None or self.client is None:
            return
        self.client.remove_rented_car(car)
        self._update_data()

    def on_click_rent_car(self, car: Car):
        if car is None or self.client is None:
            return
        self.client.add_rented_car(car)
        self._update_data()


class ClientEditController(Controller):

    def __init__(self, app: App):
        super(ClientEditController, self).__init__(app, "client_edit")
        self.client = None

        self.fields = {
            "firstName": self.widget.findChild(QtWidgets.QLineEdit, "firstNameField"),
            "lastName": self.widget.findChild(QtWidgets.QLineEdit, "lastNameField"),
            "phone": self.widget.findChild(QtWidgets.QLineEdit, "phoneField"),
            "postCode": self.widget.findChild(QtWidgets.QLineEdit, "postCodeField"),
            "city": self.widget.findChild(QtWidgets.QLineEdit, "cityField"),
            "street": self.widget.findChild(QtWidgets.QLineEdit, "streetField"),
            "buildingNumber": self.widget.findChild(QtWidgets.QLineEdit, "buildingNumberField"),
            "flatNumber": self.widget.findChild(QtWidgets.QLineEdit, "flatNumberField")
        }

        for field in self.fields.values():
            field.focusInEvent = lambda event, _field=field: _set_incorrect(_field, False)
        self.fields["postCode"].textChanged.connect(self._on_edit_post_code)
        self.fields["phone"].textChanged.connect(self._on_edit_phone)
        self.fields["buildingNumber"].textChanged.connect(
            lambda text: self._on_edit_number_field(text, self.fields["buildingNumber"]))
        self.fields["flatNumber"].textChanged.connect(
            lambda text: self._on_edit_number_field(text, self.fields["flatNumber"]))

        self.widget.findChild(QtWidgets.QPushButton, "backButton").pressed.connect(self.on_click_back)
        self.widget.findChild(QtWidgets.QPushButton, "saveButton").pressed.connect(self.on_click_save)

    def setup(self, *args):
        for field in self.fields.values():
            _set_incorrect(field, False)

        if len(args) != 1 or not isinstance(args[0], Client):
            self.client = None
            for field in self.fields.values():
                field.setText("")
            return

        self.client: Client = args[0]
        self.fields["firstName"].setText(self.client.first_name)
        self.fields["lastName"].setText(self.client.last_name)
        self.fields["phone"].setText(self.client.phone_number)
        self.fields["postCode"].setText(self.client.post_code)
        self.fields["city"].setText(self.client.city)
        self.fields["street"].setText("" if self.client.street is None else self.client.street)
        self.fields["buildingNumber"].setText(str(self.client.building_number))
        self.fields["flatNumber"].setText("" if self.client.flat_number is None else str(self.client.flat_number))

    def _on_edit_post_code(self, text):
        if not bool(re.fullmatch(r'[0-9]{2}-[0-9]{3}', text)):
            text = "".join(re.findall(r'[0-9]*', text))
            if len(text) > 2:
                text = text[0:2] + "-" + text[2:min(len(text), 5)]
            self.fields["postCode"].setText(text)

    def _on_edit_phone(self, text):
        if not bool(re.fullmatch(r'[0-9]{9}', text)):
            text = "".join(re.findall(r'[0-9]*', text))
            text = text[0:min(9, len(text))]
            self.fields["phone"].setText(text)

    def _on_edit_number_field(self, text, field: QtWidgets.QLineEdit):
        if not bool(re.fullmatch('r[0-9]*', text)):
            field.setText("".join(re.findall(r'[0-9]*', text)))

    def on_click_back(self):
        self.app.back()

    def on_click_save(self):
        if _check_if_blank(*tuple(dict(filter(lambda entry: not entry[0] == "street" and not entry[0] == "flatNumber",
                                              self.fields.items())).values())):
            return
        if not _check_if_matches(r'[0-9]{9}', self.fields['phone']):
            return
        if not _check_if_matches(r'[0-9]{2}-{1}[0-9]{3}', self.fields['postCode']):
            return
        if not _check_if_matches(r'[0-9]*', self.fields['buildingNumber'], self.fields['flatNumber']):
            return

        new_client = self.client is None

        if new_client:
            self.client = Client(self.app.client_storage.next_id())
            self.app.client_storage.add(self.client)

        self.client.first_name = self.fields["firstName"].text()
        self.client.last_name = self.fields["lastName"].text()
        self.client.phone_number = self.fields["phone"].text()
        self.client.post_code = self.fields["postCode"].text()
        self.client.city = self.fields["city"].text()
        self.client.street = None if not self.fields["street"].text() else self.fields["street"].text()
        self.client.building_number = self.fields["buildingNumber"].text()
        self.client.flat_number = None if not self.fields["flatNumber"].text() else self.fields["flatNumber"].text()

        self.app.get_back()
        self.app.open(WindowType.CLIENT, self.client)


class CarController(Controller):

    def __init__(self, app: App):
        super(CarController, self).__init__(app, "car")
        self.car = None
        self.pixmap = None

        self.brand_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "brandLabel")
        self.model_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "modelLabel")
        self.price_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "priceLabel")
        self.status_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "statusLabel")
        self.to_pay_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "toPayLabel")
        self.client_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "clientLabel")
        self.rental_date_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "rentalDateLabel")
        self.duration_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "durationLabel")
        self.image_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "imageLabel")

        self.widget.findChild(QtWidgets.QPushButton, "backButton").pressed.connect(self._on_click_back)
        self.widget.findChild(QtWidgets.QPushButton, "editButton").pressed.connect(self._on_click_edit)
        self.widget.findChild(QtWidgets.QPushButton, "deleteButton").pressed.connect(self._on_click_delete)

        self.image_container: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "imageContainer")
        self.image_container.resizeEvent = lambda event: self._resize_image()

    def setup(self, *args):
        if not len(args) == 1 or not isinstance(args[0], Car):
            return
        self.car: Car = args[0]
        self.brand_label.setText(self.car.brand)
        self.model_label.setText(self.car.model)
        self.price_label.setText(f"{self.car.to_pay():.02f} zł")
        if self.car.is_rented():
            self.status_label.setText("niedostępny")
            self.to_pay_label.setText(f"{self.car.to_pay():.02f} zł")
            self.client_label.setText(self.car.client.first_name + " " + self.car.client.last_name)
            self.rental_date_label.setText(
                time_util.date(self.car.rental_date) + ", godz " + time_util.hour(self.car.rental_date))
            self.duration_label.setText(
                time_util.get_duration_breakdown(time_util.current_time_mills() - self.car.rental_date))
        else:
            self.status_label.setText("dostępny")
            self.to_pay_label.setText("-")
            self.client_label.setText("-")
            self.rental_date_label.setText("-")
            self.duration_label.setText("-")

        if self.car.image is None:
            self.pixmap = QPixmap("resources/img/no_image.png")
        else:
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(self.car.image)
        self.image_label.setPixmap(self.pixmap)

        self._resize_image()

    def close(self):
        self.pixmap = None

    def _resize_image(self, resize_event: QtGui.QResizeEvent = None):
        if self.pixmap is None:
            return

        if resize_event is None:
            max_width = self.image_container.width() - 100
            max_height = self.image_container.height() - 100
        else:
            max_width = resize_event.size().width() - 100
            max_height = resize_event.size().height() - 100

        if max_width < 1:
            max_width = 1
        if max_height < 1:
            max_height = 1

        multiplier = max_width / self.pixmap.width()
        if self.pixmap.height() * multiplier < max_height:
            self.image_label.setPixmap(self.pixmap.scaledToWidth(max_width))
        else:
            self.image_label.setPixmap(self.pixmap.scaledToHeight(max_height))

    def _on_click_back(self):
        self.app.back()

    def _on_click_edit(self):
        self.app.open(WindowType.CAR_EDIT, self.car)

    def _on_click_delete(self):
        if self.car is not None:
            if self.car.is_rented():
                self.car.client.remove_rented_car(self.car)
            self.app.car_storage.remove(self.car)
        self._on_click_back()


class CarEditController(Controller):

    def __init__(self, app: App):
        super(CarEditController, self).__init__(app, "car_edit")
        self.car = None
        self.pixmap = None
        self.image = None

        self.fields = {
            "brand": self.widget.findChild(QtWidgets.QLineEdit, "brandField"),
            "model": self.widget.findChild(QtWidgets.QLineEdit, "modelField"),
            "price": self.widget.findChild(QtWidgets.QLineEdit, "priceField")
        }
        self.image_label: QtWidgets.QLabel = self.widget.findChild(QtWidgets.QLabel, "imageLabel")

        self.fields["price"].textChanged.connect(self._on_edit_price)
        for field in self.fields.values():
            field.focusInEvent = lambda event, _field=field: _set_incorrect(_field, False)

        self.image_container: QtWidgets.QWidget = self.widget.findChild(QtWidgets.QWidget, "imageContainer")
        self.image_container.resizeEvent = lambda event: self._resize_image()

        self.widget.findChild(QtWidgets.QPushButton, "backButton").pressed.connect(self._on_click_back)
        self.widget.findChild(QtWidgets.QPushButton, "saveButton").pressed.connect(self._on_click_save)
        self.widget.findChild(QtWidgets.QPushButton, "chooseFileButton").pressed.connect(self._on_click_choose_file)

    def setup(self, *args):
        for field in self.fields.values():
            _set_incorrect(field, False)
        if not len(args) == 1 or not isinstance(args[0], Car):
            for field in self.fields.values():
                field.setText("")
            self.pixmap = QPixmap("resources/img/no_image.png")
            self._resize_image()
            return
        self.car: Car = args[0]
        self.fields["brand"].setText(self.car.brand)
        self.fields["model"].setText(self.car.model)
        self.fields["price"].setText(f"{self.car.price:.02f}")
        if self.car.image is None:
            self.pixmap = QPixmap("resources/img/no_image.png")
        else:
            self.image = self.car.image
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(self.image)
        self._resize_image()

    def _resize_image(self, resize_event: QtGui.QResizeEvent = None):
        if self.pixmap is None:
            return

        if resize_event is None:
            max_width = self.image_container.width() - 100
            max_height = self.image_container.height() - 100
        else:
            max_width = resize_event.size().width() - 100
            max_height = resize_event.size().height() - 100

        if max_width < 1:
            max_width = 1
        if max_height < 1:
            max_height = 1

        multiplier = max_width / self.pixmap.width()
        if self.pixmap.height() * multiplier < max_height:
            self.image_label.setPixmap(self.pixmap.scaledToWidth(max_width))
        else:
            self.image_label.setPixmap(self.pixmap.scaledToHeight(max_height))

    def _on_edit_price(self, text: str):
        if not bool(re.fullmatch(r'[0-9]+[.]?[0-9]{0,2}', text)):
            result = re.findall(r'[0-9.]*', text)
            text = ""
            if len(result) > 0:
                splitted = result[0].split(".")
                text = splitted[0]
                if len(splitted) > 1:
                    if len(text) == 0:
                        text += "0"
                    text += "."
                    text += splitted[1][0: 2 if len(splitted) >= 2 else 1]
            self.fields["price"].setText(text)
            pass

    def _on_click_choose_file(self):
        dlg = QtWidgets.QFileDialog(None, "Otwórz plik", '', "Image files (*.png *.jpg)")

        if dlg.exec_():
            file_name = dlg.selectedFiles()[0]
            with open(file_name, "rb") as file:
                self.image = file.read(os.path.getsize(file_name))
                self.pixmap = QPixmap()
                self.pixmap.loadFromData(self.image)
                self._resize_image()

    def _on_click_back(self):
        self.app.back()

    def _on_click_save(self):
        if _check_if_blank(*self.fields.values()):
            return
        if not _check_if_matches("[0-9]*.[0-9]{2}", self.fields["price"]):
            return

        new_car = self.car is None
        if new_car:
            self.car = Car(self.app.car_storage.next_id())
            self.app.car_storage.add(self.car)

        self.car.brand = self.fields["brand"].text()
        self.car.model = self.fields["model"].text()
        try:
            self.car.price = float(self.fields["price"].text())
        except ValueError:
            _set_incorrect(self.fields["price"], True)
            return

        if self.image is not None:
            self.car.image = self.image

        self.app.get_back()
        self.app.open(WindowType.CAR, self.car)
