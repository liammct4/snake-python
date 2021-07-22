import tkinter as tk
from tkinter import messagebox
from enum import Enum
import time
import random


class InputControl(Enum):
	"""
	Enum class which contains all the directions for the game, this used for the direction
	variable in the SnakeGame class.
	"""
	NONE = 0,
	UP = 1,
	DOWN = 2,
	LEFT = 3,
	RIGHT = 4


class Snake():
	"""
	The snake game class, creating a Snake object will open a new snake window.
	"""
	def __init__(self):
		self.root = tk.Tk()
		width, height = 500, 543
		x = int((self.root.winfo_screenwidth() / 2) - (width / 2))
		y = int((self.root.winfo_screenheight() / 2) - (height / 2))
		self.root.geometry(f"{width}x{height}+{x}+{y}")
		self.root.title("Snake")
		self.root.resizable(False, False)
		self.root.rowconfigure(1, weight=1)
		self.root.columnconfigure(0, weight=1)

		self.TIME_BETWEEN_UPDATES = 150
		self.gamePaused = False
		self.score = tk.IntVar(self.root)
		self.timeStart = time.time()
		self.timePlayed = 0
		self.gameLose = False
		self.backgroundColour = "#212121"
		self.snakeBodyColour = "#ffff00"
		if self.snakeBodyColour == "#ff0000":
			raise RuntimeError("Cannot have snake colour same as food colour.")

		# Game widgets and scores
		self.gameBoard = tk.Frame(self.root, bg=self.backgroundColour)
		self.gameBoard.grid(row=1, column=0, sticky=tk.NSEW)
		self.scoreCard = tk.Label(self.root, textvariable=self.score, font=("Century Gothic", 20, "bold"), bg="#424242", fg="#fafafa")
		self.scoreCard.grid(row=0, column=0, sticky=tk.NSEW)
		self.pausedLabel = tk.Label(self.root, text="[GAME PAUSED]\nPress any key to continue", font=("Century Gothic", 15, "bold"), bg=self.backgroundColour, fg="#ff0000")

		self.gridColumns = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
		self.snakeBody = [[9, 7], [10, 7], [11, 7], [12, 7]]
		self.direction = InputControl.NONE
		self.foodCoords = [7, 7]

		# Keyboard keymaps
		self.keymap = { 
			'w' : InputControl.UP,
			's' : InputControl.DOWN, 
			'a' : InputControl.LEFT, 
			'd' : InputControl.RIGHT
		}

		self.oppositeDirections = { 
			InputControl.NONE : 0,
			InputControl.UP :  InputControl.DOWN,
			InputControl.DOWN : InputControl.UP,
			InputControl.LEFT : InputControl.RIGHT,
			InputControl.RIGHT : InputControl.LEFT
		}

		self.directionMovementTransformations = {
			InputControl.NONE : [0, 0],
			InputControl.UP : [0, -1],
			InputControl.DOWN : [0, 1],
			InputControl.LEFT : [-1, 0],
			InputControl.RIGHT : [1, 0]
		}

		self.root.bind("<Key>", self.key_press_event)
		self.root.bind("<Pause>", self.game_pause_event)
		self.construct_Game()

		self.root.after(self.TIME_BETWEEN_UPDATES, self.update_game_board)
		self.root.mainloop()


	def construct_Game(self):
		""" 
		Used to create all the grid squares on the game board, only called once at runtime.
		"""
		self.gameBoard.rowconfigure(tuple(range(15)), weight=1)
		self.gameBoard.columnconfigure(tuple(range(15)), weight=1)

		for row in range(15):
			for column in range(15):
				self.gridSquare = tk.Frame(self.gameBoard, bg=self.backgroundColour)
				self.gridSquare.grid(row=row, column=column, sticky=tk.NSEW, padx=1, pady=1)
				self.gridColumns[column].append(self.gridSquare)

		for i in range(9, 13):
			self.gridColumns[i][7].config(bg=self.snakeBodyColour)

		self.gridColumns[self.foodCoords[0]][self.foodCoords[1]].config(bg="#ff0000")


	def generate_food(self):
		""" 
		Generates a random x, y coordinate on the game board for food, 
		will continue to generate until a coordinate which is not occupied is found on the board.
		"""
		foodIsInEmptySpace = False
		while not foodIsInEmptySpace:
			self.foodCoords[0] = random.randint(0, 14)
			self.foodCoords[1] = random.randint(0, 14)

			if (self.gridColumns[self.foodCoords[0]][self.foodCoords[1]].cget("bg") == self.backgroundColour):
				self.gridColumns[self.foodCoords[0]][self.foodCoords[1]].config(bg="#ff0000")
				foodIsInEmptySpace = True


	def update_game_board(self):
		""" 
		Function which is called once then calls itself which acts as the game loop. Updates the snake by
		moving it in the direction of the direction variable, this will also check for any collisions and raise
		an exception handled by another function.
		"""
		self.turnDirection = self.direction

		if not self.root.focus_displayof() or self.gamePaused or self.gameLose:
			self.root.after(1000, self.update_game_board)
			if not self.gamePaused:
				self.game_pause_event(True)
				self.gamePaused = True
			return

		if self.direction == InputControl.NONE:
			self.root.after(self.TIME_BETWEEN_UPDATES, self.update_game_board)
			return

		snakeHeadPreviousCoordinates = [self.snakeBody[0][0], self.snakeBody[0][1]]
		self.snakeBody.insert(0, snakeHeadPreviousCoordinates)
		self.gridColumns[self.snakeBody[1][0]][self.snakeBody[1][1]].grid(column=self.snakeBody[1][0], row=self.snakeBody[1][1], padx=1, pady=1)

		movementTransformation = self.directionMovementTransformations[self.direction]
		self.snakeBody[0][0] += movementTransformation[0]
		self.snakeBody[0][1] += movementTransformation[1]

		self.gridColumns[self.snakeBody[-1][0]][self.snakeBody[-1][1]].config(bg=self.backgroundColour)

		try:
			if (self.snakeBody[0][0] < 0 or self.snakeBody[0][1] < 0):
				raise RuntimeError("Game over, ran into wall.")
			elif (self.gridColumns[self.snakeBody[0][0]][self.snakeBody[0][1]].cget("bg") == self.snakeBodyColour and self.direction != InputControl.NONE):
				raise RuntimeError("Game over, ran into self.")
		except (IndexError, RuntimeError):
			self.game_lose_event()
			return

		if (self.gridColumns[self.snakeBody[0][0]][self.snakeBody[0][1]].cget("bg") == "#ff0000"):
			self.gridColumns[self.snakeBody[-1][0]][self.snakeBody[-1][1]].config(bg=self.snakeBodyColour)
			self.score.set(self.score.get() + 1)
			self.scoreCard.config(text=self.score)
			self.generate_food()
		else:
			self.snakeBody.pop()

		self.gridColumns[self.snakeBody[0][0]][self.snakeBody[0][1]].config(bg=self.snakeBodyColour)
		self.root.after(self.TIME_BETWEEN_UPDATES, self.update_game_board)


	def key_press_event(self, event):
		"""
		Handles key presses, if the key pressed is either W, A, S or D, 
		the direction variable will be updated. Also handles pressing the pause key
		by either pausing or unpausing the game.
		"""
		if self.gameLose:
			return

		key = event.char.lower()

		self.gamePaused = False
		self.game_pause_event(False)

		startGameRight = self.direction == InputControl.NONE and key == "d"
		if key not in self.keymap:
			return

		oppositeDirection = self.keymap[key] == self.oppositeDirections[self.direction]
		turnOppositeDirection = self.keymap[key] == self.oppositeDirections[self.turnDirection]
		if startGameRight or oppositeDirection or turnOppositeDirection:
			return

		self.direction = self.keymap[key]


	def show_game_over_message(self):
		"""
		Called when the player has lost. When called, a game over message box
		will appear asking the player to replay (resets the game) or cancel (closes the game).
		"""
		self.message = tk.Toplevel()
		self.message.title("Game Over")
		x = (self.root.winfo_x() + (self.root.winfo_width() / 2)) - (150)
		y = (self.root.winfo_y() + (self.root.winfo_height() / 2)) - (60)
		self.message.geometry('%dx%d+%d+%d' % (300, 120, x, y))	

		self.message.resizable(False, False)
		self.message.columnconfigure(0, weight=1)
		self.message.config(bg=self.backgroundColour)
		self.message.attributes("-topmost", True)

		self.message.protocol("WM_DELETE_WINDOW", self.root.destroy)

		gameOverTitle = tk.Label(self.message, text="Game Over", font=("Century Gothic", 15, "bold"), bg=self.backgroundColour, fg="#f00")
		gameOverTitle.grid(row=0, column=0, sticky=tk.N + tk.E + tk.W)

		scoreLabel = tk.Label(self.message, text=f"Final Score: {self.score.get()}\nTime Played: {self.timePlayed}s", font=("Century Gothic", 10, "bold"), bg=self.backgroundColour, fg="#fff")
		scoreLabel.grid(row=1, column=0)

		buttons = tk.Frame(self.message, bg="#424242", width=150, height=25)
		retryButton = tk.Button(buttons, text="Retry", width=8, bg=self.backgroundColour, font=("Century Gothic", 10, "bold"), fg="white", activebackground="#2C2C2C", activeforeground="white", relief=tk.FLAT, command=self.game_over_replay)
		cancelButton = tk.Button(buttons, text="Cancel", width=8, bg=self.backgroundColour, font=("Century Gothic", 10, "bold"), fg="white", activebackground="#2C2C2C", activeforeground="white", relief=tk.FLAT, command=self.root.destroy)
		tk.Frame(buttons, bg=self.backgroundColour, width=20).grid(row=0, column=1, sticky=tk.NSEW)

		buttons.columnconfigure((0, 2), weight=1)

		buttons.grid(row=2, column=0, pady=(15, 0))
		retryButton.grid(row=0, column=0, padx=1, pady=1, sticky=tk.E)
		cancelButton.grid(row=0, column=2, padx=1, pady=1, sticky=tk.W)


	def game_lose_event(self):
		"""
		Handles a raised exception in the game loop for when the game is over, 
		This will make the snake disappear and calculate the time between the game starting and 
		when this function was callled. Also calls function "show_game_over_message" 
		which will show a game over message.
		"""
		self.gameLose = True
		self.timePlayed = round(time.time() - self.timeStart, 2)
		for i in self.snakeBody:
			if i[0] == 15 or i[1] == 15:
				continue
			self.gridColumns[i[0]][i[1]].config(bg=self.backgroundColour)

		self.show_game_over_message()


	def game_over_replay(self):
		"""
		For when a player has selected the replay option on the game over message box.
		This will reset everything back to their default positions as if the game was launched
		from new.
		"""
		self.gameLose = False
		self.message.destroy()

		for column in self.gridColumns:
			for gridSquare in column:
				gridSquare.config(bg=self.backgroundColour)

		self.snakeBody = [[9, 7], [10, 7], [11, 7], [12, 7]]
		self.direction = InputControl.NONE
		self.score.set(0)
		self.timeStart = time.time()
		self.scoreCard.config(text=0)

		for i in range(9, 13):
			self.gridColumns[i][7].config(bg=self.snakeBodyColour)

		self.foodCoords = [7, 7]
		self.gridColumns[self.foodCoords[0]][self.foodCoords[1]].config(bg="#ff0000")
		self.root.after(self.TIME_BETWEEN_UPDATES, self.update_game_board)


	def game_pause_event(self, isPause = True):
		"""
		Called when handling pause events, handles pausing and unpausing the game. Pausing the game
		will show a label saying "Game Paused" and will also prevent any movement from occuring.
		"""
		if self.gameLose:
			return

		if isPause and not self.gamePaused:
			for i in range(0, len(self.snakeBody)):
				self.gridColumns[self.snakeBody[i][0]][self.snakeBody[i][1]].config(bg="#7E7E00")
				self.pausedLabel.grid(row=1, column=0)
			self.gamePaused = True
			return

		for i in range(0, len(self.snakeBody)):
			self.gridColumns[self.snakeBody[i][0]][self.snakeBody[i][1]].config(bg=self.snakeBodyColour)

		self.pausedLabel.grid_forget()
		self.gamePaused = False


if __name__ == "__main__":
	game = Snake()