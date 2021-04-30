# Primary object in physics loop
from debug import parse_command
from debug import debug_out
from time import time as get_time
from multiprocessing import Queue


class PhysicsHandler:
    """
    Creates physics handler for a game instance.
    Handles physical data corresponding to an object and the relationship it has with other physical objects.
    In order to function, the instance should be updated and monitored in a game loop.

    Pass state updates to change the states of objects in the game.
    """
    debug_out("Physics handler created!")
    __continue_to_update = True
    __graphics_io_commands = []

    def update(self, time_delta: float) -> None:
        """
        Updates instance.
        :param time_delta: Change in time for this update in nanoseconds
        :return:
        """
        pass

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
        except IndexError:
            debug_out("ERROR - Not enough arguments for the following command: "
                      + "\nCommand: {}".format(command)
                      + "\n{}".format(str(args)))
        return False

    def run(self) -> None:
        old_time = get_time()
        while self.__continue_to_update:
            time_delta = old_time - get_time()

            self.process_commands()
            self.update(time_delta)

            for msg in self.get_graphics_io_commands():
                self.objects_out.put(msg)

            old_time = get_time()

    def process_commands(self) -> None:
        """
        Grabs messages from 'phys_in' and 'stats_in' queues and processes them
        :return: Nothing
        """
        # There might need to be a hard limit on how much data is pulled from the queue
        msgs = []
        while True:
            if not self.objects_in.empty():
                msgs.append(self.objects_in.get_nowait())
            else:
                break
        # Execute commands
        for msg in msgs:
            self.exec_command(msg)

    def active(self) -> bool:
        """
        :return: True if this node is updating
        """
        return self.__continue_to_update

    def exit(self) -> None:
        """
        Called when node is supposed to exit
        :return: True if this node successfully exits
        """
        debug_out("Physics handler exiting...")
        self.__graphics_io_commands.append(("EXIT", None))
        self.__continue_to_update = False

    def get_graphics_io_commands(self) -> list:
        ret = self.__graphics_io_commands
        self.__graphics_io_commands = []
        return ret

    def __init__(self, objects_in: Queue, objects_out: Queue):
        self.objects_in = objects_in
        self.objects_out = objects_out
