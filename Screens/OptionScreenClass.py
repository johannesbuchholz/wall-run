
from tkinter import (Frame, Label, Button, Entry, IntVar, Radiobutton, PhotoImage,
                     TOP,
                     )
from pynput import keyboard
from FieldObjects import PlayerClass as pc


class OptionScreen(Frame):
    def __init__(self, controller, parent):
        Frame.__init__(self, master=parent)
        self.parent = parent
        self.controller = controller
        # #########################################################
        # -- Player attributes
        # #########################################################
        self.p1 = {"name": "P1", "color": "Red",
                   "keys": {"left": keyboard.Key.left, "right": keyboard.Key.right},
                   "active": True,
                   "toggle": lambda: self.toggle_player(0),
                   "adjust": lambda: self.change_keys(0),
                   }
        self.p2 = {"name": "P2", "color": "Blue",
                   "keys": {"left": keyboard.KeyCode(char='n'), "right": keyboard.KeyCode(char='m')},
                   "active": True,
                   "toggle": lambda: self.toggle_player(1),
                   "adjust": lambda: self.change_keys(1),
                   }
        self.p3 = {"name": "P3", "color": "Green",
                   "keys": {"left": keyboard.KeyCode(char='y'), "right": keyboard.KeyCode(char='x')},
                   "active": True,
                   "toggle": lambda: self.toggle_player(2),
                   "adjust": lambda: self.change_keys(2),
                   }
        self.p4 = {"name": "P4", "color": "Purple",
                   "keys": {"left": keyboard.KeyCode(char='1'), "right": keyboard.KeyCode(char='q')},
                   "active": True,
                   "toggle": lambda: self.toggle_player(3),
                   "adjust": lambda: self.change_keys(3),
                   }
        self.p5 = {"name": "P5", "color": "Cyan",
                   "keys": {"left": keyboard.KeyCode(char='0'), "right": keyboard.KeyCode(char=',')},
                   "active": True,
                   "toggle": lambda: self.toggle_player(4),
                   "adjust": lambda: self.change_keys(4),
                   }
        self.p6 = {"name": "P6", "color": "Orange",
                   "keys": {"left": keyboard.KeyCode(char='6'), "right": keyboard.KeyCode(char='9')},
                   "active": True,
                   "toggle": lambda: self.toggle_player(5),
                   "adjust": lambda: self.change_keys(5),
                   }
        self.p_options = [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]

        # -- Button configs
        cnf_button_toggle_player = {"width": 6, "height": 3, "borderwidth": 2, "font": self.controller.font_medium}
        cnf_label_keys = {"width": 5, "height": 2, "borderwidth":2}
        cnf_button_adjust = {"width": 10, "height": 1, "borderwidth": 2}
        cnf_button_item = {"width": 100, "height": 40, "borderwidth": 1}
        cnf_button_thin1 = {"width": 10, "height": 1, "borderwidth": 1}

        # -- Labels
        Label(master=self, text="Options", font=self.controller.font_bigger)\
            .grid(row=1, column=1, pady=10)
        Label(master=self, text="Name", font=self.controller.font_medium)\
            .grid(row=3, column=1, columnspan=1, pady=10)
        Label(master=self, text="Keys", font=self.controller.font_medium)\
            .grid(row=4, column=1, columnspan=1, pady=10)
        Label(master=self, text="Max rounds", font=self.controller.font_medium)\
            .grid(row=6, column=1, columnspan=1, pady=10)
        Label(master=self, text="Items", font=self.controller.font_medium) \
            .grid(row=7, column=1, columnspan=1, pady=10)
        Button(master=self, text="Toggle All", command=self.toggle_all_item_buttons) \
            .grid(row=8, column=1, pady=10)

        # -- Buttons and fields regarding players specific options
        self.toggle_buttons = []
        self.name_fields = []
        self.adjust_buttons = []
        self.key_labels_left = []
        self.key_labels_right = []
        for p, i in zip(self.p_options, range(1, 7)):
            # toggle Button
            button_toggle = Button(master=self, text=str(i), command=p["toggle"],
                                   fg=p["color"], activeforeground=p["color"],
                                   relief="sunken",
                                   cnf=cnf_button_toggle_player)
            button_toggle.grid(row=2, column=2*i, columnspan=2)
            self.toggle_buttons.append(button_toggle)
            # name field
            entry_field = Entry(master=self, bd=1, width=14)
            entry_field.insert(0, p["name"])
            entry_field.grid(row=3, column=2*i, columnspan=2, padx=8)
            self.name_fields.append(entry_field)
            # direction labels
            try:
                label_left = Label(master=self, text=p["keys"]["left"].char, relief="ridge", cnf=cnf_label_keys)
                label_right = Label(master=self, text=p["keys"]["right"].char, relief="ridge", cnf=cnf_label_keys)
            except AttributeError:
                label_left = Label(master=self, text=str(p["keys"]["left"])[4:], relief="ridge", cnf=cnf_label_keys)
                label_right = Label(master=self, text=str(p["keys"]["right"])[4:], relief="ridge", cnf=cnf_label_keys)
            self.key_labels_left.append(label_left)
            self.key_labels_right.append(label_right)
            label_left.grid(row=4, column=i*2)
            label_right.grid(row=4, column=i*2+1)
            # key chooser
            button_key = Button(master=self, text="Adjust", command=p["adjust"],
                                cnf=cnf_button_adjust)
            button_key.grid(row=5, column=2*i, columnspan=2, pady=6)
            self.adjust_buttons.append(button_key)

        # -- Round chooser
        self.max_round = IntVar(master=self, value=5)
        for i, j in zip(range(5, 31, 5), range(1, 7)):
            round_button = Radiobutton(master=self, text=str(i), variable=self.max_round, value=i, indicatoron=0,
                                       width=12, height=2)
            round_button.grid(row=6, column=2*j, columnspan=2, pady=6)

        # -- Item selection
        self.item_toggle_functions = {name: lambda name=name: self.toggle_item(name)
                                      for name in self.controller.item_names
                                      }
        self.item_buttons = {}
        self.item_icons = []
        self.item_names_to_apply = self.controller.item_names  # list of item names that is transmitted by self.apply
        items_per_row = 6
        column_offset = 2
        for item_name, i in zip(self.controller.all_items, range(len(self.controller.all_items))):
            name_short = item_name.replace("Item", "")
            # Icon
            icon = PhotoImage(file="./Data/Icon{}.png".format(name_short))
            self.item_icons.append(icon)
            # Button
            button_item = Button(master=self, text=name_short, relief="sunken",
                                 command=self.item_toggle_functions[item_name],
                                 image=icon, compound=TOP,
                                 cnf=cnf_button_item
                                 )
            button_item.grid(row=7+int(i/items_per_row),
                             column=column_offset+(2 * i) % (items_per_row * 2),
                             columnspan=2)
            self.item_buttons[item_name] = button_item

        # Back and Apply
        self.bback = Button(master=self, text="Back", command=self.back, cnf=cnf_button_thin1)
        self.bback.grid(row=20, column=6, columnspan=2, pady=50)
        self.bapply = Button(master=self, text="Apply", command=self.apply, cnf=cnf_button_thin1)
        self.bapply.grid(row=20, column=8, columnspan=2, pady=50)
        # Listener
        self.listener_adjust = None  # Will be defined in make_listener
        self.new_keys = []

    # #########################################################
    # ----- Button Functions
    # #########################################################

    def back(self):
        # remove focus
        self.focus_set()
        # turn of listeners if running
        try:
            self.listener_adjust.stop()
            self.listener_adjust.join()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        # reset buttons
        for b in self.adjust_buttons:
            b.config(borderwidth=2, relief="raised")
        self.controller.show_frame("Title")

    def apply(self):
        # remove focus
        self.focus_set()
        # turn of listeners if running
        try:
            self.listener_adjust.stop()
            self.listener_adjust.join()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        # reset adjust buttons
        for b in self.adjust_buttons:
            b.config(borderwidth=2, relief="raised")
        # get names
        for i in range(6):
            self.p_options[i]["name"] = self.name_fields[i].get()[0:18]  # Max 18 characters
        # Create players with chosen settings
        players = []
        for p in self.p_options:
            if p["active"]:
                players.append(pc.Player(name=p["name"], color=p["color"], keys=p["keys"]))
        # Transfer settings to controller
        self.controller.max_rounds = self.max_round.get()
        self.controller.players = players
        self.controller.show_frame("Title")
        self.controller.item_names = self.item_names_to_apply

    # ############################
    # Toggling players
    # ############################
    def toggle_player(self, i):
        """
        Turns off and on the ith player of in the p_options list.
        """
        entry = self.p_options[i]
        entry["active"] = not entry["active"]
        if entry["active"]:
            self.toggle_buttons[i].config(borderwidth=2, relief="sunken")
        else:
            self.toggle_buttons[i].config(borderwidth=2, relief="raised")

    # ############################
    # Toggling items
    # ############################
    def toggle_item(self, item_name):
        """
        Appends or removes the the string item_name from self.controller.item_names.
        """
        if item_name in self.item_names_to_apply:
            # Remove item
            self.item_names_to_apply.remove(item_name)
            self.item_buttons[item_name].config(relief="raised")
        else:
            # Add item
            self.item_names_to_apply.append(item_name)
            self.item_buttons[item_name].config(relief="sunken")

    def toggle_all_item_buttons(self):
        """
        Toggles each item button once.
        """
        for item_name in self.controller.all_items:
            self.toggle_item(item_name)

    # ############################
    # Direction-Keys related
    # ############################
    def make_listener(self, i):
        """
        Makes a listener for player i (0 to 5) that records the next two key presses. First press becomes left command,
        second one becomes right command.
        :param i:
        :return: None
        """
        self.new_keys = []
        # Delete old listeners if active
        try:
            self.listener_adjust.stop()
            self.listener_adjust.join()
        except RuntimeError:
            pass
        except AttributeError:
            pass
        # Reset button optic
        for b in self.adjust_buttons:
            b.config(borderwidth=2, relief="raised")
        self.adjust_buttons[i].config(borderwidth=2, relief="ridge")

        def on_press(key):
            if key == keyboard.Key.esc:
                # Reset the buttons and turn of listener
                for b in self.adjust_buttons:
                    b.config(borderwidth=2, relief="raised")
                return False
            self.new_keys.append(key)
            # print("Pressed:", key)
            if len(self.new_keys) >= 2:
                self.transfer_key_queue(i)
                return False

        self.listener_adjust = keyboard.Listener(on_press=on_press)

    def transfer_key_queue(self, i):
        left = self.new_keys[0]
        right = self.new_keys[1]
        self.p_options[i]["keys"] = {"left": left, "right": right}
        # Update the control labels
        try:
            self.key_labels_left[i].config(text=left.char)
            self.key_labels_right[i].config(text=right.char)
        except AttributeError:
            self.key_labels_left[i].config(text=str(left)[4:])
            self.key_labels_right[i].config(text=str(right)[4:])
        # Reset button
        self.adjust_buttons[i].config(borderwidth=2, relief="raised")
        # Turn of teh current listeners
        try:
            self.listener_adjust.stop()
            self.listener_adjust.join()
        except RuntimeError:
            pass
        except AttributeError:
            pass

    def change_keys(self, i):
        """
        Creates a keyboard listener that records the next two keys pressed and changes the command keys of the ith
        player to these keys.
        :param i: change keys of ith player (0 to 5) as int.
        :return: None
        """
        # remove focus from any name field
        self.focus_set()
        # make listener
        self.make_listener(i)
        self.listener_adjust.start()
