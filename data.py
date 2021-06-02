import abc
import time_util
from typing import IO


class Entry(abc.ABC):

    def __init__(self, id_):
        self.id = id_

    def is_similar_all(self, *texts) -> bool:
        result = True
        for arg in texts:
            if isinstance(arg, list) or isinstance(arg, set):
                for text in arg:
                    result &= self.is_similar(text)
            else:
                result &= self.is_similar(arg)
        return result

    @abc.abstractmethod
    def is_similar(self, text: str) -> bool:
        pass

    @abc.abstractmethod
    def serialize(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, string: str):
        raise NotImplementedError


class Car(Entry):

    def __init__(self, id_: int, price: float = None, brand: str = None, model: str = None, client: Entry = None,
                 rental_date: int = 0, image: bytes = None, image_bytes_len: int = 0, client_id: int = None):
        super(Car, self).__init__(id_)
        self.price = price
        self.brand = brand
        self.model = model
        self.client = client
        self.rental_date = rental_date
        self.image = image
        self.image_bytes_len = image_bytes_len if self.image is None else len(image)
        self.client_id = client_id
        self._image = None

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image: bytes = None):
        self._image = image
        if image is None:
            self.image_bytes_len = 0
        else:
            self.image_bytes_len = len(image)

    def is_rented(self) -> bool:
        return self.client is not None

    def to_pay(self) -> int:
        diff = time_util.current_time_mills() - self.rental_date
        hours = int(diff / 3600000)
        if diff % 3600000 > 0:
            hours += 1
        return hours * self.price

    def set_image(self, image: bytes):
        self.image = image

    def serialize(self) -> str:
        return str(self.id) + "," \
               + str(self.price) + "," \
               + self.brand + "," \
               + self.model + "," \
               + ("-1" if self.client is None else str(self.client.id)) + "," \
               + str(self.rental_date) + "," \
               + str(self.image_bytes_len)

    def deserialize(self, string: str):
        if not string:
            return None
        splitted = string.split(",")
        if len(splitted) < 7:
            return None
        try:
            car = Car(int(splitted[0]))
            car.price = float(splitted[1])
            car.brand = splitted[2]
            car.model = splitted[3]
            car.client_id = int(splitted[4])
            car.rental_date = int(splitted[5])
            car.image_bytes_len = int(splitted[6])
            return car
        except ValueError:
            return None

    def is_similar(self, text: str) -> bool:
        return self.brand.lower().startswith(text) or self.model.lower().startswith(text)


class Client(Entry):

    def __init__(self, id_: int, first_name: str = None, last_name: str = None, phone_number: str = None,
                 post_code: str = None, city: str = None, street: str = None, building_number: str = 0,
                 flat_number: str = None, rented_cars=None):
        super(Client, self).__init__(id_)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.post_code = post_code
        self.city = city
        self.street = street
        self.building_number = building_number
        self.flat_number = flat_number
        self.rented_cars = [] if rented_cars is None else rented_cars

    def add_rented_car(self, car: Car, set_rental_date: bool = True):
        if self.rented_cars.__contains__(car):
            return
        self.rented_cars.append(car)
        car.client = self
        if set_rental_date:
            car.rental_date = time_util.current_time_mills()

    def remove_rented_car(self, car: Car) -> bool:
        if not self.rented_cars.__contains__(car):
            return False
        car.client = None
        car.rental_date = 0
        self.rented_cars.remove(car)
        return True

    def to_pay(self) -> int:
        result = 0
        for car in self.rented_cars:
            result += car.to_pay()
        return result

    def serialize(self) -> str:
        return str(self.id) + "," \
               + self.first_name + "," \
               + self.last_name + "," \
               + self.phone_number + "," \
               + self.post_code + "," \
               + self.city + "," \
               + ("" if self.street is None else self.street) + "," \
               + self.building_number + "," \
               + ("-1" if self.flat_number is None else self.flat_number)

    def deserialize(self, string: str):
        if not string:
            return None
        splitted = string.split(",")
        if len(splitted) < 9:
            return None
        try:
            client = Client(int(splitted[0]))
            client.first_name = splitted[1]
            client.last_name = splitted[2]
            client.phone_number = splitted[3]
            client.post_code = splitted[4]
            client.city = splitted[5]
            client.street = splitted[6]
            client.building_number = splitted[7]
            client.flat_number = splitted[8]
            return client
        except ValueError:
            return None

    def is_similar(self, text: str) -> bool:
        return self.first_name.lower().startswith(text) or self.last_name.lower().startswith(text)


