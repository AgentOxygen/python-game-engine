
from debug import debug_out
import game
import physics
import graphics_input
from multiprocessing import Process, Queue


def game_loop(objects_out: Queue, stats_out: Queue, user_in: Queue) -> None:
    """
    Reads user input and updates game statistics and object statuses

    :param objects_out: Outputs physical updates to this queue
    :param stats_out: Outputs information updates to this queue (stats)
    :param user_in: Receives user input to modify game
    :return:
    """
    debug_out("Initiating game loop...")

    game_instance = game.GameInstance(user_in, stats_out, objects_out)
    game_instance.run()


def phys_loop(objects_in: Queue, objects_out: Queue) -> None:
    """
    Receives updates from the game loop and modifies the physical status of objects in game
    Updates the physical properties of an object (force to velocity, velocity to position, etc)

    :param objects_in: Inputs updates to physical properties of objects
    :param objects_out: Outputs updates to graphics loop to be drawn
    :return:
    """
    debug_out("Initiating physics loop...")

    physics_handler = physics.PhysicsHandler(objects_in, objects_out)
    physics_handler.run()


def graphics_input_loop(phys_in: Queue, stats_in: Queue, user_out: Queue) -> None:
    """
    Receives updates from physics loop and game loop
    Tracks user input and outputs back to game loop

    :param phys_in: Receives objects with positions to draw
    :param stats_in: Receives information to display on screen
    :param user_out: Outputs tracked user input
    :return:
    """
    debug_out("Initiating graphics loop...")

    graphics_input_handler = graphics_input.GraphicsInputHandler(phys_in, stats_in, user_out)
    graphics_input_handler.run()

# ===========================================================================================
# For some reason, trying to run the graphics loop on a separate thread causes a MissingFunctionException
# So for now, keep the graphics loop on the main process
# graphicsLoop = threading.Thread(target=graphics_input_loop, args=(gameObjects, gameStats, userInput))


if __name__ == '__main__':
    # Queue containing data on objects (positions, states, commands)
    gameObjects = Queue()
    # Queue containing data on game statistics and information
    gameStats = Queue()
    # Queue containing data on drawing objects
    drawObjects = Queue()
    # Queue containing user input data
    userInput = Queue()

    # Create game and physics processes
    gameLoop = Process(target=game_loop, args=(gameObjects, gameStats, userInput,))
    physLoop = Process(target=phys_loop, args=(gameObjects, drawObjects,))
    gameLoop.daemon = True
    physLoop.daemon = True

    gameLoop.start()
    physLoop.start()

    debug_out("Starting game!")
    graphics_input_loop(drawObjects, gameStats, userInput)

    debug_out("Game exiting!")
    gameLoop.join()
    physLoop.join()
