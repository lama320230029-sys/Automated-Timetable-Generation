import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import random

# =========================
# CONSTANTS
# =========================
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

TIME_SLOTS = [
    "09:00 - 09:45",
    "09:45 - 10:30",
    "10:45 - 11:30",
    "11:30 - 12:15",
    "12:30 - 01:15",
    "01:15 - 02:00",
    "02:15 - 03:00",
    "03:00 - 03:45"
]

ALLOWED_90_STARTS = {
    "09:00 - 09:45",
    "10:45 - 11:30",
    "12:30 - 01:15",
    "02:15 - 03:00"
}

# 🎨 Soft pastel colors (nice for timetable)
PASTEL_COLORS = [
    "#FFE5E5", "#E5F0FF", "#E5FFE9", "#FFF5E5",
    "#F0E5FF", "#E5FFF7", "#FFF0F5", "#F5FFE5",
    "#E5F5FF", "#FFE5F2"
]

# =========================
# TIMETABLE ENGINE (CSP)
# =========================
class Timetable:
    def __init__(self):
        self.section_checks = 0
        self.section_conflicts = 0
        self.students = pd.read_csv("Students.csv").ffill()
        self.courses  = pd.read_csv("Courses.csv").ffill()
        self.rooms    = pd.read_csv("Rooms.csv").ffill()

        self.room_busy = set()
        self.instructor_busy = set()
        self.section_busy = set()
        self.schedule = []

    def get_structure(self):
        structure = {}
        for _, r in self.students.iterrows():
            year = int(r["YEAR"])
            program = r["Program"]
            groups = int(r["No_of_Group"])
            secs = int(r["No_of_Section per Group"])
            sec_id = 1
            gmap = {}
            for g in range(1, groups + 1):
                gmap[f"G{g}"] = [f"S{s}" for s in range(sec_id, sec_id + secs)]
                sec_id += secs
            structure[(year, program)] = gmap #Save group and section under yea and program
        return structure

    def generate(self):
        self.schedule.clear()
        self.room_busy.clear()
        self.instructor_busy.clear()
        self.section_busy.clear()

        structure = self.get_structure() #Function that has the groups and sections

        for _, c in self.courses.iterrows():
            year = int(c["YEAR"])
            program = c["Program"]
            ctype = c["Type"].lower()
            instructors = [i.strip() for i in str(c["InstructorName"]).split(",")]
            target_programs = (
                [p for (y, p) in structure if y == 3]
                if year == 3 and program == "General"
                else [program]
            )

            for prog in target_programs:
                if (year, prog) not in structure:
                    continue

                for group, sections in structure[(year, prog)].items():
                    if ctype == "lec":
                        self.place(c, year, prog, group, sections, instructors)
                    else:
                        for s in sections:
                            self.place(c, year, prog, group, [s], instructors)

        return pd.DataFrame(self.schedule)

    def place(self, c, year, program, group, sections, instructors):
        ctype = c["Type"].lower()
        duration = str(c["Duration"]).strip()
        needed = 2 if duration.startswith("90") else 1

        for day in DAYS:
            for i in range(len(TIME_SLOTS) - needed + 1):
                slots = TIME_SLOTS[i:i + needed]

                if needed == 2 and slots[0] not in ALLOWED_90_STARTS:
                    continue

                for inst in instructors:
                    if any((inst, day, t) in self.instructor_busy for t in slots):
                        continue

                    rooms = ["SEC"] if ctype == "sec" else \
                        self.rooms[self.rooms["Type"] == c["Type"]]["BUILDING_NAME"]

                    for room in rooms:
                        if ctype != "sec" and any((room, day, t) in self.room_busy for t in slots):
                            continue

                        if self.is_section_busy(year, program, group, sections, day, slots):
                            continue

                        #Skip everything for this time slot    
                        for t in slots:
                            self.instructor_busy.add((inst, day, t))
                            if ctype != "sec":
                                self.room_busy.add((room, day, t))
                            for s in sections:
                                self.section_busy.add((year, program, group, s, day, t))

                        for s in sections:
                            self.schedule.append({
                                "Day": day,
                                "Time": " / ".join(slots),
                                "Year": year,
                                "Program": program,
                                "Group": group,
                                "Section": s,
                                "Course": c["Courses"],
                                "Type": ctype,
                                "Room": room,
                                "Instructor": inst,
                                "Duration": duration
                            })
                        return
    def is_section_busy(self, year, program, group, sections, day, slots):
        """
        Evaluates section-time constraint.
        """
        self.section_checks += 1

        for s in sections:
            for t in slots:
                if (year, program, group, s, day, t) in self.section_busy:
                    self.section_conflicts += 1
                    return True
        return False

