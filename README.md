# Wall Run: "Achtung, die Kurve!"

This is an interpretation of the game "Achtung die Kurve", purely written in python3 and playable for up to six players - all on one single keyboard.

Highlights:
- Up to six-player action on one keyboard
- Choose from up to 17 powerups
- Take screenshots of your most glorious victories
- Mouse-free gameplay thanks to pause and resume function on space bar

![displaying wallrun menu](resources/wallrun_menu.png "wallrun menu")
![dsiblaying an active wallrun game](resources/wallrun_game.png "wallrun game")
![dsiblaying wallrun option menu](resources/wallrun_options.png "wallrun options")

# How to install

1. Clone this repository.
2. Create a virtual environment inside the repository and activate it.
3. Install the required packages provided within the `requirements.txt` file by running
    ```bash
    pip3 install -r requirements.txt
    ```
4. Start the programm by running
    ```bash
    python3 __main__.py
    ```
   or
    ```bash
    python3 /<absolute path to direcory>/WallRun
    ```

## Requirements

- python 3

The following packages are required:

- numpy (>=1.19.1)
- pynput (>=1.6.8)

The ui is based on tkinter which should already be included in your python installation.
