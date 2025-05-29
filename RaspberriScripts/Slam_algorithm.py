#тут типо жоски слем алгоритме
import serial, sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ClientClasses.VisualizationProcessing import VisualizePaths

serial = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

#ты ему клетки со фрейма, а он тебе все остальное
class MainComputer(VisualizePaths):
    def __init__(self):
        pass
