from enum import Enum, auto, unique



class Sensors(Enum):
    Temp = 30
    Hum = 50
    husam = 3
    husam2 = 332
    husams = 334
    husasm = 32
    husadm = auto()


if __name__ == "__main__":
    print(Sensors)
    print(Sensors.Temp.name)
    print(Sensors.Hum.value)
for item in Sensors:
    print(item.name, "=", item.value, "\n")