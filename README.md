# Constraint-Based Timetable Generation for Academic Scheduling

**Subject:** Constraint Satisfaction Problems (CSP) / Scheduling Algorithms
**Architecture:** Object-Oriented Python with Constraint Checking
**Visualization:** Python Tkinter GUI

## 📌 Project Overview

This project implements a system for generating a university class timetable that satisfies a predefined set of hard constraints. The problem is approached as a **Constraint Satisfaction Problem (CSP)**, where the goal is to assign class meetings (variables) to time slots and rooms (domains) without violating any scheduling rules (constraints).

The core of the system is the `Timetable` class, which uses a randomized constraint-based search strategy to place all required lectures and sections efficiently. The final schedule is displayed using a **Tkinter** graphical interface.

## 💡 Key Concepts

### 1. Constraint Satisfaction
The system's objective is driven by the following constraints, checked explicitly by the `_check_constraints` method:

* **Instructor Conflict:** An instructor cannot be assigned to two different meetings at the same time.
* **Room Conflict:** A physical room cannot be used for two different meetings at the same time.
* **Section Conflict:** Students belonging to the same course section cannot be scheduled for two different classes at the same time.

### 2. Time Slot Constraints
Specific temporal constraints are enforced to maintain scheduling rules:

* **Fixed Meeting Lengths:** Meetings are placed based on two primary durations: 90 minutes (Lectures) and 45 minutes (Sections/Labs).
* **90-Minute Start Rule:** 90-minute lectures must start only at predefined slots (e.g., 9:00, 10:45, 12:30, etc.) to ensure a standard break pattern.

## ⚙️ System Configuration and Data

The schedule is built around predefined data and time divisions:

### 1. Time Domain
* **Days:** Sunday through Thursday.
* **Time Slots:** Eight 45-minute slots ranging from 9:00 AM to 3:45 PM, separated by short breaks (e.g., 09:00 - 09:45, 10:45 - 11:30).

### 2. Sample Data
The system is initialized with hardcoded sample data representing the entities to be scheduled:
* **Rooms:** A list of room names.
* **Instructors:** A list of instructor names.
* **Courses:** A list of courses, including total lecture and section hours.
* **Sections:** A mapping of which sections belong to which courses.

## 🛠️ Methodology

The timetable generation process, managed by the `generate` function, follows a sequential assignment approach:

1.  **Iterative Placement:** The generator iterates through every required lecture and section for all courses.
2.  **Random Search:** For each class meeting, the system attempts to assign it to a random day and time slot.
3.  **Constraint Checking:** Before final placement, the `_check_constraints` function is called to verify that the proposed slot does not violate any of the three main scheduling rules (Instructor, Room, Section Conflict).
4.  **Conflict Handling:** If a conflict is found, the placement attempt fails, and a new random slot is chosen until a valid placement is found.

### Performance Tracking
The `generate` function includes logic to track the effectiveness of the constraint model:
* **Total Checks Performed:** Total number of times a potential placement was evaluated.
* **Conflicts Prevented:** Total number of invalid placements (conflicts) blocked by the constraint checker.

## 💻 Visualization

The final, valid timetable is structured using the `pandas` DataFrame library for easy manipulation and is then rendered into a visual grid using the `tkinter` library.

* **Grid Layout:** The GUI displays the timetable as a grid where columns are days and rows are time slots.
* **Color Coding:** Each course is assigned a unique pastel color to visually distinguish between different subjects across the schedule.

## 🛠️ Dependencies

To run this project, you need the following Python libraries:

```bash
pip install pandas
# tkinter is usually included with Python standard library
