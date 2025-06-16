import requests
import json

# URL сервера (адрес Flask-приложения из предыдущего примера)
url = 'http://localhost:5000/data'
mat = [[10]]
# Данные для отправки (в формате словаря)
data_to_send = {
    'name': mat,
}

# Отправляем POST-запрос
try:
    # Вариант 1: отправка JSON-данных
    response = requests.post(
        url,
        json=data_to_send,  # автоматически конвертирует в JSON и устанавливает Content-Type
        timeout=5  # таймаут на выполнение запроса (секунды)
    )

    # Вариант 2: можно отправить как form-data (раскомментировать если нужно)
    # response = requests.post(url, data=data_to_send)

    # Выводим результат
    print(f"Статус код: {response.status_code}")
    print("Ответ сервера:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")