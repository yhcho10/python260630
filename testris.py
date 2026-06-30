#cmd
#pip install pygame
import random
import tkinter as tk


SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "L": [[1, 0, 0], [1, 1, 1]],
    "J": [[0, 0, 1], [1, 1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
}

COLORS = {
    "I": "#00E5FF",
    "O": "#FFD600",
    "S": "#00E676",
    "Z": "#FF3D00",
    "L": "#FF9100",
    "J": "#2979FF",
    "T": "#AA00FF",
}


class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.root.resizable(False, False)

        self.width = 10
        self.height = 20
        self.cell = 24
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.level = 1
        self.running = True
        self.paused = False
        self.current_piece = None
        self.next_shape = None
        self.drop_delay = 500

        self.create_ui()
        self.new_game()

    def create_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=self.width * self.cell,
            height=self.height * self.cell,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        self.info_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.info_frame.grid(row=0, column=1, sticky="n", padx=(0, 10), pady=10)

        self.score_label = tk.Label(
            self.info_frame,
            text="점수: 0",
            font=("맑은 고딕", 14, "bold"),
            fg="#ffffff",
            bg="#1e1e1e",
        )
        self.score_label.pack(anchor="w", pady=(0, 10))

        self.level_label = tk.Label(
            self.info_frame,
            text="레벨: 1",
            font=("맑은 고딕", 12),
            fg="#ffffff",
            bg="#1e1e1e",
        )
        self.level_label.pack(anchor="w", pady=(0, 10))

        self.next_label = tk.Label(
            self.info_frame,
            text="다음 블록",
            font=("맑은 고딕", 12, "bold"),
            fg="#ffffff",
            bg="#1e1e1e",
        )
        self.next_label.pack(anchor="w")

        self.next_canvas = tk.Canvas(
            self.info_frame,
            width=6 * self.cell,
            height=6 * self.cell,
            bg="#111111",
            highlightthickness=0,
        )
        self.next_canvas.pack(pady=5)

        self.help_label = tk.Label(
            self.info_frame,
            text="← → 이동\n↓ 빠르게↓\n↑ 회전\nP 일시정지\nEsc 종료",
            font=("맑은 고딕", 10),
            justify="left",
            fg="#cccccc",
            bg="#1e1e1e",
        )
        self.help_label.pack(anchor="w", pady=(10, 0))

        self.root.bind("<Left>", lambda event: self.move_piece(-1, 0))
        self.root.bind("<Right>", lambda event: self.move_piece(1, 0))
        self.root.bind("<Down>", lambda event: self.soft_drop())
        self.root.bind("<Up>", lambda event: self.rotate_piece())
        self.root.bind("<p>", lambda event: self.toggle_pause())
        self.root.bind("<P>", lambda event: self.toggle_pause())
        self.root.bind("<Escape>", lambda event: self.quit_game())

    def new_game(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.level = 1
        self.running = True
        self.paused = False
        self.current_piece = None
        self.next_shape = random.choice(list(SHAPES.keys()))
        self.spawn_piece()
        self.update_status()
        self.draw_board()
        self.start_loop()

    def start_loop(self):
        self.root.after(self.drop_delay, self.auto_drop)

    def auto_drop(self):
        if not self.running or self.paused:
            return

        if self.move_piece(0, 1, check_only=True):
            self.move_piece(0, 1)
        else:
            self.lock_piece()
            self.clear_lines()
            self.spawn_piece()

        self.draw_board()
        self.root.after(max(100, self.drop_delay - (self.level - 1) * 40), self.auto_drop)

    def spawn_piece(self):
        shape_name = self.next_shape or random.choice(list(SHAPES.keys()))
        self.next_shape = random.choice(list(SHAPES.keys()))
        self.current_piece = {
            "shape": shape_name,
            "matrix": [row[:] for row in SHAPES[shape_name]],
            "x": self.width // 2 - 2,
            "y": 0,
        }

        if self.is_collision(self.current_piece):
            self.running = False
            self.draw_board()
            self.show_game_over()
            return None

        self.draw_next_piece()
        return self.current_piece

    def move_piece(self, dx, dy, check_only=False):
        if not self.current_piece or not self.running or self.paused:
            return False

        new_x = self.current_piece["x"] + dx
        new_y = self.current_piece["y"] + dy
        candidate = {
            "shape": self.current_piece["shape"],
            "matrix": self.current_piece["matrix"],
            "x": new_x,
            "y": new_y,
        }

        if self.is_collision(candidate):
            if dy == 1 and not check_only:
                self.lock_piece()
                self.clear_lines()
                self.spawn_piece()
            return False

        if not check_only:
            self.current_piece["x"] = new_x
            self.current_piece["y"] = new_y
            self.draw_board()
        return True

    def soft_drop(self):
        if self.move_piece(0, 1):
            self.score += 1
            self.update_status()

    def rotate_piece(self):
        if not self.current_piece or not self.running or self.paused:
            return

        rotated = [list(row) for row in zip(*self.current_piece["matrix"][::-1])]
        candidate = {
            "shape": self.current_piece["shape"],
            "matrix": rotated,
            "x": self.current_piece["x"],
            "y": self.current_piece["y"],
        }

        if not self.is_collision(candidate):
            self.current_piece["matrix"] = rotated
            self.draw_board()

    def is_collision(self, piece):
        for row_idx, row in enumerate(piece["matrix"]):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue

                nx = piece["x"] + col_idx
                ny = piece["y"] + row_idx

                if nx < 0 or nx >= self.width or ny >= self.height:
                    return True
                if ny >= 0 and self.board[ny][nx] != 0:
                    return True
        return False

    def lock_piece(self):
        if not self.current_piece:
            return

        for row_idx, row in enumerate(self.current_piece["matrix"]):
            for col_idx, cell in enumerate(row):
                if not cell:
                    continue
                nx = self.current_piece["x"] + col_idx
                ny = self.current_piece["y"] + row_idx
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    self.board[ny][nx] = self.current_piece["shape"]

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        cleared = self.height - len(new_board)
        while len(new_board) < self.height:
            new_board.insert(0, [0 for _ in range(self.width)])
        self.board = new_board

        if cleared > 0:
            self.score += [0, 100, 300, 500, 800][cleared]
            self.level = 1 + self.score // 1000
            self.update_status()

    def draw_board(self):
        self.canvas.delete("all")

        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != 0:
                    color = COLORS[self.board[y][x]]
                    self.canvas.create_rectangle(
                        x * self.cell,
                        y * self.cell,
                        (x + 1) * self.cell,
                        (y + 1) * self.cell,
                        fill=color,
                        outline="#333333",
                        width=1,
                    )

        if self.current_piece:
            for row_idx, row in enumerate(self.current_piece["matrix"]):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = self.current_piece["x"] + col_idx
                        y = self.current_piece["y"] + row_idx
                        if 0 <= y < self.height and 0 <= x < self.width:
                            self.canvas.create_rectangle(
                                x * self.cell,
                                y * self.cell,
                                (x + 1) * self.cell,
                                (y + 1) * self.cell,
                                fill=COLORS[self.current_piece["shape"]],
                                outline="#ffffff",
                                width=1,
                            )

    def draw_next_piece(self):
        self.next_canvas.delete("all")
        shape_name = self.next_shape
        matrix = SHAPES[shape_name]
        size = max(len(row) for row in matrix)
        cell_size = self.cell - 4
        offset_x = (6 * self.cell - size * cell_size) // 2
        offset_y = (6 * self.cell - len(matrix) * cell_size) // 2

        for row_idx, row in enumerate(matrix):
            for col_idx, cell in enumerate(row):
                if cell:
                    self.next_canvas.create_rectangle(
                        offset_x + col_idx * cell_size,
                        offset_y + row_idx * cell_size,
                        offset_x + (col_idx + 1) * cell_size,
                        offset_y + (row_idx + 1) * cell_size,
                        fill=COLORS[shape_name],
                        outline="#ffffff",
                        width=1,
                    )

    def update_status(self):
        self.score_label.config(text=f"점수: {self.score}")
        self.level_label.config(text=f"레벨: {self.level}")

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.canvas.create_text(
                self.width * self.cell / 2,
                self.height * self.cell / 2,
                text="일시정지",
                fill="#ffffff",
                font=("맑은 고딕", 24, "bold"),
                tags="overlay",
            )
        else:
            self.canvas.delete("overlay")
            self.draw_board()

    def show_game_over(self):
        self.canvas.create_text(
            self.width * self.cell / 2,
            self.height * self.cell / 2,
            text="게임 오버",
            fill="#ff5252",
            font=("맑은 고딕", 24, "bold"),
            tags="overlay",
        )

    def quit_game(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
