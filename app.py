from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from algoandpdf1 import assign_students_to_rooms, generate_pdf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        univ_name=request.form.get('univ_name')
        lt_count = int(request.form['lt_count'])
        lt_rows = int(request.form['lt_rows'])
        lt_cols = int(request.form['lt_cols'])
        cr_count = int(request.form['cr_count'])
        cr_rows = int(request.form['cr_rows'])
        cr_cols = int(request.form['cr_cols'])
        exam_date = request.form['exam_date']
        exam_subject = request.form['exam_subject']
        shift = request.form.get('shift')
        duration = request.form.get('duration')
        file = request.files['file']

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            df = pd.read_excel(filepath)
            students = df.to_dict(orient='index')
            rooms, student_lookup = assign_students_to_rooms(students, lt_count, cr_count, lt_rows, lt_cols, cr_rows, cr_cols)
            output_pdf_path = os.path.join(OUTPUT_FOLDER, "Seating_Arrangement.pdf")
            generate_pdf(rooms, student_lookup, univ_name , exam_subject, exam_date, duration, shift, output_pdf_path)
            return send_file(output_pdf_path, as_attachment=True)
    return render_template('index.html')
if __name__ == "__main__":
    app.run(debug=True)
