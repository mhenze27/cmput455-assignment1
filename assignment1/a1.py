# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification and game rules on Canvas

import ast
import random

from sys import stderr
from typing import List, Dict, Callable

def not_yet() -> bool:
    raise NotImplementedError("Command not implemented.")
    return False

def print_error(error: str) -> None:
    print(error, file = stderr)

class HeapGo:
    def __init__(self, komi: float, game_state: List) -> None:
        self.komi = komi
        self.game_state = game_state
        self.w_score = komi
        self.b_score = 0
        self.player = "b"
        self.num_heaps = 0

    def get_komi(self) -> float:
        return self.komi

    def get_game_state(self) -> List:
        return self.game_state

    def set_game_state(self, game_state: List) -> None:
        self.game_state = game_state

    def get_b_score(self) -> float:
        return self.b_score

    def set_b_score(self, score) -> None:
        self.b_score = score

    def get_w_score(self) -> float:
        return self.w_score

    def set_w_score(self, score) -> None:
        self.w_score = score

    def get_player(self) -> str:
        return self.player

    def set_player(self, player:str) -> None:
        self.player = player

    def get_num_heaps(self) -> int:
        return self.num_heaps

    def set_num_heaps(self, num_heaps) -> None:
        self.num_heaps = num_heaps

CommandMap = Dict[str, Callable[[str], bool]]

class CommandInterface:
    def __init__(self) -> None:
        # you can add your own initialisation here
        self.commands: CommandMap = {
            "help": self.cmd_help,
            "heapgo": self.cmd_heapgo,
            "show": self.cmd_show,
            "toplay": self.cmd_toplay,
            "play": self.cmd_play,
            "legal": self.cmd_legal,
            "genmove": self.cmd_genmove,
            "score": self.cmd_score,
            "winner": self.cmd_winner,
            }

        self.game = None

