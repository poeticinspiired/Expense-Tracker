from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import logging
import json
import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simulating a database with a list
transactions = []

@app.route('/')
def index():
    logger.debug("Accessing index page")
    return render_template('index.html')

@app.route('/api/current_time')
def get_current_time():
    return jsonify({'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/api/transactions', methods=['GET', 'POST'])
def handle_transactions():
    global transactions
    if request.method == 'GET':
        return jsonify(transactions)
    elif request.method == 'POST':
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400
        transaction = {
            'id': len(transactions),
            'amount': data.get('amount'),
            'description': data.get('description'),
            'type': data.get('type'),
            'category': data.get('category')
        }
        transactions.append(transaction)
        return jsonify(transaction), 201

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    global transactions
    for i, transaction in enumerate(transactions):
        if transaction['id'] == transaction_id:
            del transactions[i]
            return '', 204
    return jsonify({'error': 'Transaction not found'}), 404

@app.route('/api/categories')
def get_categories():
    categories = set()
    for transaction in transactions:
        categories.add(transaction['category'])
    return jsonify(list(categories))

@app.route('/api/export/csv')
def export_csv():
    # Create a StringIO object to write CSV data
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    
    # Write header
    csv_writer.writerow(['ID', 'Amount', 'Description', 'Type', 'Category'])
    
    # Write transactions
    for transaction in transactions:
        csv_writer.writerow([
            transaction['id'],
            transaction['amount'],
            transaction['description'],
            transaction['type'],
            transaction['category']
        ])
    
    # Create a response with CSV data
    output = csv_output.getvalue()
    csv_output.close()
    
    return send_file(
        io.BytesIO(output.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='transactions.csv'
    )

@app.route('/api/export/pdf')
def export_pdf():
    # Create a BytesIO buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF object, using the BytesIO buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create the table data
    data = [['ID', 'Amount', 'Description', 'Type', 'Category']]
    for transaction in transactions:
        data.append([
            transaction['id'],
            transaction['amount'],
            transaction['description'],
            transaction['type'],
            transaction['category']
        ])
    
    # Create the table
    table = Table(data)
    
    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    # Add the table to the PDF
    elements = []
    elements.append(table)
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and create the response
    pdf = buffer.getvalue()
    buffer.close()
    
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='transactions.pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
