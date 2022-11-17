import RPi.GPIO as IO          # GPIO pins
import time
import subprocess              # To get the CPU temperature

IO.setwarnings(False)
IO.setmode(IO.BCM)            # BCM pin numbers
IO.setup(14, IO.OUT)            # GPIO14
fan = IO.PWM(14,100)           # Set 100Hz frequency
fan.start(0)                   # Fan off

# minTemp = 25
# maxTemp = 70
minSpeed = 0
maxSpeed = 100

def get_temp():
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
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
    fan.ChangeDutyCycle(speed)
    time.sleep(5)