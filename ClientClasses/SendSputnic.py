from enum import verify

import requests
import json

# URL сервера (адрес Flask-приложения из предыдущего примера)
url = 'http://192.168.254.221:5000/data'
mat = [[41, 20, 20, 10, 20, 10, 10, 62], [10, 10, 20, 33, 20, 10, 10, 62], [10, 10, 31, 31, 20, 10, 10, 62],
       [10, 10, 33, 33, 20, 10, 10, 42], [10, 10, 20, 20, 20, 10, 20, 34], [10, 32, 20, 10, 10, 10, 10, 10],
       [10, 10, 10, 10, 10, 20, 20, 10], [71, 10, 32, 20, 52, 20, 20, 20]]

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