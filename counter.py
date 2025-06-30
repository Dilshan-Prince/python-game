import pyfirmata
import time

# Set up the board and pins
board = pyfirmata.Arduino('COM8')  # Adjust for your port
it = pyfirmata.util.Iterator(board)
it.start()

led_pins = [2, 3, 4]  # LEDs connected to pins 5, 6, and 7
button_pin = 5  # Button connected to pin 2

# Initialize LEDs and button
for pin in led_pins:
    board.digital[pin].mode = pyfirmata.OUTPUT
button = board.analog[button_pin]
button.mode = pyfirmata.INPUT

def set_leds(value):
    binary = format(value, '03b')
    for i in range(3):
        # Adjust index mapping to new pin arrangement
        board.digital[led_pins[i]].write(int(binary[i]))
    print(f'Setting LEDs to: {binary}')  # Debug print

counter = 0
button_pressed = False

while True:
    button_state = button.read()
    print(f'Button state: {button_state}')  # Debug print
    if button_state is True and not button_pressed:
        counter = (counter + 1) % 8
        print(f'Counter: {counter}')  # Debug print
        set_leds(counter)
        button_pressed = True
    elif button_state is False:
        button_pressed = False
    time.sleep(0.1)

# Ensure you clean up properly
board.exit()

'''
2 to the power 0 is connected to digital pin 5
2^1 = digital pin 6
2^2= digital pin 7
'''