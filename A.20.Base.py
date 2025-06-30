from pyfirmata import Arduino, util, INPUT, OUTPUT, ANALOG
from time import sleep
import random
import time

# Setup
board = Arduino('COM8')

# Constants for game
choices = ["Rock", "Paper", "Scissors", "Lizard", "Spock"]
choice_buttons = [0, 1, 2, 3, 4]
start_button = 5
indicator_led = 12
reset_button = 5

# Score LEDs
human_score_leds = [2, 3, 4]  # 2^0, 2^1, 2^2
computer_score_leds = [7, 6, 5]  # 2^0, 2^1, 2^2

# Computer choice LEDs
computer_choice_leds = {
    "Rock": [10],
    "Paper": [9],
    "Scissors": [8],
    "Lizard": [9, 10],
    "Spock": [8, 9]
}

# Buzzer pin
buzzer = 11

# Voltage threshold (2.5V out of 5V)
VOLTAGE_THRESHOLD = 2.5 / 5.0

# Initialize iterator for analog inputs
it = util.Iterator(board)
it.start()

# Set up buttons to INPUT
for button in choice_buttons + [start_button, reset_button]:
    board.analog[button].mode = INPUT
    board.analog[button].enable_reporting()

# Set up indicator LED to OUTPUT
board.digital[indicator_led].mode = OUTPUT

# Set up other LED modes to OUTPUT
for led in human_score_leds + computer_score_leds:
    board.digital[led].mode = OUTPUT
for leds in computer_choice_leds.values():
    for led in leds:
        board.digital[led].mode = OUTPUT
board.digital[buzzer].mode = OUTPUT

# Function to play BUZZER
def play_tone(duration):
    board.digital[buzzer].write(1)
    sleep(duration)
    board.digital[buzzer].write(0)

# Function to get analog input from buttons and check against voltage threshold
def read_button(button):
    voltage = board.analog[button].read()
    return voltage > VOLTAGE_THRESHOLD if voltage is not None else False

# Function to blink LEDs according to score
def update_score_leds(score, leds):
    bin_score = bin(score).replace("0b", "").rjust(3, '0')

    for i, state in enumerate(bin_score):
        board.digital[leds[i]].write(int(state))

# Function to update computer choice LEDs
def update_computer_choice_leds(choice):
    for leds in computer_choice_leds.values():
        for led in leds:
            board.digital[led].write(0)
    for led in computer_choice_leds[choice]:
        board.digital[led].write(1)

# Function to blink all LEDs (While Resetting)
def blink_all_leds():
    all_leds = human_score_leds + computer_score_leds + [led for leds in computer_choice_leds.values() for led in leds]
    for _ in range(3):
        for led in all_leds:
            board.digital[led].write(1)
        sleep(0.5)
        for led in all_leds:
            board.digital[led].write(0)
        sleep(0.5)

# Function to determine winner
def get_winner(player_choice, computer_choice):
    wins = {
        'Rock': ['Scissors', 'Lizard'],
        'Paper': ['Rock', 'Spock'],
        'Scissors': ['Paper', 'Lizard'],
        'Lizard': ['Spock', 'Paper'],
        'Spock': ['Scissors', 'Rock']
    }
    if player_choice == computer_choice:
        return 0  #Draw
    elif computer_choice in wins[player_choice]:
        return 1  #Player Wins
    else:
        return 2  #Computer Wins

# Function to get player choice and computer choice
def game_round(round_num):
    # Start buzzer and indicator LED at the same time
    board.digital[indicator_led].write(1)
    play_tone(2)
    
    start_time = time.time()
    player_choice = None
    
    while time.time() - start_time < 3:
        for i, button in enumerate(choice_buttons):
            if read_button(button):
                player_choice = choices[i]
                board.digital[indicator_led].write(0)
                break
        if player_choice:
            break

    if not player_choice:
        board.digital[indicator_led].write(0)

    computer_choice = random.choice(choices)
    update_computer_choice_leds(computer_choice)

    print(f"\nRound {round_num + 1}")
    print("Player Choice:", player_choice)
    print("Computer Choice:", computer_choice)

    if not player_choice:
        return None, computer_choice, 2
    return player_choice, computer_choice, get_winner(player_choice, computer_choice)

# Main game function
def main_game():
    player_score = 0
    computer_score = 0

    print("Press the start button to begin the game.")
    while not read_button(start_button):
        sleep(0.1)

    play_tone(1)

    for round_num in range(7):
        if round_num == 0:
            time.sleep(1)  # Initial delay before the first round
        if read_button(start_button):
            print("Game terminated by start button.")
            return
        player_choice, computer_choice, winner = game_round(round_num)
        if winner == 1:
            player_score += 1
        elif winner == 2:
            computer_score += 1

        update_score_leds(player_score, human_score_leds)
        update_score_leds(computer_score, computer_score_leds)

        print("Player Score:", player_score)
        print("Computer Score:", computer_score)
        print("\n")  # One blank lines between rounds

        # Delay between rounds
        for _ in range(7):  # 7 iterations of 1 second delay
            if read_button(start_button):
                print("Game terminated by start button.")
                return
            sleep(1)

    if player_score > computer_score:
        print('Player Wins')
    elif player_score == computer_score:
        print('The Game ended in a draw')
    else:
        print('The Computer Wins')

    # Final buzzer tone
    play_tone(3)

    # Wait for reset button press
    print("Press the reset button to restart the game.")
    while not read_button(reset_button):
        sleep(0.1)

    # Blink all LEDs for 3 seconds
    blink_all_leds()
    main_game()  # Restart the game

if __name__ == "__main__":
    main_game()
