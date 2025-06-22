import random
import time
import requests
from datetime import datetime

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="MedicineCallGenerator")

reasons = {
    "Остановка сердца": "critical",
    "Инфаркт миокарда": "critical",
    "Инсульт": "critical",
    "Тяжёлое кровотечение": "critical",
    "Ожоги 3 степени": "critical",
    "ДТП с травмами": "critical",
    "Потеря сознания": "critical",
    "Сильные судороги": "critical",
    "Падение с высоты": "critical",
    "Острая дыхательная недостаточность": "critical",
    "Травма головы": "critical",
    "Ранение ножом": "critical",
    "Передозировка наркотиками": "critical",
    "Асфиксия": "critical",
    "Аллергический шок": "critical",
    "Сильное отравление": "critical",
    "Открытый перелом": "critical",
    "Декомпенсация сахарного диабета": "important",
    "Гипертонический криз": "important",
    "Тахикардия": "important",
    "Астматический приступ": "important",
    "Высокая температура у ребёнка": "important",
    "Сильная рвота и понос": "important",
    "Обморок": "important",
    "Укус животного": "important",
    "Инфекция мочевых путей": "important",
    "Травма при падении": "important",
    "Сильная головная боль": "important",
    "Подозрение на аппендицит": "important",
    "Нарушение речи": "important",
    "Тревожность и паническая атака": "common",
    "Головокружение": "common",
    "Боль в спине": "common",
    "Простуда": "common",
    "Боль в горле": "common",
    "Температура 37.5": "common",
    "Менструальные боли": "common",
    "Нарушение сна": "common",
    "Повышенное давление без симптомов": "common",
    "Обычная головная боль": "common",
    "Заложенность носа": "common",
    "Лёгкий ушиб": "common",
    "Ссадины и царапины": "common",
    "Одиночество (психосоматическое)": "common",
    "Забытые лекарства": "common",
    "Бессонница": "common",
    "Нарушение пищеварения": "common",
    "Тошнота без рвоты": "common",
    "Лёгкий озноб": "common"
}

patient_id_min = 4
patient_id_max = 21


def generate_address_and_coordinates():
    while True:
        time.sleep(1)

        lat_min, lat_max = 59.75, 60.05
        lon_min, lon_max = 29.8, 30.6

        random_lat = random.uniform(lat_min, lat_max)
        random_lon = random.uniform(lon_min, lon_max)

        try:
            location = geolocator.reverse((random_lat, random_lon), language="ru")
            if not location:
                continue

            print(location)
            address = location.raw.get("address", {})
            street = address.get("road") or address.get("street")
            house = address.get("house_number")

            if street and house:
                addr = location.address.split(", ")
                result_addr = ", ".join([addr[1], addr[0]])
                result = {"lat": random_lat,
                          "lon": random_lon,
                          "address": result_addr}
                print(result)
                return result
        except Exception as e:
            print("Error: ", e)
            break


def send_call():
    data = generate_address_and_coordinates()
    if not data:
        print("Не удалось получить адрес.")
        return

    reason = random.choice(list(reasons.keys()))
    call_type = reasons[reason]
    date_time = datetime.now().isoformat()

    payload = {
        "reason": reason,
        "address": data["address"],
        "date_time": date_time,
        "lat": round(data["lat"], 6),
        "lon": round(data["lon"], 6),
        "status": "new",
        "type": call_type,
        "patient_id": random.randint(patient_id_min, patient_id_max),
        "team_id": None
    }

    try:
        response = requests.post("https://127.0.0.1:8000/api/calls/", json=payload, verify=False)
        print("Ответ сервера:", response.status_code)
        print("Данные запроса:", payload)
    except Exception as e:
        print("Ошибка при отправке POST-запроса:", e)


while True:
    command = input("gen - Генерация вызова\n"
                    "exit - Завершить работу\n"
                    "Введите команду: ")
    match command:
        case "gen":
            send_call()
        case "exit":
            break
        case _:
            print("Неизвестная команда")
