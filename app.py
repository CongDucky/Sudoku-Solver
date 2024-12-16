from tkinter import Tk, Frame, Button, Entry, Label, messagebox
import numpy as np

# Khởi tạo dữ liệu toàn cục
entries = []
user_entries = np.zeros((9, 9), dtype=int)
steps = []
current_step = 0

def setup_ui(root):
    global entries
    # Tiêu đề
    title_label = Label(root, text="Sudoku Solver", font=("Arial", 24, "bold"), fg="darkblue")
    title_label.grid(row=0, column=0, columnspan=3, pady=10)

    # Tạo lưới Sudoku
    grid_frame = Frame(root)
    grid_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    for i in range(9):
        row_entries = []
        for j in range(9):
            bg_color = "white"
            if (i // 3 + j // 3) % 2 == 1:  # Alternate màu sắc cho lưới 3x3
                bg_color = "lightgray"
            entry = Entry(grid_frame, width=2, font=("Arial", 18), justify="center", bg=bg_color)
            entry.grid(row=i, column=j, padx=(2 if j % 3 else 4), pady=(2 if i % 3 else 4))
            row_entries.append(entry)
        entries.append(row_entries)

    # Tạo các nút chức năng
    button_frame = Frame(root)
    button_frame.grid(row=2, column=0, columnspan=3, pady=10)

    Button(button_frame, text="Check", command=check_grid, font=("Arial", 14), bg="orange", width=15).grid(
        row=0, column=0, padx=10, pady=5
    )
    Button(button_frame, text="Solve Step by Step", command=solve_step_by_step, font=("Arial", 14), bg="lightblue", width=15).grid(
        row=0, column=1, padx=10, pady=5
    )
    Button(button_frame, text="Solve All", command=solve_all, font=("Arial", 14), bg="green", fg="white", width=15).grid(
        row=0, column=2, padx=10, pady=5
    )
    Button(button_frame, text="Reset", command=reset_grid, font=("Arial", 14), bg="red", fg="white", width=15).grid(
        row=1, column=1, padx=10, pady=5
    )

    Button(button_frame, text="Previous", command=previous_step, font=("Arial", 14), bg="lightgrey", width=15).grid(
        row=1, column=0, padx=10, pady=5
    )
    Button(button_frame, text="Next", command=next_step, font=("Arial", 14), bg="lightgreen", width=15).grid(
        row=1, column=2, padx=10, pady=5
    )

    # Nhãn hiển thị bước
    global step_label
    step_label = Label(root, text="Step: 0/0", font=("Arial", 14), fg="darkblue")
    step_label.grid(row=3, column=0, columnspan=3, pady=10)

def reset_grid():
    """Xóa toàn bộ dữ liệu và trạng thái của lưới"""
    global user_entries, steps, current_step
    for i in range(9):
        for j in range(9):
            entries[i][j].delete(0, "end")
            entries[i][j].config(bg="white")
    user_entries = np.zeros((9, 9), dtype=int)
    steps = []
    current_step = 0
    step_label.config(text="Step: 0/0")

def check_grid():
    """Kiểm tra tính hợp lệ của lưới hiện tại"""
    load_grid_data()
    invalid_positions = find_invalid_positions()
    show_invalid_positions(invalid_positions)

def load_grid_data():
    """Tải dữ liệu từ giao diện vào mảng user_entries"""
    global user_entries
    for i in range(9):
        for j in range(9):
            value = entries[i][j].get()
            if value.isdigit():
                user_entries[i][j] = int(value)
            else:
                user_entries[i][j] = 0

def find_invalid_positions():
    """Tìm các vị trí không hợp lệ trong lưới"""
    invalid_positions = []
    for i in range(9):
        for j in range(9):
            if user_entries[i][j] != 0:
                if not is_valid(i, j, user_entries[i][j]):
                    invalid_positions.append((i, j))
    return invalid_positions

def is_valid(row, col, num):
    """Kiểm tra tính hợp lệ của một số tại vị trí (row, col)"""
    global user_entries
    # Kiểm tra hàng
    if np.count_nonzero(user_entries[row, :] == num) > 1:
        return False
    # Kiểm tra cột
    if np.count_nonzero(user_entries[:, col] == num) > 1:
        return False
    # Kiểm tra vùng 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    if np.count_nonzero(user_entries[start_row:start_row+3, start_col:start_col+3] == num) > 1:
        return False
    return True

def show_invalid_positions(invalid_positions):
    """Hiển thị các ô lỗi và gợi ý sửa"""
    for i in range(9):
        for j in range(9):
            entries[i][j].config(bg="white")  # Reset màu nền

    for row, col in invalid_positions:
        entries[row][col].delete(0, "end")  # Xóa giá trị không hợp lệ
        entries[row][col].insert(0, str(find_suggestion(row, col)))
        entries[row][col].config(bg="lightcoral")  # Đánh dấu ô lỗi

    if invalid_positions:
        messagebox.showerror("Invalid Grid", "Có lỗi trong lưới Sudoku. Đã gợi ý sửa!")
    else:
        messagebox.showinfo("Valid Grid", "Lưới hợp lệ!")

def find_suggestion(row, col):
    """Tìm giá trị hợp lệ cho một ô"""
    for num in range(1, 10):
        if is_valid(row, col, num):
            return num
    return 0  # Không tìm thấy giá trị hợp lệ

def solve_all():
    """Giải toàn bộ lưới Sudoku"""
    load_grid_data()
    if not solve(user_entries):
        messagebox.showerror("Error", "Không thể giải lưới này!")
    else:
        display_solution()

def solve(board):
    """Giải Sudoku bằng thuật toán Relations and Residuals"""
    # Tìm ô trống
    empty_cells = [(row, col) for row in range(9) for col in range(9) if board[row][col] == 0]
    if not empty_cells:
        return True  # Đã giải xong

    # Chọn ô có ít giá trị khả dụng nhất
    empty_cells.sort(key=lambda cell: len(get_candidates(board, cell[0], cell[1])))
    row, col = empty_cells[0]
    candidates = get_candidates(board, row, col)

    for num in candidates:
        board[row][col] = num
        if solve(board):
            return True
        board[row][col] = 0  # Quay lui nếu không tìm được lời giải

    return False  # Không tìm được lời giải

def get_candidates(board, row, col):
    """Trả về danh sách các giá trị khả dụng cho ô (row, col)"""
    candidates = set(range(1, 10))
    # Loại trừ các số đã xuất hiện trong hàng
    candidates -= set(board[row, :])
    # Loại trừ các số đã xuất hiện trong cột
    candidates -= set(board[:, col])
    # Loại trừ các số đã xuất hiện trong khối 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    candidates -= set(board[start_row:start_row+3, start_col:start_col+3].flatten())
    return list(candidates)


def display_solution():
    """Hiển thị lưới đã giải"""
    for i in range(9):
        for j in range(9):
            entries[i][j].delete(0, "end")
            entries[i][j].insert(0, str(user_entries[i][j]))
            entries[i][j].config(bg="lightblue")

def solve_step_by_step():
    """Giải Sudoku từng bước và lưu các trạng thái chính xác"""
    global steps, current_step
    load_grid_data()
    steps = []
    current_step = 0

    # Tạo bản sao của bảng hiện tại
    step_board = user_entries.copy()

    def step_solution(board):
        # Tìm ô trống
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    # Lấy các giá trị khả dụng
                    candidates = get_candidates(board, i, j)
                    if len(candidates) == 1:
                        # Điền giá trị duy nhất
                        board[i][j] = candidates[0]
                        steps.append(board.copy())
                        return True
        return False

    # Lặp cho đến khi bảng được giải
    while step_solution(step_board):
        pass

    # Kiểm tra nếu lưới không thể giải
    if np.any(step_board == 0):
        messagebox.showerror("Error", "Không thể giải lưới này!")
        return

    # Hiển thị bước đầu tiên
    display_step()

def display_step():
    """Hiển thị bước hiện tại"""
    global steps, current_step
    if steps:
        step_board = steps[current_step]
        for i in range(9):
            for j in range(9):
                entries[i][j].delete(0, "end")
                if step_board[i][j] != 0:
                    entries[i][j].insert(0, str(step_board[i][j]))
                    # Highlight chỉ ô được giải trong bước hiện tại
                    if current_step > 0 and steps[current_step - 1][i][j] == 0:
                        entries[i][j].config(bg="lightblue")
                    else:
                        entries[i][j].config(bg="white")
        step_label.config(text=f"Step: {current_step + 1}/{len(steps)}")

def next_step():
    """Chuyển tới bước tiếp theo"""
    global current_step
    if current_step < len(steps) - 1:
        current_step += 1
        display_step()


def previous_step():
    """Quay lại bước trước đó"""
    global current_step
    if current_step > 0:
        current_step -= 1
        display_step()

# Chương trình chính
root = Tk()
root.title("Sudoku Solver")
root.geometry("600x800")
setup_ui(root)
root.mainloop()
