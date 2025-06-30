from tkinter import Tk, Label, Button
from PIL import Image, ImageTk
from pyfirmata import Arduino, util, INPUT, OUTPUT
from time import sleep
import random
import time
import threading

# Setup
port = 'COM8'
board = Arduino(port)

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

# Function to play BUZZER and light indicator LED
def play_tone_and_indicator(duration):
    board.digital[buzzer].write(1)
    board.digital[indicator_led].write(1)
    sleep(duration)
    board.digital[buzzer].write(0)
    board.digital[indicator_led].write(0)

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

# Function to blink all LEDs
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
def game_round():
    play_tone_and_indicator(1)
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

    board.digital[indicator_led].write(0)
    play_tone_and_indicator(0.5)

    computer_choice = random.choice(choices)
    update_computer_choice_leds(computer_choice)

    print("Player Choice: ", player_choice)
    print("Computer Choice: ", computer_choice)

    if not player_choice:
        return "Nothing", computer_choice, 2
    return player_choice, computer_choice, get_winner(player_choice, computer_choice)

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors Lizard Spock Game")
        
        self.player_label = Label(root, text="Player Choice")
        self.player_label.pack()
        self.player_image = Label(root)
        self.player_image.pack()

        self.computer_label = Label(root, text="Computer Choice")
        self.computer_label.pack()
        self.computer_image = Label(root)
        self.computer_image.pack()

        self.status_label = Label(root, text="Press Start to Begin")
        self.status_label.pack()

        self.start_button = Button(root, text="Start", command=self.start_game)
        self.start_button.pack()

        self.reset_button = Button(root, text="Reset", command=self.reset_game)
        self.reset_button.pack()

        # Load images using PIL and convert to ImageTk format
        self.player_images = {choice: ImageTk.PhotoImage(Image.open(f"{choice}.jpg")) for choice in choices}
        self.computer_images = {choice: ImageTk.PhotoImage(Image.open(f"{choice}.jpg")) for choice in choices}
        self.nothing_image = ImageTk.PhotoImage(Image.open("Nothing.jpg"))

        self.game_running = False

    def start_game(self):
        if not self.game_running:
            self.game_running = True
            threading.Thread(target=self.run_game).start()

    def reset_game(self):
        self.game_running = False
        blink_all_leds()
        self.status_label.config(text="Game Reset. Press Start to Begin")

    def update_images(self, player_choice, computer_choice):
        if player_choice == "Nothing":
            self.player_image.config(image=self.nothing_image)
        else:
            self.player_image.config(image=self.player_images[player_choice])

        self.computer_image.config(image=self.computer_images[computer_choice])
        self.status_label.config(text=f'Player: {player_choice}, Computer: {computer_choice}')

    def run_game(self):
        player_score = 0
        computer_score = 0

        self.status_label.config(text="Game Started")

        while not read_button(start_button):
            sleep(0.1)

        play_tone_and_indicator(1)

        for round in range(7):
            if not self.game_running:
                break

            player_choice, computer_choice, winner = game_round()
            self.update_images(player_choice, computer_choice)

            if winner == 1:
                player_score += 1
            elif winner == 2:
                computer_score += 1

            update_score_leds(player_score, human_score_leds)
            update_score_leds(computer_score, computer_score_leds)

            self.status_label.config(text=f'Round {round + 1}: Player Score: {player_score}, Computer Score: {computer_score}')

            play_tone_and_indicator(0.5)
            if read_button(start_button):
                self.status_label.config(text="Game terminated mid-way.")
                self.game_running = False
                return

            sleep(2)

        if player_score > computer_score:
            self.status_label.config(text='Player Wins')
        elif player_score == computer_score:
            self.status_label.config(text='The Game ended in a draw')
        else:
            self.status_label.config(text='The Computer Wins')

        play_tone_and_indicator(1)
        while not read_button(reset_button):
            sleep(0.1)

        blink_all_leds()
        self.game_running = False
        self.start_game()

if __name__ == '__main__':
    root = Tk()
    app = GameApp(root)
    root.mainloop()
