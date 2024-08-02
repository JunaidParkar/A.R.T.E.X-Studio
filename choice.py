import os
import msvcrt

def get_choice(choices):
    def print_choices(selected_index):
        for idx, choice in enumerate(choices):
            prefix = "> " if idx == selected_index else "  "
            print(f"{prefix}{choice}")

    selected_index = 0
    start_line = None

    while True:
        if start_line is None:
            start_line = os.get_terminal_size().lines - len(choices) - 1
        else:
            for _ in range(len(choices)):
                print("\033[F\033[K", end='')  # Move cursor up and clear the line
        
        print_choices(selected_index)
        
        key = msvcrt.getch()
        if key == b'\xe0':  # Arrow keys start with special character
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                if selected_index > 0:
                    selected_index -= 1
            elif key == b'P':  # Down arrow
                if selected_index < len(choices) - 1:
                    selected_index += 1
        elif key == b'\r':  # Enter key
            break

    for _ in range(len(choices)):
        print("\033[F\033[K", end='')  # Move cursor up and clear the line

    return choices[selected_index]

def main():
    choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
    selected_choice = get_choice(choices)
    print(f"You selected: {selected_choice}")
    choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
    selected_choice = get_choice(choices)
    print(f"You selected: {selected_choice}")