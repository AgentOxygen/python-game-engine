# Contains debugger functions

from datetime import datetime
from multiprocessing import Queue


def parse_command(msg: tuple) -> tuple:
    if type(msg) != tuple:
        raise TypeError("Command-message is not a tuple of format: (string, args)")
    command, args = msg
    if type(command) != str:
        raise TypeError("Command should be a string.")
    return command, args


def post_command(queue: Queue, command: str, args=None) -> None:
    msg = parse_command((command, args))
    queue.put(msg)


def debug_out(msg: str) -> None:
    """
    Outputs message to console and logs.
    :param msg: Message to output.
    :return: None
    """
    print("[{}]  {}".format(datetime.now().strftime("%H:%M:%S"), msg))
