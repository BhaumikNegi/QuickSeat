
import pandas as pd
from fpdf import FPDF

def get_room_capacity(rows, cols):
    return rows * cols

def create_room(name, rows, cols):
    return {
        'name': name,
        'rows': rows,
        'cols': cols,
        'seats': [[None for _ in range(cols)] for _ in range(rows)]
    }

def create_all_rooms(num_lts, num_crs, lt_rows, lt_cols, cr_rows, cr_cols):
    rooms = []
    for i in range(num_lts):
        rooms.append(create_room(f"LT-{i+1}", lt_rows, lt_cols))
    for i in range(num_crs):
        rooms.append(create_room(f"CR-{i+1}", cr_rows, cr_cols))
    rooms.sort(key=lambda r: get_room_capacity(r['rows'], r['cols']), reverse=True)
    return rooms

def can_sit(room, row, col, roll, dept_map):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    my_dept = dept_map[roll]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < room['rows'] and 0 <= c < room['cols']:
            neighbor = room['seats'][r][c]
            if neighbor and dept_map.get(neighbor) == my_dept:
                return False
    return True

def assign_students_to_rooms(student_data, num_lts, num_crs, lt_rows, lt_cols, cr_rows, cr_cols):
    students = sorted(student_data.values(), key=lambda x: x['Roll'])
    dept_map = {s['Roll']: s['Dept'] for s in students}
    student_lookup = {s['Roll']: s for s in students}
    rooms = create_all_rooms(num_lts, num_crs, lt_rows, lt_cols, cr_rows, cr_cols)
    student_idx = 0
    assigned = set()
    for room in rooms:
        for row in range(room['rows']):
            for col in range(room['cols']):
                if student_idx >= len(students):
                    break
                for offset in range(len(students)):
                    roll = students[(student_idx + offset) % len(students)]['Roll']
                    if roll in assigned:
                        continue
                    if can_sit(room, row, col, roll, dept_map):
                        room['seats'][row][col] = roll
                        assigned.add(roll)
                        student_idx += 1
                        break
                if student_idx >= len(students):
                    break
            if student_idx >= len(students):
                break
        if student_idx >= len(students):
            break
    return rooms, student_lookup

def generate_pdf(rooms, student_lookup, univ_name, exam_name, exam_date, exam_time, shift, output_path):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    page_width = pdf.w - 2 * pdf.l_margin

    for room in rooms:
        if not any(any(seat for seat in row) for row in room['seats']):
            continue
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, univ_name, ln=True, align='C')
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, exam_name, ln=True)
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, f"Seating Arrangement", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Room: {room['name']}", ln=True)
        pdf.cell(0, 10, f"Date: {exam_date}", ln=True)
        pdf.cell(0, 10, f"Time: {exam_time}", ln=True)
        pdf.cell(0, 10, f"Shift: {shift}", ln=True)

        col_width = page_width / room['cols']
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        for i in range(room['cols']):
            pdf.cell(col_width, 10, f"Col {i+1}", 1, 0, 'C', fill=True)
        pdf.ln()

        pdf.set_font("Arial", '', 10)
        for row in room['seats']:
            for seat in row:
                if seat:
                    student = student_lookup[seat]
                    text = f"{seat} ({student['Dept']})"
                else:
                    text = ""
                pdf.cell(col_width, 10, text, 1, 0, 'C')
            pdf.ln()

    pdf.output(output_path)
    return output_path
