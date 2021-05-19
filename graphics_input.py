# Primary object in graphics input loop

from debug import parse_command
from debug import debug_out
from multiprocessing import Queue
from time import time
import pyglet
import constants


class GraphicsInputHandler(pyglet.window.Window):
    """
    Creates graphics and input handler for a game instance.
    Handles graphics for game and translates user input into game commands.
    In order to function, the instance should be updated and monitored in a game loop.

    Pass positional and statistical updates to change the appearance of objects and displays in the game.
    Uses pyglet:
    https://pyglet.readthedocs.io/en/latest/programming_guide/quickstart.html#hello-world
    """
    debug_out("Graphics-Input handler created!")
    __game_commands = []
    __continue_to_update = True
    __shapes = []

    is_main_menu = True
    # Add vertexes to this batch for rendering in window
    batch = pyglet.graphics.Batch()
    # Used for processing key inputs
    keys = pyglet.window.key

    def update(self, time_delta: float) -> None:
        """
        Updates instance.
        :param time_delta: Change in time for this update in nanoseconds
        :return: Nothing
        """
        self.process_commands()
        self.on_draw()

    def game_cmd(self, command: str, args) -> None:
        self.__game_commands.append((command, args))

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
            elif command == "DEBUG_DOT_SCREEN":
                self.debug_draw_dot(args[0], args[1], args[2])
                return True
            elif command == "DEBUG_TIME":
                graph_sent_time = args[0]
                game_sent_time = args[1]
                round_trip = round(time() - graph_sent_time, 4)
                graph_to_game = round(game_sent_time - graph_sent_time, 4)
                game_to_graph = round(time() - game_sent_time, 4)
                debug_out("Round trip: {}s, Graph->Game: {}s, Game->Graph: {}s"
                          .format(round_trip, graph_to_game, game_to_graph))
                return True
        except IndexError:
            debug_out("ERROR - Not enough arguments for the following command: "
                      + "\nCommand: {}".format(command)
                      + "\n{}".format(str(args)))
        return False

    def active(self) -> bool:
        """
        :return: True if this node is updating
        """
        return self.__continue_to_update

    def exit(self) -> bool:
        """
        Called when node is supposed to exit
        :return: True if this node successfully exits
        """
        debug_out("Graphics-input handler exiting...")
        self.__game_commands.append(("EXIT", None))
        self.process_commands()
        self.close()
        return True

    def get_game_commands(self) -> list:
        """
        Returns commands for outputting to game node and clears internal waiting list
        :return: List of commands
        """
        ret = self.__game_commands
        self.__game_commands = []
        return ret

    def __init__(self, phys_in: Queue, stats_in: Queue, user_out: Queue, process_rate=-1):
        """
        :param phys_in: Receives objects with positions to draw
        :param stats_in: Receives information to display on screen
        :param user_out: Outputs tracked user input
        :param process_rate: Rate at which to process incoming and outgoing data from queues (updates per second)
        """
        super(GraphicsInputHandler, self).__init__(vsync=False)
        self.phys_in = phys_in
        self.stats_in = stats_in
        self.user_out = user_out
        self.process_rate = float(process_rate)
        self.hello_world_debug_label = pyglet.text.Label('Hello, world')

    def process_commands(self) -> None:
        """
        Grabs messages from 'phys_in' and 'stats_in' queues and processes them
        :return: Nothing
        """
        # There might need to be a hard limit on how much data is pulled from the queue
        msgs = []
        while True:
            if not self.phys_in.empty():
                msgs.append(self.phys_in.get_nowait())
            else:
                break
        while True:
            if not self.stats_in.empty():
                msgs.append(self.stats_in.get_nowait())
            else:
                break
        # Execute commands
        for msg in msgs:
            self.exec_command(msg)

        for msg in self.get_game_commands():
            self.user_out.put(msg)

    def run(self) -> bool:
        """
        Called to start this node's update loop
        :return: True if this node successfully starts running
        """
        pyglet.clock.schedule_interval(self.update, self.process_rate)
        pyglet.app.run()
        return True

    def debug_draw_dot(self, x: float, y: float, radius: float):
        """
        Draws a dot on the screen by adding a circle shape to the list
        :param x: x coord for center
        :param y: y coord for center
        :param radius: radius of circle from center
        :return:
        """
        self.__shapes.append(pyglet.shapes.Circle(x=x, y=y, radius=radius, color=(50, 225, 30), batch=self.batch))

    def on_draw(self) -> None:
        """
        Called when redrawing the screen. Could be optimized to redraw only certain parts of the screen if necessary
        :return:
        """
        self.clear()
        self.hello_world_debug_label.draw()
        self.batch.draw()

    def on_close(self) -> None:
        """
        Called when the user closes the window
        :return:
        """
        self.exit()

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        pass

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        debug_out("{}, {}, {}".format(x, y, button))

    def on_mouse_release(self, x, y, button, modifiers) -> None:
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        pass

    def on_key_press(self, symbol, modifiers) -> None:
        # This has an extra time() argument for debugging things. It should be removed from game.py as well
        self.game_cmd('USER_KEY_PRESS', [self.keys.symbol_string(symbol), modifiers, time()])

    def on_key_release(self, symbol, modifiers) -> None:
        self.game_cmd('USER_KEY_RELEASE', [self.keys.symbol_string(symbol), modifiers])
        pass