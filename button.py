from pyfirmata import Arduino, util
import time

# Replace 'COM8' with your port if different
board = Arduino('COM8')

it = util.Iterator(board)
it.start()

# Enable reporting for analog pin A1
analog_pin = board.get_pin('a:0:i')

while True:
    # Read the value from the analog pin
    voltage = analog_pin.read()

    # Check if a value is read (might return None if no data is available)
    if voltage is not None:
        # The read value is between 0 and 1, multiply by 5 for voltage in Volts
        voltage = voltage * 5
        print(f'Voltage on Pin: {voltage:.2f} V')

    time.sleep(1)  # Read every second
