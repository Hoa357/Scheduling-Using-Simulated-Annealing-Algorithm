import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
import pandas as pd
import random
import json
import os

# Tải dữ liệu từ tệp Excel
def load_data_from_excel(file_path):
    """Tải dữ liệu từ tệp Excel và trả về danh sách giảng viên, phòng, ngày và ca thi."""
    xls = pd.ExcelFile(file_path)

    days_df = pd.read_excel(xls, sheet_name='ExamDates')
    days = days_df.iloc[:, 0].dropna().tolist()

    rooms_df = pd.read_excel(xls, sheet_name='Rooms')
    rooms = rooms_df.iloc[:, 0].dropna().tolist()

    teachers_df = pd.read_excel(xls, sheet_name='Teachers')
    teachers = teachers_df.iloc[:, :2].dropna().values.tolist()

    slots_df = pd.read_excel(xls, sheet_name='ExamSlots')
    slots = slots_df.apply(lambda row: f"{row.iloc[0]} ({row.iloc[1]} - {row.iloc[2]})", axis=1).tolist()

    return teachers, rooms, days, slots

# Hàm tính toán độ phù hợp của lịch
def fitness(schedule):
    """Tính toán độ phù hợp của một lịch thi."""
    penalty = 0
    teacher_usage = {}

    for entry in schedule:
        day = entry['Day']
        slot = entry['Slot']
        teachers = entry['Teachers']

        for teacher in teachers:
            if teacher in teacher_usage.get((day, slot), set()):
                penalty += 1
            else:
                if (day, slot) not in teacher_usage:
                    teacher_usage[(day, slot)] = set()
                teacher_usage[(day, slot)].add(teacher)

    return -penalty

# Tạo lịch ngẫu nhiên
def generate_random_schedule(teachers, rooms, days, slots):
    schedule = []
    teacher_usage = {}

    for day in days:
        for slot in slots:
            teacher_usage[(day, slot)] = set()
            for room in rooms:
                available_teachers = [t[0] for t in teachers if t[0] not in teacher_usage[(day, slot)]]

                if len(available_teachers) > 0:
                    assigned_teachers = random.sample(available_teachers, min(2, len(available_teachers)))
                    teacher_usage[(day, slot)].update(assigned_teachers)

                    schedule.append({
                        "Day": day,
                        "Slot": slot,
                        "Room": room,
                        "Teachers": assigned_teachers
                    })

    return schedule

# Thuật toán Simulated Annealing
def simulated_annealing(teachers, rooms, days, slots, initial_temp=1000, cooling_rate=0.95, max_iterations=1000):
    current_schedule = generate_random_schedule(teachers, rooms, days, slots)
    current_fitness = fitness(current_schedule)
    temp = initial_temp

    for _ in range(max_iterations):
        neighbor_schedule = current_schedule[:]
        random_entry = random.choice(neighbor_schedule)
        day, slot = random_entry['Day'], random_entry['Slot']
        available_teachers = [t[0] for t in teachers if t[0] not in {t for e in neighbor_schedule if e['Day'] == day and e['Slot'] == slot for t in e['Teachers']}]
        if available_teachers:
            random_entry['Teachers'] = random.sample(available_teachers, min(2, len(available_teachers)))

        neighbor_fitness = fitness(neighbor_schedule)
        delta = neighbor_fitness - current_fitness

        if delta > 0 or random.random() < pow(2.718, delta / temp):
            current_schedule = neighbor_schedule
            current_fitness = neighbor_fitness

        temp *= cooling_rate

    return current_schedule

# Lưu lịch vào tệp JSON
def save_schedule_to_json(schedule):
    if not os.path.exists("schedules"):
        os.makedirs("schedules")
    file_path = os.path.join("schedules", "schedule.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)

# Hiển thị lịch thi
def display_schedule():
    global teachers, rooms, days, slots, selected_day

    if not teachers or not rooms or not slots:
        messagebox.showerror("Lỗi", "Chưa tải dữ liệu. Vui lòng tải tệp Excel trước.")
        return

    selected_date = selected_day.get()
    if not selected_date:
        messagebox.showerror("Lỗi", "Chưa chọn ngày. Vui lòng chọn một ngày.")
        return

    schedule = simulated_annealing(teachers, rooms, [selected_date], slots)
    save_schedule_to_json(schedule)

    for child in table_frame.winfo_children():
        child.destroy()

    header = ["Ca Thi"] + rooms
    for col in header:
        lbl = tk.Label(table_frame, text=col, borderwidth=1, relief="solid", bg="lightblue", font=("Arial", 12, "bold"))
        lbl.grid(row=0, column=header.index(col), sticky="nsew", padx=5, pady=5)

    for slot_idx, slot in enumerate(slots):
        tk.Label(table_frame, text=slot, borderwidth=1, relief="solid", bg="lightgray", font=("Arial", 10)).grid(row=slot_idx + 1, column=0, sticky="nsew", padx=5, pady=5)
        for room_idx, room in enumerate(rooms):
            matching = next((entry for entry in schedule if entry['Slot'] == slot and entry['Room'] == room), None)
            if matching:
                teachers_display = ", ".join(map(str, matching['Teachers']))
                lbl = tk.Label(table_frame, text=teachers_display, borderwidth=1, relief="solid", bg="white", font=("Arial", 10))
                lbl.grid(row=slot_idx + 1, column=room_idx + 1, sticky="nsew", padx=5, pady=5)

# Tải tệp Excel
def load_excel_file():
    file_path = filedialog.askopenfilename(filetypes=[("Tệp Excel", "*.xlsx;*.xls")])
    if file_path:
        global teachers, rooms, days, slots
        teachers, rooms, days, slots = load_data_from_excel(file_path)
        btn_generate.config(state="normal")
        cal.config(state="normal")
        messagebox.showinfo("Thành công", "Dữ liệu đã được tải thành công!")
# Khởi tạo giao diện người dùng
root = tk.Tk()
root.title("Phần Mềm Tạo Lịch Thi")
root.geometry("800x600")
root.config(bg="#f5f5f5")

cal = Calendar(root, state="disabled")
cal.pack(pady=10)

selected_day = tk.StringVar()

def select_date():
    selected_day.set(cal.get_date())

btn_select_date = ttk.Button(root, text="Chọn Ngày", command=select_date, style="TButton")
btn_select_date.pack(pady=5)

table_frame = tk.Frame(root, bg="white")
table_frame.pack(padx=10, pady=10, fill="both", expand=True)

btn_load = ttk.Button(root, text="Tải Dữ Liệu từ Tệp Excel", command=load_excel_file, style="TButton")
btn_load.pack(pady=10)

btn_generate = ttk.Button(root, text="Tạo Lịch Thi", command=display_schedule, state="disabled", style="TButton")
btn_generate.pack(pady=10)

teachers, rooms, days, slots = [], [], [], []

# Style configurations for buttons
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#4CAF50", font=("Arial", 10))
style.map("TButton", background=[('active', '#45a049')])

root.mainloop()