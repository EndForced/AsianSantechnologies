import subprocess

from wayProcessingOperations.BasicWaveOperations import possible_codes

networks = {"Pro":"87658765", "TP-Link_26A0":"96472569"}
favourite_network = "Pro"

def am_i_connected(nets):
    res = subprocess.run(["iwgetid","-r"], capture_output = True)
    res = res.stdout.strip()
    res = str(res).replace("ESSID:", "")
    res = res.replace(r'"', '')

    for i in nets.keys():
        if i in res:
            return i
        print("my net:", i)
    else:
        return False

def find_possible_networks(nets, find_favourite = 0):
    res = subprocess.run(
        "sudo iwlist wlan0 scan | grep ESSID",
        shell=True,
        check=True,
        text=True,
        capture_output=True
    )
    res = res.stdout.strip()
    res = str(res).replace("ESSID:", "")
    res = res.replace(r'"','')

    if find_favourite:
        if favourite_network in res:
            return True


    for key, val in nets.items():
        if key in res:
            return key

    return False

def connect_to_wifi(ssid, password):
    print("connecting to", ssid)
    # Создаём временный конфиг для wpa_supplicant
    config = f"""
    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """

    # Записываем конфиг во временный файл
    with open("/tmp/wpa_temp.conf", "w") as f:
        f.write(config)

    try:
        # Останавливаем текущий wpa_supplicant (если нужно)
        subprocess.run(["sudo", "killall", "wpa_supplicant"], check=False)

        # Запускаем wpa_supplicant с новым конфигом
        result = subprocess.run(
            [
                "sudo",
                "wpa_supplicant",
                "-B",  # запуск в фоне
                "-i", "wlan0",
                "-c", "/tmp/wpa_temp.conf"
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Запрашиваем IP через DHCP
        subprocess.run(["sudo", "dhclient", "wlan0"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)

def main():
    net = am_i_connected(networks)

    if net == favourite_network:
        return

    elif net and net != favourite_network:
        if find_possible_networks(networks, find_favourite = 1):
            connect_to_wifi(favourite_network, networks[favourite_network])

    elif not net:
        possible_network = find_possible_networks(networks)
        connect_to_wifi(possible_network, networks[possible_network])