#============================================================================
# You need to implement the following methods.
#============================================================================
    def cmd_heapgo(self, args: str) -> bool:
        # Get the komi and game string from args
        marker = 0
        for char in args:
            if char == "[":
                break
            marker += 1

        try:
            komi = float(args[:marker].strip())
        except ValueError:
            return False
        game_str = args[marker:].strip()
        game_str = ast.literal_eval(game_str)

        # Check against restrictions
        # 1. The number of heaps is between 1 and 10 (inclusive)
        if len(game_str) > 10 or len(game_str) < 1:
            return False

        # 2. Each heap contains from 1 to 10 tokens (inclusive)
        for heap in game_str:
            if len(heap) > 10 or len(heap) < 1:
                return False

        # 3. Each token (c, n) has color c, either 'b' or 'w', and value n, an integer between 1 and 20 (inclusive).
        for heap in game_str:
            for token in heap:
                if token[0] not in ("b", "w"):
                    return False
                if not isinstance(token[1], int):
                    return False
                if token[1] < 1 or token[1] > 20:
                    return False
                if len(token) != 2:
                    return False

        # 4. The komi is an integer + 0.5 to avoid draws. Initialise Black's score to 0, and White's score to the komi. Range: -100 < komi < +100
        if komi > 99.5 or komi < -99.5:
            return False
        # Source: https://stackoverflow.com/a/54027361
        if  not (abs(komi) - 0.5) % 1 == 0: # Make sure komi ends with 0.5
            return False
        
        # If all checks passed return True

        # Instantiate a game instance
        self.game = HeapGo(komi, game_state=game_str)

        # Set the number of heaps
        self.game.set_num_heaps(len(game_str))

        return True
    
    def cmd_show(self, args: str) -> bool:
        # show prints the komi, then a space, then the game state
        # Check if the game exists
        if not self.game:
            return False
        
        komi = self.game.get_komi()
        game_state = self.game.get_game_state()

        print(f"k {komi} {game_state}")

        return True
    
    def cmd_toplay(self, args: str) -> bool:
        # Set the current player to b or w

        # Make sure there is an active game
        if not self.game:
            return False
        if args == "b":
            self.game.set_player("b")
        elif args == "w":
            self.game.set_player("w")
        # Check if the input is valid
        else:
            return False

        return True
    
    def cmd_play(self, args: str) -> bool:
        # Plays a turn
        # Make sure there is an active game
        if not self.game:
            return False

        # Check if heap_number is valid
        heap_number = args
        try:
            heap_number = int(heap_number)
        except ValueError:
            return False
        if heap_number < 0 or heap_number >= self.game.get_num_heaps():
            return False

        # Check whether the current heap is empty
        if len(self.game.get_game_state()[heap_number]) == 0:
            return False

        # Play the move
        turn_over = False
        while not turn_over:
            # Load in the game_state
            game_state = self.game.get_game_state()

            # Take the token from the top of the head (end of the list)
            current_heap = game_state[heap_number]
            # Get the colour of the token
            token_colour = current_heap[-1][0]
            # Get the value of the token
            token_value = current_heap[-1][1]

            # Add the token value to our score and remove it from the heap
            if self.game.get_player() == "b":
                self.game.set_b_score(self.game.get_b_score() + token_value)
            elif self.game.get_player() == "w":
                self.game.set_w_score(self.game.get_w_score() + token_value)
            current_heap.pop()

            # If the token is the opponents colour end turn
            if token_colour != self.game.get_player():
                turn_over = True
            # If the current heap is empty end turn
            if len(current_heap) == 0:
                turn_over = True

            # Update the game_state
            self.game.set_game_state(game_state)
            
        # Change the player variable
        if self.game.get_player() == "w":
            self.game.set_player("b")
        elif self.game.get_player() == "b":
            self.game.set_player("w")

        return True
    
    def cmd_legal(self, args: str) -> bool:
        legal = True

        # Make sure there is an active game
        if not self.game:
            return False

        # Check if heap_number is valid
        heap_number = args
        try:
            heap_number = int(heap_number)
        except ValueError:
            legal = False
            return False
        if heap_number < 0:
            legal = False
            return False
        if heap_number >= self.game.get_num_heaps():
            legal = False

        # Check whether the current heap is empty
        try:
            if len(self.game.get_game_state()[heap_number]) == 0:
                legal = False
        except IndexError:
            print("no")
            return True

        if legal:
            print("yes")
        else:
            print("no")

        return True
    
    def cmd_genmove(self, args: str) -> bool:
        # Make a list of all possible moves, then pick one at random do it
        # Make sure there is an active game
        if not self.game:
            return False

        valid_moves = []

        index = 0
        for heap in self.game.get_game_state():
            if len(heap) > 0:
                valid_moves.append(index)
            index += 1

        # If there are no valid moves
        if len(valid_moves) == 0:
            return False

        # If there are valid moves choose one at random
        random_move = random.choice(valid_moves)
        print(random_move)

        # Play that move
        self.cmd_play(str(random_move))

        return True
    
    def cmd_score(self, args: str) -> bool:
        # Prints the score in this format b 0 w 0.5
        # Make sure there is an active game
        if not self.game:
            return False
        b_score = self.game.get_b_score()
        w_score = self.game.get_w_score()
        print(f"b {b_score} w {w_score}")
        return True
    
    def cmd_winner(self, args: str) -> bool:
        # Check if the game is over
        # Make sure there is an active game
        if not self.game:
            return False
        
        game_over = True

        game_state = self.game.get_game_state()
        for heap in game_state:
            if len(heap) > 0:
                game_over = False

        if game_over:
            # Check who won (highest score) due to komi there can never be a tie
            winner = "b" if self.game.get_b_score() > self.game.get_w_score() else "w"
            print(winner)

        return game_over

#============================================================================
# End of functions requiring implementation
#============================================================================

#============================================================================
# The code below should not need modification
# Anyway, you may change or add to this code as you see fit
# Examples:
# You can add class variables to __init__ above
# You can add better error messages
# You can put commands inside your own Heap Go class
# etc.
#============================================================================
    # List available commands
    def cmd_help(self, ignore_args: str) -> bool:
        print("\nKnown commands:")
        for cmd in self.commands:
            print(cmd)
        return True

    def process_command(self, cmd_name: str, cmd_args: str) -> None:
        # Try to find command, None if wrong name
        status = "= -1"
        cmd = self.commands.get(cmd_name)
        if cmd:
            try:
                if cmd(cmd_args): # success!
                    status = "= 1"
            except Exception as e:
                print_error(f"Command {cmd_name} with arguments {cmd_args} failed with exception: {e}")
        else:
            print_error("Unknown command. Type 'help' for commands.")
        print(status)
    
    def main_loop(self) -> None:
        process_commands = True
        while process_commands:
            try:
                line = input()
            except EOFError:
                break
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            cmd_name = parts[0]
            if cmd_name == "exit":
                process_commands = False
                continue
            cmd_args = parts[1] if len(parts) > 1 else ""
            self.process_command(cmd_name, cmd_args)

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