# =========================
# GUI
# =========================
def run_gui(df):
    root = tk.Tk()
    root.title("University Timetable")
    root.geometry("1600x900")

    top = ttk.Frame(root, padding=5)
    top.pack(fill=tk.X)
    #label drowpdown
    ttk.Label(top, text="Select Year:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    year_var = tk.StringVar()
    #dropdown lsit
    ttk.Combobox(
        top, values=sorted(df["Year"].unique()),
        textvariable=year_var, state="readonly", width=8
    ).pack(side=tk.LEFT, padx=5)

    ttk.Button(top, text="Show Timetable").pack(side=tk.LEFT)
    #grid
    container = ttk.Frame(root)
    container.pack(fill=tk.BOTH, expand=True)
    #canvas
    canvas = tk.Canvas(container, bg="#f5f5f5")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    #vertical and horizontal scrolling
    v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    h_scroll = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    grid = tk.Frame(canvas)
    canvas.create_window((0, 0), window=grid, anchor="nw")
    grid.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # course → color map
    course_color = {}
    color_index = 0

    def get_course_color(course):
        nonlocal color_index
        if course not in course_color:
            course_color[course] = PASTEL_COLORS[color_index % len(PASTEL_COLORS)]
            color_index += 1
        return course_color[course]

    def draw():
        #remvoes previously draw timetable
        for w in grid.winfo_children():
            w.destroy()

        if not year_var.get():
            messagebox.showwarning("Warning", "Select Year")
            return

        sub = df[df["Year"] == int(year_var.get())]

        #one of these for the year selected
        cols = sorted(
            sub[["Program", "Group", "Section"]]
            .drop_duplicates().apply(tuple, axis=1).tolist()
        )
        #header
        tk.Label(grid, text="Day / Time", bg="#ddd", relief="solid", width=18)\
            .grid(row=0, column=0, sticky="nsew")

        for i, (p, g, s) in enumerate(cols):
            tk.Label(grid, text=f"{p}\n{g}-{s}",
                     bg="#ddd", relief="solid", width=25)\
                .grid(row=0, column=i + 1, sticky="nsew")

        used = set()
        r = 1

        for d in DAYS:
            for t in TIME_SLOTS:
                tk.Label(grid, text=f"{d}\n{t}",
                         bg="#eee", relief="solid", width=18)\
                    .grid(row=r, column=0, sticky="nsew")

                c = 0
                while c < len(cols):
                    if (r, c) in used:
                        c += 1
                        continue

                    p, g, s = cols[c]
                    cell = sub[
                        (sub["Day"] == d) &
                        (sub["Time"].str.contains(t)) &
                        (sub["Program"] == p) &
                        (sub["Group"] == g) &
                        (sub["Section"] == s)
                    ]

                    if cell.empty:
                        tk.Label(grid, text="", relief="solid")\
                            .grid(row=r, column=c + 1, sticky="nsew")
                        c += 1
                        continue

                    m = cell.iloc[0]
                    rowspan = 2 if str(m["Duration"]).startswith("90") else 1
                    colspan = 1

                    if rowspan == 2:
                        used.add((r + 1, c))

                    if m["Type"] == "lec":
                        for nc in range(c + 1, len(cols)):
                            p2, g2, s2 = cols[nc]
                            other = sub[
                                (sub["Day"] == d) &
                                (sub["Time"].str.contains(t)) &
                                (sub["Program"] == p2) &
                                (sub["Group"] == g2) &
                                (sub["Section"] == s2) &
                                (sub["Course"] == m["Course"]) &
                                (sub["Instructor"] == m["Instructor"])
                            ]
                            if other.empty:
                                break
                            colspan += 1
                            used.add((r, nc))
                            if rowspan == 2:
                                used.add((r + 1, nc))

                    # TEXT
                    if m["Type"] == "lab":
                        text = f"{m['Course']}\n{m['Room']}\n{m['Instructor']}"
                    elif m["Type"] == "sec":
                        text = f"{m['Course']}\nsec\n{m['Instructor']}"
                    else:
                        text = f"{m['Course']}\nlec\n{m['Room']}\n{m['Instructor']}"

                    bg = get_course_color(m["Course"])

                    tk.Label(
                        grid,
                        text=text,
                        bg=bg,
                        relief="solid",
                        wraplength=300,
                        justify="center"
                    ).grid(
                        row=r, column=c + 1,
                        rowspan=rowspan, columnspan=colspan,
                        sticky="nsew"
                    )

                    c += colspan
                r += 1

    for w in top.winfo_children():
        if isinstance(w, ttk.Button):
            w.config(command=draw)

    root.mainloop()

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    engine = Timetable()
    df = engine.generate()
    print("\n📊 SECTION CONSTRAINT EVALUATION")
    print("--------------------------------")
    print(f"Total checks performed : {engine.section_checks}")
    print(f"Conflicts prevented    : {engine.section_conflicts}")
    print(f"Valid placements       : {engine.section_checks - engine.section_conflicts}")

    df.to_csv("Final_Timetable.csv", index=False, encoding="utf-8-sig")
    run_gui(df)