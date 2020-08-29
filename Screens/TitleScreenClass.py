
from tkinter import (Frame, Label, Button,
                     TOP, CENTER, BOTTOM, DISABLED)
from Screens import GameScreenClass as games


class TitleScreen(Frame):
    def __init__(self, controller, parent):
        Frame.__init__(self, master=parent)
        self.parent = parent
        self.controller = controller

        # canv = Canvas(master=self, width=100, height=100, bd=0, relief='ridge', highlightthickness=0)
        # canv.pack(side=TOP, anchor=CENTER)
        # img = PhotoImage(file=".png")
        # canv.image = img
        # canv.create_image(0, 0, anchor=NW, image=img)

        title_label = Label(master=self,
                            font=controller.font_bigger,
                            text="___Wall\n  Run___",
                            )

        subtitle_label = Label(master=self,
                               font=controller.font_big,
                               text="Main Menu",
                               )

        title_label.pack(side=TOP, anchor=CENTER,
                         pady=(int(5 * controller.scale), int(10 * controller.scale)))

        subtitle_label.pack(side=TOP, anchor=CENTER,
                            pady=(int(10 * controller.scale), int(30 * controller.scale)))

        button_setting = {"width": int(12 * controller.scale),
                          "height": int(3 * controller.scale),
                          "font": controller.font_medium,
                          }

        Button(master=self,
               text="New Game",
               command=self.new_game,
               cnf=button_setting,
               ).pack(side=TOP, anchor=CENTER)

        Button(master=self,
               text="Practice",
               command=self.new_practice_game,
               cnf=button_setting,
               ).pack(side=TOP, anchor=CENTER, pady=(0,10))

        Button(master=self,
               text="Options",
               command=lambda: controller.show_frame("Options"),
               cnf=button_setting,
               ).pack(side=TOP, anchor=CENTER)

        # Button(master=self,
        #        text="Rules",
        #        command=lambda: controller.show_frame("Rules"),
        #        state=DISABLED,
        #        cnf=button_setting,
        #        ).pack(side=TOP, anchor=CENTER)

        Button(master=self,
               text="Exit",
               command=controller.exit_session,
               cnf=button_setting,
               ).pack(side=TOP, anchor=CENTER, pady=50)

        Label(master=self,
              text="Johannes Buchholz 2020",
              font=("Helvetica", 8)
              ).pack(side=BOTTOM, anchor=CENTER)

    def new_game(self):
        """
        Creates a new game screen and brings it to the front.

        :return: None
        """
        self.controller.frames["Game"] = games.GameScreen(parent=self.parent, controller=self.controller)
        self.controller.frames["Game"].grid(row=0, column=0, sticky="nsew")
        self.controller.frames["Game"].set_buttons(state="init")  # Initialise buttons on the game screen.
        self.controller.show_frame("Game")

    def new_practice_game(self):
        """
        Creates a new game screen and brings it to the front. Enables practice mode.
        :return: None
        """
        self.controller.frames["Game"] = games.GameScreen(parent=self.parent, controller=self.controller)
        self.controller.frames["Game"].grid(row=0, column=0, sticky="nsew")
        self.controller.frames["Game"].set_buttons(state="init")  # Initialise buttons on the game screen.
        self.controller.frames["Game"].practice_game = True  # Enable practice mode
        self.controller.frames["Game"].label_title.config(text="___Wall\n  Run___\n\nPractice Mode")  # Set title
        self.controller.show_frame("Game")


