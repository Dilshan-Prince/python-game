import pyfirmata
import time

# Specify the port where your Arduino is connected
board = pyfirmata.Arduino('COM8')

# Define the digital pins where LEDs are connected
led_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]

# Start an iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Set all LED pins as OUTPUT
for pin in led_pins:
    board.digital[pin].mode = pyfirmata.OUTPUT

# Blink LEDs continuously
try:
    while True:
        # Turn all LEDs on
        for pin in led_pins:
            board.digital[pin].write(1)
        time.sleep(1)
        
        # Turn all LEDs off
        for pin in led_pins:
            board.digital[pin].write(0)
        time.sleep(1)
except KeyboardInterrupt:
    # Turn off all LEDs when exiting
    for pin in led_pins:
        board.digital[pin].write(0)
    board.exit()
    print("Program stopped")
