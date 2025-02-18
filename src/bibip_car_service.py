import os
from datetime import datetime
from decimal import Decimal
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


MODELS_FILE: str = 'models.txt'
MODELS_INDEX_FILE: str = 'models_index.txt'
CARS_FILE: str = 'cars.txt'
CARS_INDEX_FILE: str = 'cars_index.txt'
SALES_FILE: str = 'sales.txt'
SALES_INDEX_FILE: str = 'sales_index.txt'
ROW_LEN: int = 500
OVER_ROW_LEN = 501


class Index:
    def __init__(self, id: str, index: str) -> None:
        self.id: str = id
        self.index: str = index


class IndexCasher:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    @staticmethod
    def cash(file_path: str) -> list:
        cached_index: list = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as table:
                lines: list[str] = table.readlines()
                split_lines = list(
                    map(lambda line: line.strip().split(','), lines)
                )
                return list(
                    map(
                        lambda splited_line: Index(
                            id=splited_line[0], index=splited_line[1]
                            ), split_lines
                        )
                )
        return cached_index


class CarService:
    def __init__(self, root_dir_path: str) -> None:
        self.root_dir_path = root_dir_path
        self.models_index: list[Index] = IndexCasher.cash(
            self.__make_path(MODELS_FILE)
        )
        self.cars_index: list[Index] = IndexCasher.cash(
            self.__make_path(CARS_FILE)
        )
        self.sales_index: list[Index] = IndexCasher.cash(
            self.__make_path(SALES_FILE)
        )

    def __make_path(self, file_name: str) -> str:
        return '/'.join([self.root_dir_path, file_name])

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        with open(
            self.__make_path(MODELS_FILE), 'a'
        ) as model_file:
            models_string: str = (
                f'{model.id},{model.name},{model.brand}'.ljust(ROW_LEN)
            )
            model_file.write(models_string + '\n')

        model_index: Index = Index(
            id=model.index(), index=str(len(self.models_index))
        )

        self.models_index.append(model_index)
        self.models_index.sort(key=lambda x: x.id)

        with open(
            self.__make_path(MODELS_INDEX_FILE), 'w'
        ) as model_index_file:
            for model_index in self.models_index:
                string_index_model: str = (
                    f'{model_index.id},{model_index.index}'.ljust(ROW_LEN)
                )
                model_index_file.write(string_index_model + '\n')
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        with open(
            self.__make_path(CARS_FILE), 'a'
        ) as cars_file:
            cars_string: str = (
                f'{car.vin},{car.model},{car.price},'
                f'{car.date_start},{car.status}'.ljust(ROW_LEN)
            )
            cars_file.write(cars_string + '\n')

        car_index: Index = Index(
            id=car.index(), index=str(len(self.cars_index)))

        self.cars_index.append(car_index)
        self.cars_index.sort(key=lambda x: x.id)

        with open(
            self.__make_path(CARS_INDEX_FILE), 'w'
        ) as cars_index_file:
            for cars_index in self.cars_index:
                string_index_car: str = (
                    f'{cars_index.id},{cars_index.index}'.ljust(ROW_LEN)
                )
                cars_index_file.write(string_index_car + '\n')
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        with open(
            self.__make_path(SALES_FILE), 'a'
        ) as sales_file:
            sale_string: str = (
                f'{sale.sales_number},{sale.car_vin},'
                f'{sale.sales_date},{sale.cost}'.ljust(ROW_LEN)
            )
            sales_file.write(sale_string + '\n')

        sale_index: Index = Index(
            id=sale.index(), index=str(len(self.sales_index))
        )
        self.sales_index.append(sale_index)
        self.sales_index.sort(key=lambda x: x.id)

        with open(
            self.__make_path(SALES_INDEX_FILE), 'w+'
        ) as sales_index_file:
            for sales_index in self.sales_index:
                string_index_model: str = (
                    f'{sales_index.id},'
                    f'{sales_index.index}'.ljust(ROW_LEN)
                )
                sales_index_file.write(string_index_model + '\n')

        car_row_number: int = 0
        for car_index in self.cars_index:
            if car_index.id == sale.car_vin:
                car_row_number = int(car_index.index)

        with open(
            self.__make_path(CARS_FILE), 'r+'
        ) as cars_file:
            cars_file.seek(car_row_number * OVER_ROW_LEN)
            row_value: str = cars_file.read(ROW_LEN)
            car_row_line: list = row_value.strip().split(',')
            cars_file.seek(car_row_number * ROW_LEN)
            format_string = row_value.replace(
                car_row_line[4], CarStatus.sold).ljust(ROW_LEN)
            cars_file.write(format_string)

        return Car(
            vin=car_row_line[0], model=car_row_line[1],
            price=car_row_line[2], date_start=car_row_line[3],
            status=CarStatus.sold
        )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        with open(
            self.__make_path(CARS_FILE), 'r'
        ) as cars_file:
            cars_line: list[str] = cars_file.readlines()
            split_lines = list(
                map(lambda line: line.strip().split(','), cars_line)
            )
            return list(
                Car(
                    vin=line[0],
                    model=int(line[1]),
                    price=Decimal(line[2]),
                    date_start=datetime.strptime(line[3], "%Y-%m-%d %H:%M:%S"),
                    status=CarStatus(line[4])
                )
                for line in split_lines if line[4] == status
            )

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        num_model_row: int = 0
        num_sale_row: int = 0

        if not self.cars_index:
            self.cars_index = IndexCasher.cash(
                self.__make_path(CARS_INDEX_FILE)
            )

        if not self.sales_index:
            self.sales_index = IndexCasher.cash(
                self.__make_path(SALES_INDEX_FILE)
            )

        if not self.models_index:
            self.models_index = IndexCasher.cash(
                self.__make_path(MODELS_INDEX_FILE)
            )

        car_index_dict = dict(
            map(
                lambda car_index: (car_index.id, car_index.index),
                self.cars_index
            )
        )

        if vin not in car_index_dict.keys():
            return None

        num_car_row = car_index_dict.get(vin)
        assert isinstance(num_car_row, str)

        with open(
            self.__make_path(CARS_FILE), 'r'
        ) as cars_file:
            cars_file.seek(int(num_car_row) * OVER_ROW_LEN)
            car_row_value: str = cars_file.read(ROW_LEN)
            car_value: list = car_row_value.strip().split(',')

        for model_index in self.models_index:
            if model_index.id != car_value[1]:
                continue
            num_model_row = int(model_index.index)

        with open(
            self.__make_path(MODELS_FILE), 'r'
        ) as models_file:
            models_file.seek(int(num_model_row) * OVER_ROW_LEN)
            model_row_value: str = models_file.read(ROW_LEN)
            model_value: list = model_row_value.strip().split(',')

        for sale_index in self.sales_index:
            if sale_index.id != car_value[0]:
                continue
            num_sale_row = int(sale_index.index)

        if os.path.exists(self.__make_path(SALES_FILE)):
            with open(
                self.__make_path(SALES_FILE), 'r'
            ) as sales_file:
                sales_file.seek(int(num_sale_row) * OVER_ROW_LEN)
                sale_row_value: str = sales_file.read(ROW_LEN)
                sale_value: list = sale_row_value.strip().split(',')

        car_info: dict = dict(
            vin=car_value[0],
            car_model_name=model_value[1],
            car_model_brand=model_value[2],
            price=car_value[2],
            date_start=car_value[3],
            status=car_value[4],
            sales_date=(
                sale_value[2] if car_value[4] == CarStatus.sold else None
            ),
            sales_cost=(
                sale_value[3] if car_value[4] == CarStatus.sold else None
            )
        )
        return CarFullInfo(**car_info)

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        if not self.cars_index:
            self.cars_index = IndexCasher.cash(
                self.__make_path(CARS_INDEX_FILE)
            )

        car_index_dict = dict(
            map(
                lambda car_index: (car_index.id, car_index.index),
                self.cars_index
            )
        )
        cars_index = list(
            map(
                lambda car_index: Index(
                    id=new_vin, index=car_index.index
                ) if car_index.id == vin else car_index, self.cars_index
            )
        )
        self.cars_index = cars_index
        self.cars_index.sort(key=lambda x: x.id)

        with open(
            self.__make_path(CARS_INDEX_FILE), 'w'
        ) as cars_index_file:
            for car_index in cars_index:
                cars_index_file.write(
                    f'{car_index.id},{car_index.index}'.ljust(ROW_LEN))

        num_car_row = car_index_dict.get(vin)
        assert isinstance(num_car_row, str)

        with open(
            self.__make_path(CARS_FILE), 'r+'
        ) as cars_file:
            cars_file.seek(int(num_car_row) * OVER_ROW_LEN)
            row_value: str = cars_file.read(ROW_LEN)
            car_row_line: list = row_value.strip().split(',')
            cars_file.seek(int(num_car_row))
            cars_file.write(
                row_value.replace(
                    car_row_line[0], new_vin
                ).ljust(ROW_LEN))
        return Car(
            vin=new_vin,
            model=car_row_line[1],
            price=car_row_line[2],
            date_start=car_row_line[3],
            status=car_row_line[4]
        )

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        car_vin = None
        with open(
            self.__make_path(SALES_FILE), 'r'
        ) as sales_read_file:
            file_value: list = sales_read_file.readlines()
        with open(
            self.__make_path(SALES_FILE), 'w'
        ) as sales_write_file:
            for value in file_value:
                if sales_number not in value:
                    sales_write_file.write(value)
                else:
                    car_vin = value.strip().split(',')[1]

        with open(
            self.__make_path(SALES_INDEX_FILE), 'r'
        ) as sales_index_read_file:
            index_file_value: list = sales_index_read_file.readlines()
        with open(
            self.__make_path(SALES_INDEX_FILE), 'w'
        ) as sales_index_write_file:
            for value in index_file_value:
                if car_vin not in value:
                    sales_index_write_file.write(value)

        if not self.cars_index:
            self.cars_index = IndexCasher.cash(
                self.__make_path(CARS_INDEX_FILE))

        car_index_dict = dict(
            map(
                lambda car_index: (car_index.id, car_index.index),
                self.cars_index
            )
        )
        assert isinstance(car_vin, str)
        num_car_row = car_index_dict.get(car_vin)
        assert isinstance(num_car_row, str)

        with open(
            self.__make_path(CARS_FILE), 'r+'
        ) as cars_file:
            cars_file.seek(int(num_car_row) * OVER_ROW_LEN)
            car_row_value: str = cars_file.read(ROW_LEN)
            car_value: list = car_row_value.strip().split(',')
            cars_file.seek(int(num_car_row) * OVER_ROW_LEN)
            cars_file.write(
                car_row_value.replace(
                    car_value[4], CarStatus.available
                ).ljust(ROW_LEN))
        return Car(
            vin=car_value[0],
            model=car_value[1],
            price=car_value[2],
            date_start=car_value[3],
            status=car_value[4]
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        with open(
            self.__make_path(SALES_FILE), 'r'
        ) as sales_read_file:
            file_value: list = sales_read_file.readlines()

        sales_history = dict()
        for value in file_value:
            value_item: list = value.strip().split(',')
            sales_history[value_item[1]] = value_item[3]

        if not self.cars_index:
            self.cars_index = IndexCasher.cash(
                self.__make_path(CARS_INDEX_FILE)
            )

        cars_row: list = list(
            int(car_index.index)
            for car_index in self.cars_index
            if car_index.id in sales_history.keys()
        )
        with open(
            self.__make_path(CARS_FILE), 'r'
        ) as cars_read_file:
            salon_cars: dict = {
                row_value.strip().split(',')[0]:
                row_value.strip().split(',')[1]
                for row_number, row_value in enumerate(
                    cars_read_file.readlines()
                )
                if row_number in cars_row and row_value != '\n'
            }

        if not self.models_index:
            self.models_index = IndexCasher.cash(
                self.__make_path(MODELS_INDEX_FILE)
            )
        models_row: list = list(
            model_index.index
            for model_index in self.models_index
            if model_index.id in salon_cars.values()
        )
        with open(
            self.__make_path(MODELS_FILE), 'r'
        ) as models_read_file:
            salon_models: dict = {
                row_value.strip().split(',')[0]: [
                    row_value.strip().split(',')[1],
                    row_value.strip().split(',')[2]
                ]
                for row_number, row_value in enumerate(models_read_file)
                if str(row_number) in models_row
            }

        resume_table: list = []
        for car_vin, car_models in salon_cars.items():
            brand_model = salon_models.get(car_models)
            assert isinstance(brand_model, list)
            price = sales_history.get(car_vin)
            resume_table.append([brand_model[0], brand_model[1], price])
        list_total = []

        group_table: list = []
        for value in salon_models.values():
            count_item = sum(i[0] == value[0] and i[1] == value[1]
                             for i in resume_table)
            price = sum(float(i[2]) for i in resume_table if i[0]
                        == value[0] and i[1] == value[1])
            group_table.append([value[0], value[1], count_item, price])
        group_table = sorted(
            group_table, key=lambda x: (x[2], x[3]), reverse=True
            )[:3]
        for value in group_table:
            list_total.append(
                ModelSaleStats(
                    car_model_name=value[0],
                    brand=value[1],
                    sales_number=value[2]
                )
            )

        return list_total[:3]
