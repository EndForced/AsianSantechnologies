from enum import verify

import requests
import json

# URL сервера (адрес Flask-приложения из предыдущего примера)
url = 'http://192.168.43.221:5000/data'
mat = [[10, 10, 10, 10, 10, 10, 10, 10],
           [10, 10, 10, 10, 10, 10, 10, 10],
           [10, 10, 10, 0, 0, 0, 0, 0],
           [10, 10, 10, 0, 0, 0, 0, 0],
           [10, 10, 10, 0, 41, 20, 52, 0],
           [10, 10, 10, 0, 10, 31, 10, 0],
           [10, 10, 10, 0, 10, 10, 71, 0],
           [10, 10, 10, 0, 63, 63, 63, 0]]
# Данные для отправки (в формате словаря)
data_to_send = {
    'mat': str(mat),
}

# Отправляем POST-запрос
try:
    # Вариант 1: отправка JSON-данных
    response = requests.post(
        url,
        json=data_to_send,  # автоматически конвертирует в JSON и устанавливает Content-Type
        timeout=5, # таймаут на выполнение запроса (секунды)
        verify = False
    )

    # Вариант 2: можно отправить как form-data (раскомментировать если нужно)
    # response = requests.post(url, data=data_to_send)

    # Выводим результат
    print(f"Статус код: {response.status_code}")
    print("Ответ сервера:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")