class Storage:

    def __init__(self, max_id: int = 0):
        self.max_id = max_id
        self.entry_set = set()

    def next_id(self) -> int:
        self.max_id += 1
        return self.max_id

    def get(self, id: int):
        if id is None:
            return None
        for entry in self.entry_set:
            if entry.id == id:
                return entry
        return None

    def get_all(self) -> set:
        return self.entry_set

    def add(self, entry: Entry):
        self.max_id = max(entry.id, self.max_id)
        self.entry_set.add(entry)

    def add_all(self, entry_set: set):
        if entry_set is None or len(entry_set) == 0:
            return
        self.max_id = max(self.max_id, max(entry_set, key=lambda entry: entry.id).id)
        self.entry_set.update(self.entry_set, entry_set)

    def remove(self, entry: Entry):
        self.entry_set.remove(entry)

    def clear(self):
        self.entry_set.clear()
        self.max_id = 0

    def search_all(self, text: str) -> set:
        return self.search(text, self.entry_set)

    @staticmethod
    def search(text: str, entry_set: set) -> set:
        if not text:
            return entry_set
        words = set(filter(lambda word: word, text.lower().split(" ")))
        return set(filter(lambda entry: entry.is_similar_all(words), entry_set))


class Data:

    def __init__(self, file: IO, car_set: set = None, client_set: set = None):
        self.file = file
        self.car_set = set() if car_set is None else car_set
        self.client_set = set() if client_set is None else client_set

    def load(self):
        if self.file is None:
            return
        header_bytes = self.file.read(12)

        clients_amount: int = int.from_bytes(header_bytes[0:4], 'big')
        cars_amount: int = int.from_bytes(header_bytes[4:8], 'big')

        clients_serialized: list = []
        clients_lines_amount: int = int.from_bytes(header_bytes[8:12], 'big')

        for i in range(clients_lines_amount):
            text_length = int.from_bytes(self.file.read(4), 'big')
            text_bytes = self.file.read(text_length)
            clients_serialized.append(text_bytes.decode("iso-8859-2"))

        self.client_set = deserialize_all(clients_serialized, Client(-1))
        car_worker = Car(-1)
        for i in range(cars_amount):
            car_bytes_amount = int.from_bytes(self.file.read(4), 'big')
            car_bytes = self.file.read(car_bytes_amount)
            car = deserialize(car_bytes.decode("iso-8859-2"), car_worker)
            if car is None:
                continue
            if car.image_bytes_len > 0:
                car.image = self.file.read(car.image_bytes_len)

            self.car_set.add(car)
        for car in self.car_set:
            if car.client_id is None or car.client_id == -1:
                continue
            clients = list(filter(lambda client: client.id == car.client_id, self.client_set))
            if len(clients) > 0:
                clients[0].add_rented_car(car, False)

    def save(self):
        if self.file is None:
            return
        header_bytes: bytes = len(self.client_set).to_bytes(4, "big")
        header_bytes += len(self.car_set).to_bytes(4, "big")

        clients_serialized: list = serialize_all(self.client_set, 100)
        header_bytes += len(clients_serialized).to_bytes(4, "big")

        self.file.write(header_bytes)

        for string in clients_serialized:
            self.file.write(len(string).to_bytes(4, "big"))
            self.file.write(string.encode("iso-8859-2"))

        for car in self.car_set:
            car_serialized = car.serialize()
            self.file.write(len(car_serialized).to_bytes(4, "big"))
            self.file.write(car_serialized.encode("iso-8859-2"))
            if car.image is not None:
                self.file.write(car.image)


def serialize(entry: Entry) -> str:
    return entry.serialize()


def serialize_all(entry_set: set, buf: int = None) -> list:
    string_list = []
    if len(entry_set) < 1:
        return string_list

    if buf is None:
        for entry in entry_set:
            string_list.append(entry.serialize())
        return string_list

    if buf < 1:
        return string_list
    i = 0
    temp = ""
    for entry in entry_set:
        if i >= buf:
            string_list.append(temp)
            temp = ""
            i = 0
        if i != 0:
            temp += ";"
        temp += entry.serialize()
        i += 1
    if temp:
        string_list.append(temp)
    return string_list


def deserialize(string: str, entry: Entry) -> Entry:
    return entry.deserialize(string)


def deserialize_all(string_list: list, entry_worker: Entry) -> set:
    entry_set = set()
    if string_list is None or len(string_list) == 0 or entry_worker is None:
        return entry_set

    for string_line in string_list:
        splitted = string_line.split(";")
        for string in splitted:
            entry = entry_worker.deserialize(string)
            if entry is None:
                continue
            entry_set.add(entry)
    return entry_set
