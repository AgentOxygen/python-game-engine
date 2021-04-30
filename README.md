# Game Components
## Scenes
Scenes are what separate the different stages/states of the game:
1. Startup Menu (basic settings and navigational buttons)
2. Planning Phase (choosing a server, character, or load-out)
3. Competitive Play (for example, different maps)

Each scene has different elements that need to be loaded into memory.
Switching scenes allows the game to move from one stage to another without
sacrificing performance (for example, there's no need to load a map if the
player is not playing on it). In some cases it makes sense to combine scenes
or make even more.

## Objects

### Graphics Object JSON
To display an object on the screen, the graphics node needs a template associated with the
object in order to draw it. `GRAPH_TEMPLATES` should be the path to a JSON file where
all graphics object templates are stored. The format is as follows:
~~~
"graph/example_object": {
   "display_name": "Example Name",
   "attribute_1": true,
   "attribute_2": 14.2,
   "shapes": {
      "Circle": {
         "x" = 3.3,
         "y" = 52.0,
         "r" = 2
      },
      "Rectangle": {
         "x" = 13.55,
         "y" = 9.1,
         "s1" = 33,
         "s2" = 22
      }
   }
},
.. more objects ..
~~~
The `x` and `y` values are with coordinated to a standard cartesian plane. When the graphics
draw the template, the center of the object is at the origin (0, 0). By default, all rotations are
centered at this origin (later I will add the ability to define multiple rotation points for
a single object). Scalar values are scaled during processing, so just assume a unit length/factor of 1.

## Serialization

# Process Node Commands
Separate python processes act as independent nodes and communicate to each other by exchanging messages through
 queues.

There are three threads:
1. Game Logic - processes events and updates game statistics
2. Physics - updates physical objects in the game: motion, forces, collisions, etc.
3. Graphics/User Input - updates screen and tracks user input

This list documents what commands each node can receive and how they process them. 
For example, any node can receive the `EXIT` command which will initiate exit procedures 
for that given node and prompt it send an `EXIT` command to the other nodes. Commands listed 
under a node can be processed by that node. This does not indicate which node(s) should send 
specific commands to any other node. This documentation is based on receiving, not sending. 
Essentially, these "commands" are like "events".

## General Commands
These commands are recognized on all three nodes.

**Command:** `EXIT`  **Args:** `None`
> Initiates exit procedures, closing all others threads and ending the application.

## Game Logic Commands
These commands are recognized by the game logic node.

**Command:** `USER_MOUSE_CLICK`  **Args:** `BUTTON:int, GUI_OBJECT_ID:str`
> Indicates a user clicked on the GUI object specified by GUI_OBJECT_ID using the button specified by BUTTON.

**Command:** `USER_KEY_PRESS`  **Args:** `[KEY:str, MODIFIERS:str]`
> Indicates a user pressed the keyboard key specified by KEY.  
> Calls game.process_key_input()

**Command:** `USER_KEY_RELEASE`  **Args:** `[KEY:str, MODIFIERS:str]`
> Indicates a user released the keyboard key specified by KEY.

## Physics Commands
These commands are recognized by the physics node.

## Graphics/User Input Commands
These commands are recognized by the graphics/user input node.

**Command:** `DEBUG_DOT_SCREEN`  **Args:** `X:float, Y:float, RADIUS:float`
> Debug method that places a dot at X and Y with a size specified by SIZE on the user's screen.

**Command:** `GR_CREATE_OBJECT`  **Args:** `[UUID:uuid.UUID, TEMPLATE:str]`
> Creates graphical object with specified UUID using specified TEMPLATE  
> The UUID should correspond to the game object stored on the game node  
> The TEMPLATE should correspond to a dictionary located in the GRAPH_TEMPLATES JSON file

**Command:** `GR_CHANGE_STATE`  **Args:** `[UUID:uuid.UUID, STATE:str, VALUE:(float/str/bool)]`
> Changes specified STATE of the graphical object associated with the specified UUID
