import pyfirmata
import time
import random

# Set up the board
board = pyfirmata.Arduino('COM3')  # Change the port as needed

# Start an iterator to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Define the pins for player choices (using analog pin A5)
player_pin = board.get_pin('a:5:i')

# Define the thresholds for each button on the analog pin
thresholds = {
    'rock': (0, 200),
    'paper': (201, 400),
    'scissors': (401, 600),
    'lizard': (601, 800),
    'spock': (801, 1023)
}

# Define the pins for computer choices (using digital pins)
computer_leds = {
    'rock': board.get_pin('d:2:o'),
    'paper': board.get_pin('d:3:o'),
    'scissors': board.get_pin('d:4:o'),
    'lizard': board.get_pin('d:5:o'),
    'spock': board.get_pin('d:6:o')
}

# Define the pins for round display (using specified digital pins)
round_leds = [
    board.get_pin('d:10:o'),  # Round display LED for 2^0
    board.get_pin('d:11:o'),  # Round display LED for 2^1
    board.get_pin('d:12:o')   # Round display LED for 2^2
]

# Function to reset all LEDs except for the current round's computer choice LED and round LEDs
def reset_leds(keep_choice=None):
    for choice, led in computer_leds.items():
        if choice != keep_choice:
            led.write(0)

# Function to display the current round using LEDs
def display_round(round_number):
    binary_representation = bin(round_number)[2:].zfill(3)  # 3 bits for 3 LEDs
    for i, bit in enumerate(binary_representation):
        round_leds[i].write(int(bit))

# Function to choose a random option for the computer
def computer_choice():
    reset_leds()  # Reset all LEDs before making a new choice
    choice = random.choice(list(computer_leds.keys()))
    computer_leds[choice].write(1)
    return choice

# Rules for the game
rules = {
    'rock': ['scissors', 'lizard'],
    'paper': ['rock', 'spock'],
    'scissors': ['paper', 'lizard'],
    'lizard': ['paper', 'spock'],
    'spock': ['rock', 'scissors']
}

# Function to determine the winner
def determine_winner(player, computer):
    if player == computer:
        return 'tie'
    elif computer in rules[player]:
        return 'player'
    else:
        return 'computer'

# Initial reset
reset_leds()

# Main game loop
player_score = 0
computer_score = 0
round_number = 1

print("Press the start button to begin the game!")

while True:
    if player_pin.read():
        while round_number <= 7:
            print(f"\nRound {round_number}")
            print(f"Please select your choice for round {round_number}:")

            # Wait for player input
            player_choice = None
            while player_choice is None:
                analog_value = player_pin.read()
                if analog_value is not None:
                    analog_value = analog_value * 1023  # Scale the analog value
                    for choice, (low, high) in thresholds.items():
                        if low <= analog_value <= high:
                            player_choice = choice
                            break

            print(f"Player chose {player_choice}")

            # Generate computer choice
            computer_choice_name = computer_choice()
            print(f"Computer chose {computer_choice_name}")

            # Determine the winner
            winner = determine_winner(player_choice, computer_choice_name)
            if winner == 'player':
                player_score += 1
                print("Player wins this round!")
            elif winner == 'computer':
                computer_score += 1
                print("Computer wins this round!")
            else:
                print("It's a tie!")

            # Update the score
            print(f"Score - Player: {player_score}, Computer: {computer_score}")

            # Display the round number using LEDs
            display_round(round_number)

            # Increment round number
            round_number += 1

            # Wait before the next round and keep the LEDs lit
            time.sleep(2)

        # End of game
        print("Game Over!")
        print(f"Final Score - Player: {player_score}, Computer: {computer_score}")

        # Reset all LEDs at the end of the game
        reset_leds()
        for led in round_leds:
            led.write(0)
        break
    time.sleep(0.1)