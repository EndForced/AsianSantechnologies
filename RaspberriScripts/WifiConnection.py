#!/usr/bin/env python3

import subprocess
import time
import re


def check_wifi_connection(ssid):
    """Проверяет, подключены ли мы к указанной сети WiFi"""
    try:
        result = subprocess.run(['iwgetid'], capture_output=True, text=True)
        return ssid in result.stdout
    except:
        return False


def connect_to_wifi(ssid, password):
    """Пытается подключиться к указанной WiFi сети"""
    try:
        # Удаляем существующее соединение (если есть)
        subprocess.run(['nmcli', 'con', 'delete', ssid], stderr=subprocess.DEVNULL)

        # Пытаемся подключиться
        result = subprocess.run([
            'nmcli', 'device', 'wifi', 'connect', ssid,
            'password', password
        ], capture_output=True, text=True)

        return "successfully activated" in result.stdout
    except Exception as e:
        print(f"Ошибка при подключении: {e}")
        return False


def main():
    SSID = "Pro"
    PASSWORD = "87658765"
    CHECK_INTERVAL = 10  # Проверять каждые 10 секунд

    print(f"Скрипт подключения к WiFi '{SSID}' запущен")

    while True:
        if not check_wifi_connection(SSID):
            print(f"Не подключены к {SSID}. Пытаюсь подключиться...")
            if connect_to_wifi(SSID, PASSWORD):
                print(f"Успешно подключились к {SSID}")
            else:
                print(f"Не удалось подключиться к {SSID}. Повторная попытка через {CHECK_INTERVAL} сек.")
        else:
            print(f"Уже подключены к {SSID}. Проверка через {CHECK_INTERVAL} сек.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()