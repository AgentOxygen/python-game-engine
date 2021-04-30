# Primary object in game loop
from debug import parse_command
from debug import debug_out
from time import time as get_time
from multiprocessing import Queue


class GameInstance:
    """
    Creates game instance for handling server-sided information about the game
    Handles and stores game logic, creation, deletion, manipulation, and serialization
    (Examples: creating a unit, telling a unit to move, giving credits to the player)

    In order to function, the instance should be updated and monitored in a game loop.

    Pass commands to the game instance to affect things in the running game
    """
    debug_out("Game instance created!")
    __continue_to_update = True
    __phys_commands = []
    __stats_commands = []

    def update(self, time_delta: float) -> None:
        """
        Updates instance.
        :param time_delta: Change in time for this update in nanoseconds
        :return:
        """
        pass

    def run(self) -> bool:
        """
        Called to start this node's update loop
        :return: True if this node successfully starts running
        """
        old_time = get_time()
        while self.__continue_to_update:
            time_delta = old_time - get_time()

            self.process_commands()
            self.update(time_delta)

            for msg in self.get_physics_commands():
                self.objects_out.put(msg)
            for msg in self.get_stats_commands():
                self.stats_out.put(msg)

            old_time = get_time()
        return True

    def process_commands(self) -> None:
        """
        Grabs messages from 'user_in' queues and processes them
        :return: Nothing
        """
        # There might need to be a hard limit on how much data is pulled from the queue
        msgs = []
        while True:
            if not self.user_in.empty():
                msgs.append(self.user_in.get_nowait())
            else:
                break
        # Execute commands
        for msg in msgs:
            self.exec_command(msg)

    def phys_cmd(self, command: str, args):
        self.__phys_commands.append((command, args))

    def stats_cmd(self, command: str, args):
        self.__stats_commands.append((command, args))

    def get_physics_commands(self) -> list:
        # Returns queued up commands and clears internal list
        ret = self.__phys_commands
        self.__phys_commands = []
        return ret

    def get_stats_commands(self) -> list:
        # Returns queued up commands and clears internal list
        ret = self.__stats_commands
        self.__stats_commands = []
        return ret

    def active(self) -> bool:
        """
        :return: True if this node is updating
        """
        return self.__continue_to_update

    def exec_command(self, msg: tuple) -> bool:
        """
        Executes command using message and arguments passed through the parameter
        :param msg: Tuple containing command and arguments
        :return: True if command was successfully executed
        """
        command, args = parse_command(msg)
        try:
            if command == "EXIT":
                self.exit()
                return True
            elif command == 'USER_KEY_PRESS':
                self.process_key_input(args[0], args[1])
                self.stats_cmd("DEBUG_TIME", [args[2], get_time()])
                return True
        except IndexError:
            debug_out("ERROR - Not enough arguments for the following command: "
                      + "\nCommand: {}".format(command)
                      + "\n{}".format(str(args)))
        return False

    def process_key_input(self, key, modifiers) -> None:
        """
        Called when the game node is notified that the user has pressed a key.
        :param key: Key pressed
        :param modifiers: Any modifiers used such as shift or ctl, indicated by an integer
        :return: None
        """
        if key == 'ESCAPE':
            self.exit()
        elif key == 'SPACE':
            self.stats_cmd("DEBUG_DOT_SCREEN", [10, 20, 15])

    def exit(self) -> None:
        """
        Called when node is supposed to exit
        :return: True if this node successfully exits
        """
        debug_out("Graphics-input handler exiting...")
        self.__phys_commands.append(("EXIT", None))
        self.__stats_commands.append(("EXIT", None))
        self.__continue_to_update = False

    def __init__(self, user_in: Queue, stats_out: Queue, objects_out: Queue):
        self.user_in = user_in
        self.stats_out = stats_out
        self.objects_out = objects_out
        pass
