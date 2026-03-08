from flask import Flask, render_template, request, send_file, session, redirect, url_for
import pandas as pd
import io, os, json
from analyzer      import process_all_parts
from excel_builder import build_excel
from pdf_reporter  import build_pdf

app = Flask(__name__)
app.secret_key = 'rotem-srs-spare-parts-2026'  # needed for session storage


def read_uploaded_file(file):
    """Read the uploaded Excel or CSV file into a list of dicts."""
    filename = file.filename.lower()
    if filename.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    required = ['part_name','monthly_faults','months_recorded',
                'lead_time_days','max_demand','unit_cost']
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'Missing columns: {missing}')

    return df.to_dict(orient='records')


@app.route('/', methods=['GET'])
def index():
    """Show the upload page."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Receive uploaded file, run analysis, show results."""
    if 'file' not in request.files:
        return render_template('index.html', error='No file uploaded.')

    file        = request.files['file']
    station     = request.form.get('station', 'Depot')

    if file.filename == '':
        return render_template('index.html', error='Please select a file.')

    try:
        parts             = read_uploaded_file(file)
        results, summary  = process_all_parts(parts)
        # Store in session for download endpoints
        session['results'] = json.dumps(results)
        session['summary'] = json.dumps(summary)
        session['station'] = station
        return render_template('results.html',
                               results=results, summary=summary, station=station)
    except Exception as e:
        return render_template('index.html', error=f'Error processing file: {str(e)}')


@app.route('/download/excel')
def download_excel():
    """Generate and download the Excel report."""
    results = json.loads(session.get('results', '[]'))
    summary = json.loads(session.get('summary', '{}'))
    station = session.get('station', 'Depot')
    excel_bytes = build_excel(results, summary, station)
    return send_file(
        io.BytesIO(excel_bytes),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{station}_spare_parts_report.xlsx'
    )


@app.route('/download/pdf')
def download_pdf():
    """Generate and download the PDF report."""
    results = json.loads(session.get('results', '[]'))
    summary = json.loads(session.get('summary', '{}'))
    station = session.get('station', 'Depot')
    pdf_bytes = build_pdf(results, summary, station)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{station}_spare_parts_report.pdf'
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)

