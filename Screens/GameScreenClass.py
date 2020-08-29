from importlib import import_module

from numpy import sin, cos, radians, zeros, ones
from numpy.random import default_rng
from threading import Thread
from tkinter import (Frame, Canvas, PhotoImage, Label, Button,
                     CENTER, DISABLED, NORMAL, NW, LEFT)
from time import sleep
from timeit import default_timer
from pynput import keyboard

from Utils.Const import *
from Utils.HelperFunctions import get_rectangle_corners


class GameScreen(Frame):
    """
    Contains all elements and functionality for playing the game.

    Concerning the actual game field there are two layers to look at: the visual and the effective layer.
    The visual layer consists of a Canvas Object containing a PhotoImage Object where all the pixels are displayed on.
    The effective layer consists of two 2-dimensional numpy arrays storing the locations of walls and items
    respectively. For convenience reasons, both layers use the same syntax for location description. This results in
    the second layer being mirrored compared to the first layer. An example:
        Considering the pixel on the first layer at position (x, y), x describing the horizontal location and y the
        vertical location starting at the top left corner. In order for the second layer to align perfectly to that,
        the corresponding pixel should be at position [y, x] since the first entry describes the row number and the
        second entry the column number of a matrix.
        Instead, both layers store the corresponding pixel at (x, y) resulting in the second layer being
        mirrored at the first diagonal axis.

    """
    def __init__(self, controller, parent):
        Frame.__init__(self, master=parent)
        self.parent = parent
        self.controller = controller

        # reset player scores
        for p in self.controller.players:
            p.wins = 0

        # -- ATTRIBUTES
        self.current_round = 0
        self.max_wins = self.controller.max_rounds
        self.walls = zeros((self.controller.field_size, self.controller.field_size))
        self.gap_rate = 100  # Higher means fewer gaps
        self.gap_length = 4

        self.running = False
        self.tick_count = 0
        self._interval = 1/28  # tick interval in seconds

        self.practice_game = False  # If True, every round ends in a draw.

        # -- Game field
        self.canvas = Canvas(master=self,
                             width=self.controller.canvas_size,
                             height=self.controller.canvas_size,
                             bg="Black",
                             )

        self.field_image = None  # defined in call of self.initiate_canvas

        self.initiate_canvas()

        # -- Title label
        self.label_title = Label(master=self,
                                 font=self.controller.font_big,
                                 text="___Wall\n  Run___",
                                 justify=CENTER,
                                 )
        self.label_title.grid(row=0, column=10, columnspan=3)

        # -- Game buttons
        button_setting = {"width": int(3 * controller.scale),
                          "height": int(2 * controller.scale),
                          "font": controller.font_basic,
                          }

        self.binit = Button(master=self,
                            text="Init",
                            command=self.initialise_new_round,
                            cnf=button_setting,
                            state=DISABLED,
                            )
        self.binit.grid(row=1, column=10)

        self.bgopause = Button(master=self,
                               text="Go",
                               command=self.start_round,
                               cnf=button_setting,
                               state=DISABLED,
                               )
        self.bgopause.grid(row=1, column=11)

        self.bback = Button(master=self,
                            text="Back",
                            command=self.back,
                            cnf=button_setting,
                            )

        self.bback.grid(row=1, column=12)

        # -- Game labels
        self.label_rounds = Label(master=self,
                                  font=self.controller.font_medium,
                                  text="Round {0}\n {1} Points to win".format(self.current_round, self.max_wins),
                                  )
        self.label_rounds.grid(row=2, column=10, columnspan=3)

        self.label_info = Label(master=self,
                                font=self.controller.font_medium,
                                text="",
                                )
        self.label_info.grid(row=3, column=10, columnspan=3)

        # -- Player labels
        self.player_labels = []
        self.display_ranking()

        # -- Item related
        self.item_max_count = 6  # Total number of items that is allowed to exist on the field.
        self.items = zeros((self.controller.field_size, self.controller.field_size), dtype="int")  # Item locations
        self.items_spawned = {}  # Dict of triple: (item object, PhotoImage of icon, position of top left pixel)
        self.item_id = 1  # Key for items_spawned dict. Rolling int per round starting at 1.
        self.items_active = []  # List of tuple of currently active items (item object, expiration tick)
        self.item_drop_chance = 0.005  # Chance to spawn an item per tick.

        # -- Other
        self.thread_jobs = None  # will be defined in start_round
        self.player_dot_traces = None  # will be defined in initialise_new_round
        self.rng = default_rng()  # RNG object

        # -- Listeners for space bar
        self.listener_space = None

    # ########################################
    # Player related functions
    # ########################################

    def place_player(self, p, pos=None, angle=None):
        """
        This function places player p on the game field at position pos.
        In fact this function updates the coordinates of the player-object to pos
        and additionally adds a tail-wall to the class-attribute walls.
        It also resets all player attributes to its defaults.

        :param p: Player Object to be placed.
        :param pos: Position to place the player as tuple of size 2 of int.
        If None, each coordinate is randomly chosen from [tol, field_size - tol],
        where tol is 10% of the field size.
        :param angle: angle the player faces, default None (which is random angle).
        :return: None
        """
        # set move command of each player to STRAIGHT and make alive
        p.move_command = DIR_STRAIGHT
        p.speed = SPEED_NORMAL
        p.turn_rate = RATE_NORMAL
        p.size = SIZE_NORMAL
        p.key_is_held_down = False

        p.alive = True
        # Set facing angle.
        if angle is None:
            p.angle = self.rng.integers(0, 360)
        else:
            p.angle = angle

        # Set position
        if pos is None:
            tol = int(self.controller.field_size * 0.1)
            p.pos = (self.rng.integers(tol, self.controller.field_size - tol, endpoint=True),
                     self.rng.integers(tol, self.controller.field_size - tol, endpoint=True)
                     )
        else:
            p.pos = pos

        # p.dot_trace = self.dot_trace(pos=p.pos, r=p.size)
        p.dot_trace, p.data_strings, p.rect_corners = self.dot_trace_string_data_rect_corners(pos=p.pos,
                                                                                              r=p.size,
                                                                                              color=p.color)
        # get wall trace
        tail_len = 12
        tail_trace = self.way_trace(dot_trace=p.dot_trace, dist=tail_len,
                                    angle=(p.angle+180) % 360, sparse=max(1, int(p.size/2))
                                    )
        # update walls
        for c in [x for x in tail_trace if x not in p.dot_trace]:  # prevent crash with own way trace
            self.walls[c] = -1
        # draw trace
        self.put_trace(trace=tail_trace, color=p.color)
        # draw head
        # self.put_trace(trace=p.dot_trace, color="White")
        self.field_image.put(data=p.data_strings[0].replace(p.color, "White"), to=p.rect_corners[0])

    # ########################################
    # Item related functions
    # ########################################

    def remove_item(self, item_id):
        """
        Removes an item from the field by its round specific id, both visually and effectively.

        :param item_id: int, id of the item to remove. Needs to be present in self..items_spawned.
        :return: triple (removed item instance, item icon, pos)
        """
        item_to_remove, icon, pos = self.items_spawned.pop(item_id)
        x, y = pos
        self.items[x:x+ITEMSIZE, y:y+ITEMSIZE] = 0
        return item_to_remove, icon, pos

    def create_item_by_name(self, name):
        """
        Creates a random item instance among all registered items and returns it.

        :param name: string, name of the item-class
        :return: Item instance of given class name.
        """

        item_module = import_module("FieldObjects.Items." + name)
        item_class = getattr(item_module, name)
        return item_class(self.controller, self)

    def place_item(self, name, pos):
        """
        Places the item identified by name on the game field at pos. This function also draws the item on the canvas
        and removes the oldest item on the field, if the maximum number of items is reached.

        :param name: String, Class name of the item to place.
        :param pos: Tuple of size 2 of int, position on the game field to place the item.
        :return: None
        """
        # -- Create and store item
        item_to_place = self.create_item_by_name(name)
        icon = PhotoImage(file=item_to_place.image_path)
        self.items_spawned[self.item_id] = (item_to_place, icon, pos)
        # -- Place item on the field
        # visually
        x, y = pos
        offset = (self.controller.canvas_size - self.controller.field_size)/2  # Offset between canvas and game field.
        self.canvas.create_image(offset + x, offset + y, image=icon, anchor=NW)  # Icon is put un CANVAS not field
        # effectively
        self.items[x:x+ITEMSIZE, y:y+ITEMSIZE] = self.item_id
        # -- Increase item item_id
        self.item_id = self.item_id + 1

    # ########################################
    # Canvas and window related functions
    # ########################################

    def display_ranking(self):
        """
        Displays the player names and their points in descending order on the game screen.

        :return: None
        """

        for lab_n, lab_p in self.player_labels:
            lab_n.destroy()
            lab_p.destroy()

        row = 4
        # get sorted list of player wins in descending order
        scores = list(self.controller.players)
        scores.sort(key=lambda p: p.wins, reverse=True)
        for p in scores:
            # Name
            lab_name = Label(master=self,
                             font=self.controller.font_basic,
                             text=p.name,
                             fg=p.color,
                             )
            lab_name.grid(row=row, column=10, columnspan=2)
            # Points
            lab_points = Label(master=self,
                               font=self.controller.font_basic,
                               text=p.wins,
                               fg=p.color,
                               justify=LEFT
                               )
            lab_points.grid(row=row, column=12, columnspan=1)
            self.player_labels.append((lab_name, lab_points))
            row += 1

    def initiate_canvas(self):
        self.walls = zeros((self.controller.field_size, self.controller.field_size))
        self.canvas.destroy()
        self.canvas = Canvas(master=self,
                             width=self.controller.canvas_size,
                             height=self.controller.canvas_size,
                             bg="Black",
                             )
        self.canvas.grid(row=0, column=0, columnspan=10, rowspan=10, padx=5, pady=5)

        self.field_image = PhotoImage(width=self.controller.field_size,
                                      height=self.controller.field_size,
                                      )

        self.canvas.create_image((self.controller.canvas_size / 2, self.controller.canvas_size / 2),
                                 image=self.field_image,
                                 anchor=CENTER,
                                 )

        self.toggle_border(on=True)
        self.display_border()

    def display_border(self, on=True):
        """
        Updates the visuals for the surrounding walls.

        :param on: boolean, True means that walls are displayed as "on" or present, and absent otherwise (default True).
        :return: None
        """
        if on:
            color = "White"
        else:
            color = "Black"
        # left border
        self.field_image.put(data=color, to=(0, 0, 1, self.controller.field_size))
        # top border
        self.field_image.put(data=color, to=(0, 0, self.controller.field_size, 1))
        # right border
        self.field_image.put(data=color, to=(0, self.controller.field_size-1,
                                             self.controller.field_size-1, self.controller.field_size))
        # bottom border
        self.field_image.put(data=color, to=(self.controller.field_size-1, 0,
                                             self.controller.field_size, self.controller.field_size))

    # ########################################
    # Movement and functional functions
    # ########################################

    def dot_trace(self, pos, r):
        """
        Creates a list of coordinates that represent a circle of radius r on a 2d grid.
        This function respects the borders of the game field.

        :param pos: center of dot as tuple of size 2 of int
        :param r: radius is pixels as int
        :return: list
        """
        # check all pixels in square
        X, Y = pos
        trace = []
        for x, y in [(x, y) for x in range(X-r, X+r+1) for y in range(Y-r, Y+r+1)]:
            if (x - X)**2+(y-Y)**2 < r:
                # append if pixel is in circle around pos
                trace.append((x % self.controller.field_size,
                              y % self.controller.field_size)
                             )
        return trace

    def dot_trace_string_data_rect_corners(self, pos, r, color):
        """
        Computes a string containing the information for drawing a dot with the native PhotoImage put function.
        The returned string-data does not cross the game field border.
        """
        crossing_bot = []
        crossing_bot_left = []
        crossing_bot_right = []
        crossing_top = []
        crossing_top_left = []
        crossing_top_right = []
        crossing_left = []
        crossing_right = []
        crossing_nothing = []
        crossing_sets = [crossing_bot, crossing_bot_left, crossing_bot_right, crossing_top, crossing_top_left,
                         crossing_top_right, crossing_left, crossing_right, crossing_nothing]

        X, Y = pos
        dot_trace = []
        for x, y in [(x, y) for x in range(X-r, X+r+1) for y in range(Y-r, Y+r+1)]:
            if (x - X)**2+(y - Y)**2 < r:
                # Decide if and where pixels cross the field-border
                if x < 0 and y < 0:
                    crossing_top_left.append((x % self.controller.field_size, y % self.controller.field_size))
                elif x < 0 and y >= self.controller.field_size:
                    crossing_bot_left.append((x % self.controller.field_size, y % self.controller.field_size))
                elif x >= self.controller.field_size and y < 0:
                    crossing_top_right.append((x % self.controller.field_size, y % self.controller.field_size))
                elif x >= self.controller.field_size and y >= self.controller.field_size:
                    crossing_bot_right.append((x % self.controller.field_size, y % self.controller.field_size))
                elif x < 0 and not y < 0 and not y >= self.controller.field_size:
                    crossing_left.append((x % self.controller.field_size, y % self.controller.field_size))
                elif x >= self.controller.field_size and not y < 0 and not y >= self.controller.field_size:
                    crossing_right.append((x % self.controller.field_size, y % self.controller.field_size))
                elif not x < 0 and not x >= self.controller.field_size and y < 0:
                    crossing_top.append((x % self.controller.field_size, y % self.controller.field_size))
                elif not x < 0 and not x >= self.controller.field_size and y >= self.controller.field_size:
                    crossing_bot.append((x % self.controller.field_size, y % self.controller.field_size))
                else:
                    crossing_nothing.append((x % self.controller.field_size, y % self.controller.field_size))
                dot_trace.append((x % self.controller.field_size, y % self.controller.field_size))

        # ----- create string-data for PhotoImage's put method.
        # Roll through every pixel of the square in the respective crossing set
        data_strings = []
        rect_corners = []
        for crossing_set in crossing_sets:
            if not crossing_set:
                continue
            data_string = ""
            a, b, x, y = get_rectangle_corners(crossing_set)
            for i in range(a, x+1):  # x-axis roll-through
                data_string += "{"
                for j in range(b, y+1):  # y-axis roll-through
                    if (i, j) in crossing_set:
                        data_string += color + " "
                    else:
                        current_color = self.field_image.get(i, j)
                        if current_color == RGB_VALUES[color]:
                            data_string += color + " "
                        else:
                            # data_string += "#{:02x}{:02x}{:02x}".format(*self.field_image.get(i, j)) + " "
                            data_string += "Black" + " "
                data_string += "} "
            data_strings.append(data_string)
            rect_corners.append((a, b, x+1, y+1))

        return dot_trace, data_strings, rect_corners

    def get_target_pixel(self, pos, dist, angle):
        """
        Computes the pixel that is reached after going from pos in direction of angle for a distance of dist.

        :param pos: starting position, tuple of size 2 of int
        :param dist: walking distance, int
        :param angle: directional angle, 0 is facing north, int in [0, 359)
        :return: tuple of size 2.
        """
        x, y = pos
        rad = radians(angle % 360)
        return ((x + round(cos(rad) * dist)) % self.controller.field_size,
                (y + round(sin(rad) * dist)) % self.controller.field_size
                )

    def way_trace(self, dot_trace, dist, angle, sparse=1):
        """
        Computes a list of positions if one starts from each position in dot_trace
        and goes a distance of dist facing the given angle.

        :param dot_trace: list of tuple of size 2 of int or tuple of size 2
        :param dist: distance to go, int
        :param angle: facing angle, int
        :param sparse: level of denseness between points, lower is denser. int > 0. default 1.
        :return: list of coordinates
        """
        way_trace = []
        for pix in dot_trace:
            for d in range(dist):
                if d % sparse == 0:
                    way_trace.append(self.get_target_pixel(pos=pix,
                                                           dist=d,
                                                           angle=angle
                                                           )
                                     )
        return way_trace

    def toggle_border(self, on=True):
        """
        Toggles surrounding walls in numpy array on and off. No visual effect is applied.

        :param on: boolean, If True, walls are turned on. Off otherwise.
        :return: None
        """
        if on:
            self.walls[0, :] = -ones(self.controller.field_size)
            self.walls[-1, :] = -ones(self.controller.field_size)
            self.walls[:, 0] = -ones(self.controller.field_size)
            self.walls[:, -1] = -ones(self.controller.field_size)
        else:
            self.walls[0, :] = zeros(self.controller.field_size)
            self.walls[-1, :] = zeros(self.controller.field_size)
            self.walls[:, 0] = zeros(self.controller.field_size)
            self.walls[:, -1] = zeros(self.controller.field_size)

    # ########################################
    # Listener functions
    # ########################################

    def make_listener(self, act):
        """
        Makes a listener for the space key to init or start or pause a round. It also stops the old listener.

        :param act: string, type of action the listener should have (use "init". "go" or "pause").
        :return: None
        """
        self.turn_off_space_listener()
        if act == "go":
            def on_press(key):
                if key == keyboard.Key.space:
                    self.start_round()
                    return False
            self.listener_space = keyboard.Listener(on_press=on_press)
        elif act == "init":
            def on_press(key):
                if key == keyboard.Key.space:
                    self.initialise_new_round()
                    return False
            self.listener_space = keyboard.Listener(on_press=on_press)
        elif act == "pause":
            def on_press(key):
                if key == keyboard.Key.space:
                    self.pause_round()
                    return False
            self.listener_space = keyboard.Listener(on_press=on_press)

    def turn_off_space_listener(self):
        """
        Turns of the game-screen owned listener listener_space.
        :return: None
        """
        try:
            self.listener_space.stop()
            self.listener_space.join()
        except AttributeError:
            pass
        except RuntimeError:  # If thread not started yet
            pass

    def turn_off_player_listeners(self):
        """
        This function turns off all player listeners (movement controls) and resets their facing-directions.

        :return:
        """
        for p in self.controller.players:
            p.move_command = DIR_STRAIGHT
            try:
                p.listener.stop()
                p.listener.join()
            except AttributeError:
                pass
            except RuntimeError:  # If thread not started yet
                pass

    def turn_off_all_listeners(self):
        """
        This function turns of all player control-listeners and pause-listeners.

        :return: None
        """
        # Player listeners
        self.turn_off_player_listeners()
        self.turn_off_space_listener()

    # ########################################
    # Meta / button functions
    # ########################################

    def set_buttons(self, state):
        """
        Sets the buttons on the window according to the given state.
        It also activates a listener with the according action on the space key if state is "go", "pause" or "init".

        :param state: String, "go" yields buttons which can unpause the round, "pause" yields buttons which can pause
        the game, "init" yields buttons which can initiate a new round and "off" turns all buttons off.
        :return: None
        """
        if state == "go":
            self.bgopause.config(text="Go", command=self.start_round, state=NORMAL)
            self.binit.config(state=DISABLED)
            self.make_listener(act="go")
            self.listener_space.start()
        elif state == "pause":
            self.bgopause.config(text="Pause", command=self.pause_round, state=NORMAL)
            self.binit.config(state=DISABLED)
            self.make_listener(act="pause")
            self.listener_space.start()
        elif state == "init":
            self.bgopause.config(text="Pause", command=self.pause_round, state=DISABLED)
            self.binit.config(state=NORMAL)
            self.make_listener(act="init")
            self.listener_space.start()
        elif state == "off":
            self.bgopause.config(text="Go", command=self.start_round, state=DISABLED)
            self.binit.config(state=DISABLED)
            self.turn_off_space_listener()
        else:
            raise ValueError("The parameter state must be 'go', 'pause', 'init' or 'off' but was '" + state + "'.")

    def initialise_new_round(self):
        """
        Preparation in order to start the round.
        Place players.

        :return: None.
        """
        self.current_round += 1
        self.label_rounds.config(text="Round {0}\n {1} Points to win".format(self.current_round, self.max_wins))
        # Clear items
        self.reset_all_items()
        # clean canvas
        self.initiate_canvas()
        # Buttons
        self.set_buttons(state="go")
        # Placing players
        for p in self.controller.players:
            # Put player on field
            self.place_player(p)
        # Other
        self.label_info.config(text="")

    def start_round(self):
        """
        Starts the session by enabling all players movement listeners and starts the movement actions.

        :return: None
        """
        # Buttons
        self.set_buttons(state="pause")
        # Activate players listeners
        for p in self.controller.players:
            p.make_listener()
            p.listener.start()

        # Initiate periodic events
        self.running = True
        # Separate thread init for periodic jobs
        self.thread_jobs = Thread(group=None,
                                  target=self.ticker,
                                  name="periodic_tasks",
                                  daemon=True
                                  )
        self.thread_jobs.start()
        # Clear info message
        self.label_info.config(text="")

    def pause_round(self):
        """
        Stops the move jobs and all player movement listeners and activates buttons in order to restart the round again.

        :return: None
        """
        self.running = False
        # Buttons
        self.set_buttons(state="go")
        # Player listeners
        self.turn_off_player_listeners()

    def back(self):
        self.running = False
        self.turn_off_all_listeners()
        self.reset_all_items()
        self.controller.show_frame("Title")

    # ########################################
    # Ticker functions
    # ########################################

    def ticker(self):
        """
        Collects all jobs that have to be done every tick.
        This function puts its calling thread to sleep and therefore should be called within a separate thread.

        :return: None
        """
        first_loop = True
        while self.running:
            start = default_timer()
            # print("Current Tick:", self.tick_count)
            self.tick_count += 1
            # #### old_traces = self.move()
            old_traces = self.move()
            move = default_timer()
            # print("Time for move:", move - start)
            # #### self.update_visuals(old_traces)
            self.update_visuals(old_traces)
            self.check_events()
            if self.check_round_end():
                self.running = False
                self.turn_off_all_listeners()
                self.solve_round_end()
                break
            update = default_timer()
            # print("Time for update:", update - move)
            if not first_loop and self._interval-(update-start) < 0:
                self.pause_round()
                self.label_info.config(text="The tick processing took longer\n "
                                            "than the given tick rate!\n Game is paused.",
                                       fg="black")
            first_loop = False
            # print("Sleep length:", self._interval-(update-start))
            sleep(max([0, self._interval-(update-start)]))
            end = default_timer()
            # print("Tick length:", end - start, "\n==============")

    def move(self):
        """
        This function moves every player by one step according to their current position, speed, angle and
        move command. It also updates the walls with the way traces and returns a list of all the old player positions.

        :return: dict of list of tuple of int of size 2.
        """
        old_data_strings_rect_corners = {}
        for p in self.controller.players:
            if not p.alive:
                continue

            if p.move_command == DIR_LEFT:
                p.angle = (p.angle - p.turn_rate) % 360
            elif p.move_command == DIR_RIGHT:
                p.angle = (p.angle + p.turn_rate) % 360
            # ## compute new position
            p.pos = self.get_target_pixel(pos=p.pos, dist=p.speed, angle=p.angle)
            # ## reset move_command if players turn rate is set to RATE_RIGHT_ANGLE.
            if p.turn_rate == RATE_RIGHT_ANGLE:
                p.move_command = DIR_STRAIGHT
            # ## update new dot trace
            p.update_tolerance_heads()  # store current (old) dot-trace for tolerance computation
            old_dot_trace = p.dot_trace
            old_data_strings_rect_corners[p] = (p.data_strings, p.rect_corners)
            p.dot_trace, p.data_strings, p.rect_corners = self.dot_trace_string_data_rect_corners(pos=p.pos,
                                                                                                  r=p.size,
                                                                                                  color=p.color)
            p.compute_collision_head()  # compute the current collision head
            # ## update walls
            if (self.tick_count % self.gap_rate > self.gap_length
                    and not p.flying):
                for pix in [c for c in old_dot_trace if c not in p.dot_trace]:
                    self.walls[pix] = -1
        return old_data_strings_rect_corners

    def check_events(self):
        """
        This function performs various checks and acts accordingly:
            1. Check collisions with walls -> kill player
            2. Check collision with items -> activate items
            3. Check item expiration -> deactivate items
            4. Spawn new items by chance
        :return:
        """
        # Check crashes with walls and items
        for p in self.controller.players:
            if p.alive:
                for pix in p.collision_head:
                    # Walls
                    if not p.flying and self.walls[pix] == -1 and not p.pixel_in_tolerance(pix):
                        p.alive = False
                        break
                    # Items
                    if p.alive and self.items[pix] > 0:
                        item_id = self.items[pix]
                        item, _, pos = self.remove_item(item_id)  # Remove item from field and item-matrix
                        # activate item
                        self.items_active.append((item, self.tick_count + item.duration))
                        item.activate(player=p)  # Activate the effect
                        break
        # Check to deactivate items
        for tup in self.items_active:
            item, end = tup
            if end <= self.tick_count:
                item.deactivate()
                self.items_active.remove(tup)
        # Place items
        if self.item_max_count > 0 and self.rng.random() < self.item_drop_chance:
            # Remove oldest item if the max count is reached.
            if self.item_max_count <= len(self.items_spawned):
                oldest_id = min(self.items_spawned.keys())
                self.remove_item(oldest_id)
            x_rand = self.rng.integers(ITEMSIZE, self.controller.field_size-ITEMSIZE)
            y_rand = self.rng.integers(ITEMSIZE, self.controller.field_size-ITEMSIZE)
            self.place_item(name=self.rng.choice(self.controller.item_names), pos=(x_rand, y_rand))

    def update_visuals(self, old_data_strings_rect_corners):
        """
        Draws the current position of each player on the canvas.
        """
        # Draw player traces and dots.
        for p in self.controller.players:
            if not p.alive:
                continue
            # draw old position if player is not flying
            old_data_strings, old_rect_corners = old_data_strings_rect_corners[p]
            if self.tick_count % self.gap_rate > self.gap_length and not p.flying:
                for data_string, rect_corners in zip(old_data_strings, old_rect_corners):
                    self.field_image.put(data=data_string, to=rect_corners)
            else:
                for data_string, rect_corners in zip(old_data_strings, old_rect_corners):
                    self.field_image.put(data=data_string.replace(p.color, "Black"), to=rect_corners)

            # draw new player head
            if p.flying and self.tick_count % 4 in [2, 3]:
                # Player is flying. Do not print every 3rd and 4th head position.
                pass
            else:
                # Player is not flying. Print head as usual.
                for data_string, rect_corners in zip(p.data_strings, p.rect_corners):
                    self.field_image.put(data=data_string.replace(p.color, "White"),
                                         to=rect_corners)

            self.put_trace(trace=p.collision_head, color="Cyan")

    # ########################################
    # Helper functions
    # ########################################

    def clear_walls(self):
        """
        Removes all walls but the border. Visually and effectively.

        :return: None
        """
        # visually
        self.field_image.put(data="Black", to=(1, 1, self.controller.field_size-1, self.controller.field_size-1))
        # effectively
        self.walls[1:-1, 1:-1] = 0

    def put_trace(self, trace, color):
        """
        Displays a trace of pixels on the canvas. One may have to update the tk mainloop.

        :param trace: list of tuple of size 2 of int or single tuple of size two.
        :param color: string
        :return:
        """
        if type(trace) is list:
            for pos in trace:
                self.field_image.put(color, pos)
        else:
            self.field_image.put(data=color, to=trace)

    def solve_round_end(self):
        """
        This function wraps up the task when a round ends by either one or no player surviving. This includes:
            1. Award the winner, if there is one.
            2. Check for game end and solve that accordingly.
                -> Prepare everything for the next round/game.
        :return: None
        """
        # -- Award Winner
        self.award_winner()
        # -- Check game end
        if self.check_game_end():
            self.set_buttons(state="off")
            game_winner = sorted(self.controller.players, key=lambda p: p.wins)[-1]
            self.label_info.config(text=str(game_winner.name) + "\nwins the game.\n Congratulations!")
        else:
            self.set_buttons(state="init")

    def check_round_end(self):
        """
        This function returns true, if the current round is over, meaning one ore no players are left alive unless
        it is a practice game. In that case the round only ends when no player is alive.

        :return: bool, True if round is over, False otherwise.
        """
        players_alive = [p for p in self.controller.players if p.alive]
        if len(players_alive) <= 1 and not self.practice_game:
            return True
        elif len(players_alive) == 0 and self.practice_game:
            return True
        else:
            return False

    def award_winner(self):
        """
        This function checks if the round is over and awards the winner of the round, if there is one.
        It also updates the leaderboard and displays a text naming the winning player.
        This function does nothing, if the round is not yet decided.

        :return: None
        """

        players_alive = [p for p in self.controller.players if p.alive]
        if len(players_alive) > 1:
            # Not decided
            return
        elif len(players_alive) == 0:
            # Draw
            self.label_info.config(text="Nobody wins\nround number " + str(self.current_round) + ".", fg="Black")
            return
        else:
            winner = players_alive[-1]
            winner.wins += 1
            # Update labels
            self.display_ranking()
            self.label_info.config(text=winner.name + "\nwins round number " + str(self.current_round) + ".",
                                   fg=winner.color)

    def check_game_end(self):
        """
        This function returns True if the current game is decided, meaning that one player has the maximum amount of
        required wins.

        :return: bool, True if teh game is over, False otherwise.
        """

        players_sorted = sorted(self.controller.players, key=lambda p: p.wins)  # ascending
        if len(players_sorted) > 0 and players_sorted[-1].wins >= self.max_wins:
            return True
        else:
            return False

    def reset_all_items(self):
        """
        Clears all items from the game field, deactivates all running effects and resets the item variables.
        :return: None
        """
        # -- Clean up item variables
        self.item_id = 1
        for tup in self.items_active:
            item, _ = tup
            item.deactivate()
        self.items_spawned = {}
        self.items_active = []
        self.items = zeros((self.controller.field_size, self.controller.field_size), dtype="int")

    # ########################################
    # Deprecated / legacy functions
    # ########################################

    def _update_visuals_deprecated(self, old_traces):
        """
        Draws the current position of each player on the canvas.

        :param old_traces: list of list of tuple of size 2, representing the pixels of each players old position.
        :return: None
        """
        # Draw player traces and dots.
        for p in self.controller.players:
            if not p.alive:
                continue
            old_trace = old_traces[p]
            # draw old position if player is alive and not flying
            if self.tick_count % self.gap_rate > self.gap_length and not p.flying:
                self.put_trace(trace=old_trace, color=p.color)
            else:
                self.put_trace(trace=old_trace, color="Black")  # Override the previously drawn white head
            # draw new player head
            if p.flying and self.tick_count % 4 in [2, 3]:
                # Player is flying. Do not print every 3rd and 4th head position.
                pass
            else:
                # Player is not flying. Print head as usual.
                self.put_trace(trace=p.dot_trace, color="White")

    def _move_deprecated(self):
        """
        This function moves every player by one step according to their current position, speed, angle and
        move command. It also updates the walls with the way traces and returns a list of all the old player positions.

        :return: dict of list of tuple of int of size 2.
        """
        old_way_traces = {}
        for p in self.controller.players:
            if not p.alive:
                continue
            if p.move_command == DIR_LEFT:
                p.angle = (p.angle - p.turn_rate) % 360
                player_moved_straight = False
            elif p.move_command == DIR_RIGHT:
                p.angle = (p.angle + p.turn_rate) % 360
                player_moved_straight = False
            # compute new position
            p.pos = self.get_target_pixel(pos=p.pos, dist=p.speed, angle=p.angle)
            player_moved_straight = True

            # reset move_command if players turn rate is set to RATE_RIGHT_ANGLE.
            if p.turn_rate == RATE_RIGHT_ANGLE:
                p.move_command = DIR_STRAIGHT

            # update new dot trace
            old_dot_trace = p.dot_trace
            old_way_traces[p] = old_dot_trace
            p.dot_trace = self.dot_trace(pos=p.pos, r=p.size)  # new dot trace at new position

            # update walls if...
            if (self.tick_count % self.gap_rate > self.gap_length  # it is not a tick where gaps are drawn &&
                    and (p.turn_rate != RATE_RIGHT_ANGLE or player_moved_straight)  # there was NOT a 90 degree turn &&
                    and not p.flying):  # player is not flying.
                for pix in [c for c in old_dot_trace if c not in p.dot_trace]:
                    self.walls[pix] = -1
        return old_way_traces

    def put_trace_by_function(self, func, rect):
        """
        This function draws color values given by the function func to a rectangle onto field_image.
        It cycles through every pixel of the rectangle calls func on it to determine the color of that pixel.
        The pixels coordinates are also forced to point on the field (modulo self.controller.field_size)

        This should perform better than 'put_trace' for each pixel in the players dot trace.
        See https://stackoverflow.com/questions/10417524/why-is-photoimage-put-slow for more info why this is faster.

        Use '#{:02x}{:02x}{:02x}'.format(*self.field_image.get(i, j)) in case of extracting a color from the field.

        :param func: Python function, tuple of size two of int -> color value (string or hex).
        :param rect: Tuple of size 4 of int defining upper left and lower right point of the rectangle.
        :return: None
        """

        a, b, x, y = rect

        # create data string.
        # Roll through every pixel of the square from (x-p.size, y-p.size) to (x+p.size, y+p.size) and decide its color.
        data_string = ""
        for i in range(a, x+1):  # x-axis roll-through
            data_string += "{"
            for j in range(b, y+1):  # y-axis roll-through
                data_string += func(i, j) + " "
            data_string += "} "
        self.field_image.put(data=data_string, to=rect)
