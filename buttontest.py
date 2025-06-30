import pyfirmata
import time

# Set up the Arduino board
board = pyfirmata.Arduino('COM8')

# Start an iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Define the pin for the analog input
analog_input = board.get_pin('a:0:i')

# Allow some time for the board to set up
time.sleep(1)

try:
    while True:
        # Read the value from the analog pin (0.0 to 1.0)
        analog_value = analog_input.read()
        
        # Convert the analog value to voltage (assuming 5V reference)
        if analog_value is not None:
            voltage = analog_value * 5.0
            print(f"Voltage at Pin: {voltage:.2f} V")
        
        time.sleep(0.5)  # Delay for readability
except KeyboardInterrupt:
    # Clean up when exiting the program
    board.exit()
    print("Exiting...")
