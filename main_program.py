Python 3.12.0b4 (tags/v3.12.0b4:97a6a41, Jul 11 2023, 13:49:15) [MSC v.1935 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> from flask import Flask, request, jsonify
... from gpiozero import DigitalOutputDevice, PWMOutputDevice, RotaryEncoder
... import RPi.GPIO as GPIO
... from time import sleep
... import math
... import threading
... import atexit
... 
... app = Flask(__name__)
... 
... GPIO.setmode(GPIO.BCM)
... 
... # -------- WHEEL MOTORS --------
... MOTORS = {
...     "W1": (DigitalOutputDevice(5), DigitalOutputDevice(6)),
...     "W2": (DigitalOutputDevice(7), DigitalOutputDevice(1)),
...     "W3": (DigitalOutputDevice(20), DigitalOutputDevice(21))
... }
... 
... def motor(in1, in2, direction):
...     if direction == 1:
...         in1.on(); in2.off()
...     elif direction == -1:
...         in1.off(); in2.on()
...     else:
...         in1.off(); in2.off()
... 
... def stop_all():
...     for in1, in2 in MOTORS.values():
...         motor(in1, in2, 0)
... 
... # -------- MOTOR A --------
... ENA_A = PWMOutputDevice(22)
... IN1_A = DigitalOutputDevice(17)
... IN2_A = DigitalOutputDevice(27)
... encoder_A = RotaryEncoder(a=23, b=24, max_steps=0)
... 
CPR_motor = 28
gearbox_ratio = 300
counts_per_rev_A = CPR_motor * gearbox_ratio

wheel_diameter = 4.7
circumference = math.pi * wheel_diameter
counts_per_cm_A = counts_per_rev_A / circumference

# -------- MOTOR B --------
ENA_B = PWMOutputDevice(15)
IN1_B = DigitalOutputDevice(16)
IN2_B = DigitalOutputDevice(10)
encoder_B = RotaryEncoder(a=25, b=8, max_steps=0)

counts_per_rev_B = 28080
counts_per_cm_B = counts_per_rev_B / circumference

# -------- SERVOS --------
servo_pins = [12, 13, 18, 19]
servos = []

for pin in servo_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 50)
    pwm.start(0)
    servos.append(pwm)

def move_servo(index, angle):
    angle = max(0, min(180, angle))
    duty = 2 + (angle / 18)
    servos[index].ChangeDutyCycle(duty)
    sleep(0.4)
    servos[index].ChangeDutyCycle(0)

# -------- MOTOR FUNCTIONS --------
def move_motor_A(cm):
    encoder_A.steps = 0
    target = abs(int(cm * counts_per_cm_A))

    if cm > 0:
        IN1_A.on(); IN2_A.off()
    else:
        IN1_A.off(); IN2_A.on()

    ENA_A.value = 0.4

    while abs(encoder_A.steps) < target:
        sleep(0.001)

    ENA_A.value = 0

def move_motor_B(cm):
    encoder_B.steps = 0
    target = abs(int(cm * counts_per_cm_B))

    if cm > 0:
        IN1_B.on(); IN2_B.off()
    else:
        IN1_B.off(); IN2_B.on()

    ENA_B.value = 0.4

    while abs(encoder_B.steps) < target:
        sleep(0.001)

    ENA_B.value = 0

# -------- API ROUTES --------

@app.route("/control")
def control():
    cmd = request.args.get("cmd", "S")

    if cmd == "F":
        motor(*MOTORS["W2"], 0)
        motor(*MOTORS["W3"], 1)
        motor(*MOTORS["W1"], 1)
    elif cmd == "B":
        motor(*MOTORS["W2"], 0)
        motor(*MOTORS["W3"], -1)
        motor(*MOTORS["W1"], -1)
    elif cmd == "L":
        motor(*MOTORS["W1"], 1)
        motor(*MOTORS["W2"], 1)
        motor(*MOTORS["W3"], -1)
    elif cmd == "R":
        motor(*MOTORS["W1"], -1)
        motor(*MOTORS["W2"], -1)
        motor(*MOTORS["W3"], 1)
    else:
        stop_all()

    return "OK"

@app.route("/moveA")
def moveA():
    cm = float(request.args.get("cm", 0))
    threading.Thread(target=move_motor_A, args=(cm,)).start()
    return jsonify({"A": cm})

@app.route("/moveB")
def moveB():
    cm = float(request.args.get("cm", 0))
    threading.Thread(target=move_motor_B, args=(cm,)).start()
    return jsonify({"B": cm})

@app.route("/servo", methods=['POST'])
def servo():
    for i in range(4):
        val = request.form.get(f"m{i+1}")
        if val:
            move_servo(i, int(val))
    return "OK"

# CLEANUP
@atexit.register
def cleanup():
    stop_all()
    ENA_A.value = 0
    ENA_B.value = 0
    for s in servos:
        s.stop()
    GPIO.cleanup()

if __name__ == "__main__":
