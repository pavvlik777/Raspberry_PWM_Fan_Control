import OPi.GPIO as GPIO  # GPIO pins
import time
import threading
import subprocess  # To get the CPU temperature



class Pwm(threading.Thread):
    def __init__(self, gpioPin, frequency):
        self.baseTime = 1.0 / frequency
        self.maxCycle = 100.0
        self.sliceTime = self.baseTime / self.maxCycle
        self.gpioPin = gpioPin
        self.terminated = False
        self.toTerminate = False


    def start(self, dutyCycle):
        self.dutyCycle = dutyCycle
        GPIO.setup(control_pin, GPIO.OUT)
        self.thread = threading.Thread(None, self.__run, None, (), {})
        self.thread.start()

    def changeDutyCycle(self, dutyCycle):
        self.dutyCycle = dutyCycle

    def changeFrequency(self, frequency):
        self.baseTime = 1.0 / frequency
        self.sliceTime = self.baseTime / self.maxCycle

    def stop(self):
        self.toTerminate = True
        while self.terminated == False:
            time.sleep(0.01)

        GPIO.output(control_pin, 0)


    def __run(self):
        while self.toTerminate == False:
            if self.dutyCycle > 0:
                GPIO.output(control_pin, 1)
                time.sleep(self.dutyCycle * self.sliceTime)

            if self.dutyCycle < self.maxCycle:
                GPIO.output(control_pin, 0)
                time.sleep((self.maxCycle - self.dutyCycle) * self.sliceTime)

        self.terminated = True



# pin number = (position of letter in alphabet - 1) * 32 + pin number
# So, PD14 will be (4 - 1) * 32 + 14 = 110
# Orange Pi 3 LTS physical board pin to GPIO pin
BOARD = {
    3:  122,    # PD26/TWI0-SDA/TS3-D0/UART3-CTS/JTAG-DI
    5:  121,    # PD25/TWI0-SCK/TS3-DVLD/UART3-RTS/JTAG-DO
    7:  118,    # PD22/PWM0/TS3-CLK/UART2-CTS
    8:  354,    # PL2/S-UART-TX
    10: 355,    # PL3/S-UART-RX
    11: 120,    # PD24/TWI2-SDA/TS3-SYNC/UART3-RX/JTAG-CK
    12: 114,    # PD18/LCD0-CLK/TS2-ERR/DMIC-DATA3
    13: 119,    # PD23/TWI2-SCK/TS3-ERR/UART3-TX/JTAG-MS
    15: 362,    # PL10/S-OWC/S-PWM1
    16: 111,    # PD15/LCD0-D21/TS1-DVLD/DMIC-DATA0/CSI-D9
    18: 112,    # PD16/LCD0-D22/TS1-D0/DMIC-DATA1
    19: 229,    # PH5/SPI1-MOSI/SPDIF-MCLK/TWI1-SCK/SIM1-RST
    21: 230,    # PH6/SPI1-MISO/SPDIF-IN/TWI1-SDA/SIM1-DET
    22: 117,    # PD21/LCD0-VSYNC/TS2-D0/UART2-RTS
    23: 228,    # PH4/SPI1-CLK/PCM0-MCLK/H-PCM0-MCLK/SIM1-DATA
    24: 227,    # PH3/SPI1-CS/PCM0-DIN/H-PCM0-DIN/SIM1-CLK
    26: 360     # PL8/S-PWM0
}

control_pin = 8  # PL2
frequency = 100  # Set 100Hz frequency

GPIO.setwarnings(False)
GPIO.setmode(BOARD)            # BOARD pin numbers
GPIO.setup(control_pin, GPIO.OUT)
#fan = Pwm(control_pin, 100)           # Set 100Hz frequency
#fan.start(0)                   # Fan off

#minTemp = 25
#maxTemp = 70
minSpeed = 0
maxSpeed = 100
temperature_file = '/sys/devices/virtual/thermal/thermal_zone0/temp'

baseTime = 1.0 / frequency
sliceTime = baseTime / maxSpeed


def get_temp():
    output = subprocess.run(['cat', temperature_file], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str) / 1000
    except (IndexError, ValueError):
        raise RuntimeError('Could not get temperature')
    
def get_speed_by_temp(temp):
    result_speed = int(0.03 * temp * temp - 0.74 * temp + 3.51)
    if result_speed < minSpeed:
        result_speed = minSpeed
    elif result_speed > maxSpeed:
        result_speed = maxSpeed

    return result_speed


while 1:
    temp = get_temp()
    speed = get_speed_by_temp(temp)

    time_passed = 0
    while time_passed < 5:
        if speed > 0:
            GPIO.output(control_pin, 1)
            time.sleep(speed * sliceTime)
            time_passed += speed * sliceTime

        if speed < maxSpeed:
            GPIO.output(control_pin, 0)
            time.sleep((maxSpeed - speed) * sliceTime)
            time_passed += (maxSpeed - speed) * sliceTime