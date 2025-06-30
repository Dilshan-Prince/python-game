import pyfirmata
import time

# Set up the board and buzzer pin
board = pyfirmata.Arduino('COM8')  # Adjust for your port
it = pyfirmata.util.Iterator(board)
it.start()

buzzer_pin = 11  # Adjust for your buzzer pin
board.digital[buzzer_pin].mode = pyfirmata.OUTPUT

# Define note frequencies (Hz)
notes = {
    'C4': 261, 'D4': 294, 'E4': 329, 'F4': 349,
    'G4': 392, 'A4': 440, 'B4': 493, 'C5': 523
}

# Define song (Mary Had a Little Lamb)
song = [
    ('E4', 0.4), ('D4', 0.4), ('C4', 0.4), ('D4', 0.4),
    ('E4', 0.4), ('E4', 0.4), ('E4', 0.8),
    ('D4', 0.4), ('D4', 0.4), ('E4', 0.4), ('E4', 0.4),
    ('E4', 0.4), ('E4', 0.4), ('E4', 0.8),
    ('E4', 0.4), ('D4', 0.4), ('C4', 0.4), ('D4', 0.4),
    ('E4', 0.4), ('E4', 0.4), ('E4', 0.8),
    ('E4', 0.4), ('D4', 0.4), ('C4', 0.4), ('D4', 0.4),
    ('E4', 0.4), ('E4', 0.4), ('E4', 0.8)
]

def play_tone(pin, freq, duration):
    if freq == 0:
        board.digital[pin].write(0)
    else:
        board.digital[pin].write(1)
        time.sleep(duration / 2)  # Half the duration for each half-cycle
        board.digital[pin].write(0)
        time.sleep(duration / 2)
    
def play_song(song):
    for note, duration in song:
        freq = notes.get(note, 0)  # Get frequency of the note
        play_tone(buzzer_pin, freq, duration)
        time.sleep(0.1)  # Short pause between notes

if __name__ == "__main__":
    play_song(song)
    board.exit()
