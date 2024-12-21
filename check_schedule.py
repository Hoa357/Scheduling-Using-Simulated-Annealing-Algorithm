import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

# Tải lịch từ file JSON
def load_schedule(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải lịch: {e}")
        return None

# Lọc lịch theo mã giảng viên
def filter_schedule_by_teacher(schedule, teacher_id):
    teacher_schedule = [
        entry for entry in schedule if teacher_id in entry["Teachers"]
    ]
    return teacher_schedule

# Hiển thị lịch vào bảng
def display_schedule(schedule):
    for child in table_frame.winfo_children():
        child.destroy()

    unique_days = sorted({entry["Day"] for entry in schedule})
    unique_slots = sorted({entry["Slot"] for entry in schedule})

    # Tạo tiêu đề cột (ca thi)
    tk.Label(table_frame, text="Ngày \\ Ca", borderwidth=1, relief="solid", bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="nsew")
    
    # Tạo tiêu đề dòng cho ngày
    for col_idx, slot in enumerate(unique_slots, start=1):
        tk.Label(table_frame, text=slot, borderwidth=1, relief="solid", bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=col_idx, sticky="nsew")

    # Điền các ô trong bảng (phòng thi)
    for row_idx, day in enumerate(unique_days, start=1):
        tk.Label(table_frame, text=day, borderwidth=1, relief="solid", bg="#f4f4f4", font=("Segoe UI", 10)).grid(row=row_idx, column=0, sticky="nsew")
        for col_idx, slot in enumerate(unique_slots, start=1):
            rooms = [
                entry["Room"] for entry in schedule if entry["Day"] == day and entry["Slot"] == slot
            ]
            room_text = "\n".join(rooms) if rooms else "-"
            tk.Label(table_frame, text=room_text, borderwidth=1, relief="solid", bg="white", font=("Segoe UI", 10)).grid(row=row_idx, column=col_idx, sticky="nsew")

# Tải và lọc lịch
def load_and_filter_schedule():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        return

    schedule = load_schedule(file_path)
    if not schedule:
        return

    teacher_id_str = teacher_id_entry.get().strip()
    if not teacher_id_str:
        messagebox.showerror("Lỗi", "Vui lòng nhập mã giảng viên.")
        return

    try:
        teacher_id = int(teacher_id_str)
    except ValueError:
        messagebox.showerror("Lỗi", "Mã giảng viên không hợp lệ.")
        return

    teacher_schedule = filter_schedule_by_teacher(schedule, teacher_id)
    if not teacher_schedule:
        messagebox.showinfo("Thông báo", "Không tìm thấy lịch cho giảng viên này.")
    else:
        display_schedule(teacher_schedule)

# Khởi tạo giao diện người dùng
root = tk.Tk()
root.title("Tra cứu lịch thi của giảng viên")
root.geometry("900x650")
root.config(bg="#E0F7FA")

# Khung nhập mã giảng viên
input_frame = tk.Frame(root, bg="#E0F7FA")
input_frame.pack(pady=20)

tk.Label(input_frame, text="Mã Giảng Viên:", bg="#E0F7FA", font=("Segoe UI", 12), fg="#00796B").pack(side="left", padx=10)
teacher_id_entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=20, bd=2, relief="solid", highlightthickness=2, highlightcolor="#00796B")
teacher_id_entry.pack(side="left", padx=10)

# Nút tải và lọc lịch với hiệu ứng hover
def on_enter(event):
    btn_load_filter.config(bg="#00695C", fg="white")

def on_leave(event):
    btn_load_filter.config(bg="#4CAF50", fg="white")

btn_load_filter = ttk.Button(root, text="Load và Xem Lịch", command=load_and_filter_schedule, width=20, style="TButton")
btn_load_filter.pack(pady=20)

btn_load_filter.bind("<Enter>", on_enter)
btn_load_filter.bind("<Leave>", on_leave)

# Khung bảng hiển thị lịch với viền mềm mại
table_frame = tk.Frame(root, bg="white", bd=2, relief="solid", padx=10, pady=10)
table_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Cải tiến với padding và canh chỉnh cho các phần tử
style = ttk.Style()
style.configure("TButton",
                font=("Segoe UI", 12),
                padding=10,
                relief="flat",
                background="#4CAF50",
                foreground="white")

root.mainloop()