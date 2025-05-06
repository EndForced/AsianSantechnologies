#!/usr/bin/env python3

import subprocess
import time


def get_current_wifi():
    """Возвращает SSID текущей WiFi сети или None если не подключен"""
    try:
        result = subprocess.run(['iwgetid', '-r'],
                                capture_output=True,
                                text=True,
                                timeout=5)
        return result.stdout.strip()
    except:
        return None


def connect_to_wifi(ssid, password):
    """Пытается подключиться к указанной WiFi сети"""
    try:
        # Проверяем, видна ли сеть
        scan_result = subprocess.run(['nmcli', 'dev', 'wifi', 'list'],
                                     capture_output=True,
                                     text=True,
                                     timeout=10)
        if ssid not in scan_result.stdout:
            print(f"Сеть {ssid} не найдена в доступных")
            return False

        # Удаляем существующее соединение (если есть)
        subprocess.run(['nmcli', 'con', 'delete', ssid],
                       stderr=subprocess.DEVNULL,
                       timeout=5)

        # Пытаемся подключиться
        result = subprocess.run([
            'nmcli', 'device', 'wifi', 'connect', ssid,
            'password', password
        ], capture_output=True, text=True, timeout=15)

        return "successfully activated" in result.stdout
    except subprocess.TimeoutExpired:
        print("Таймаут при попытке подключения")
        return False
    except Exception as e:
        print(f"Ошибка при подключении: {str(e)}")
        return False


def main():
    TARGET_SSID = "Pro"
    PASSWORD = "87658765"
    CHECK_INTERVAL = 30  # Проверять каждые 30 секунд

    print(f"Скрипт мониторинга WiFi подключения к '{TARGET_SSID}' запущен")

    while True:
        current_ssid = get_current_wifi()

        if current_ssid == TARGET_SSID:
            print(f"Уже подключены к целевой сети {TARGET_SSID}. Следующая проверка через {CHECK_INTERVAL} сек.")
        elif current_ssid:
            print(f"Подключены к другой сети ({current_ssid}). Не переподключаемся.")
        else:
            print(f"Не подключены ни к какой сети. Пытаюсь подключиться к {TARGET_SSID}...")
            if connect_to_wifi(TARGET_SSID, PASSWORD):
                print(f"Успешно подключились к {TARGET_SSID}")
            else:
                print(f"Не удалось подключиться к {TARGET_SSID}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()