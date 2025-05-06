import subprocess

networks = {"Pro":"87658765", "TP-Link_26A0":"96472569"}

res = subprocess.run(["iwgetid","-r"], capture_output = True)
res = res.stdout.strip()

if res in networks.keys():
    exit()
else:
    pass
res = subprocess.run(
    "sudo iwlist wlan0 scan | grep ESSID",
    shell=True,
    check=True,
    text=True,
    capture_output=True
)
res = res.stdout.strip()
print(type(res))

