import random
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

# Lớp mô tả phòng học
class Room:
    def __init__(self, id, capacity, equipment):
        self.id = id
        self.capacity = capacity
        self.equipment = equipment

# Lớp mô tả giáo viên
class Teacher:
    def __init__(self, id, subjects, available_times):
        self.id = id
        self.subjects = subjects
        self.available_times = available_times  # Danh sách thời gian rảnh

# Lớp mô tả nhóm sinh viên
class StudentGroup:
    def __init__(self, id, subjects):
        self.id = id
        self.subjects = subjects

# Lớp mô tả một lớp học cụ thể
class ClassSchedule:
    def __init__(self, subject, teacher, student_group, duration, equipment):
        self.subject = subject
        self.teacher = teacher
        self.student_group = student_group
        self.duration = duration
        self.equipment = equipment
        self.room = None
        self.time_slot = None

# Lớp mô tả lịch học (cá thể trong thuật toán GA)
class Schedule:
    def __init__(self, classes, rooms, teachers, time_slots):
        self.classes = classes
        self.rooms = rooms
        self.teachers = teachers
        self.time_slots = time_slots
        self.assign_random_schedule()

    def assign_random_schedule(self):
        for cls in self.classes:
            cls.room = random.choice(self.rooms)
            cls.time_slot = random.choice(self.time_slots)

    def fitness(self):
        score = 0
        used_slots = {}
        for cls in self.classes:
            key = (cls.room.id, cls.time_slot)
            if key in used_slots:
                score -= 10  # Phòng bị trùng thời gian
            else:
                used_slots[key] = True
            
            if cls.time_slot not in cls.teacher.available_times:
                score -= 5  # Giáo viên không rảnh
            
            if cls.room.capacity < len(cls.student_group.subjects):
                score -= 5  # Phòng không đủ chỗ
        return score

    def crossover(self, other):
        point = len(self.classes) // 2
        child_classes = self.classes[:point] + other.classes[point:]
        return Schedule(child_classes, self.rooms, self.teachers, self.time_slots)

    def mutate(self):
        if random.random() < 0.1:  # Xác suất đột biến
            random.choice(self.classes).time_slot = random.choice(self.time_slots)

# Hàm thực thi thuật toán GA
def genetic_algorithm(classes, rooms, teachers, time_slots, generations=100):
    population = [Schedule(classes, rooms, teachers, time_slots) for _ in range(10)]
    fitness_history = []
    for _ in range(generations):
        population.sort(key=lambda x: x.fitness(), reverse=True)
        fitness_history.append(population[0].fitness())
        new_population = [population[0]]  # Giữ cá thể tốt nhất
        while len(new_population) < 10:
            p1, p2 = random.choices(population[:5], k=2)
            child = p1.crossover(p2)
            child.mutate()
            new_population.append(child)
        population = new_population
    plot_fitness(fitness_history)
    return population[0]  # Trả về lịch tốt nhất

# Vẽ biểu đồ đánh giá tiến trình tối ưu hóa
def plot_fitness(fitness_history):
    plt.plot(fitness_history)
    plt.xlabel("Generations")
    plt.ylabel("Fitness Score")
    plt.title("Optimization Progress")
    plt.show()

# Dữ liệu giả lập
rooms = [Room("A101", 50, ["Projector"]), Room("B202", 30, ["Whiteboard"])]
teachers = [Teacher("T1", ["Math", "Physics"], ["Monday 8AM", "Tuesday 10AM"]),
            Teacher("T2", ["English"], ["Monday 10AM", "Wednesday 8AM"])]
students = [StudentGroup("S1", ["Math", "English"]), StudentGroup("S2", ["Physics", "English"])]
classes = [ClassSchedule("Math", teachers[0], students[0], 2, ["Projector"]),
           ClassSchedule("Physics", teachers[0], students[1], 2, []),
           ClassSchedule("English", teachers[1], students[0], 2, ["Whiteboard"])]
time_slots = ["Monday 8AM", "Monday 10AM", "Tuesday 8AM", "Wednesday 8AM"]

# Chạy thuật toán GA
best_schedule = genetic_algorithm(classes, rooms, teachers, time_slots)

# Xuất kết quả ra file Excel
def export_to_excel(schedule):
    data = []
    for cls in schedule.classes:
        data.append([cls.subject, cls.teacher.id, cls.student_group.id, cls.room.id, cls.time_slot])
    df = pd.DataFrame(data, columns=["Môn học", "Giáo viên", "Nhóm SV", "Phòng", "Thời gian"])
    df.to_excel("schedule.xlsx", index=False)
    print("Lịch học đã được xuất ra file schedule.xlsx")

export_to_excel(best_schedule)

# Hiển thị lịch học bằng giao diện Tkinter
def show_schedule(schedule):
    root = tk.Tk()
    root.title("Lịch học")
    tree = ttk.Treeview(root, columns=("Môn học", "Giáo viên", "Nhóm SV", "Phòng", "Thời gian"), show='headings')
    for col in ("Môn học", "Giáo viên", "Nhóm SV", "Phòng", "Thời gian"):
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for cls in schedule.classes:
        tree.insert("", "end", values=(cls.subject, cls.teacher.id, cls.student_group.id, cls.room.id, cls.time_slot))
    tree.pack(expand=True, fill='both')
    root.mainloop()

show_schedule(best_schedule)
