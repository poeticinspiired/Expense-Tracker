from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime, timedelta
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
recurring_transactions = []

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
            'category': data.get('category'),
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'is_recurring': data.get('is_recurring', False),
            'recurrence_interval': data.get('recurrence_interval')
        }
        transactions.append(transaction)
        if transaction['is_recurring']:
            add_recurring_transaction(transaction)
        return jsonify(transaction), 201

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    global transactions, recurring_transactions
    for i, transaction in enumerate(transactions):
        if transaction['id'] == transaction_id:
            deleted_transaction = transactions.pop(i)
            if deleted_transaction['is_recurring']:
                remove_recurring_transaction(deleted_transaction)
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
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    
    csv_writer.writerow(['ID', 'Amount', 'Description', 'Type', 'Category', 'Date', 'Is Recurring', 'Recurrence Interval'])
    
    for transaction in transactions:
        csv_writer.writerow([
            transaction['id'],
            transaction['amount'],
            transaction['description'],
            transaction['type'],
            transaction['category'],
            transaction['date'],
            transaction['is_recurring'],
            transaction.get('recurrence_interval', '')
        ])
    
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
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    data = [['ID', 'Amount', 'Description', 'Type', 'Category', 'Date', 'Is Recurring', 'Recurrence Interval']]
    for transaction in transactions:
        data.append([
            transaction['id'],
            transaction['amount'],
            transaction['description'],
            transaction['type'],
            transaction['category'],
            transaction['date'],
            'Yes' if transaction['is_recurring'] else 'No',
            transaction.get('recurrence_interval', '')
        ])
    
    table = Table(data)
    
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
    
    elements = []
    elements.append(table)
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='transactions.pdf'
    )

def add_recurring_transaction(transaction):
    recurring_transactions.append(transaction)

def remove_recurring_transaction(transaction):
    global recurring_transactions
    recurring_transactions = [t for t in recurring_transactions if t['id'] != transaction['id']]

@app.route('/api/process_recurring_transactions', methods=['POST'])
def process_recurring_transactions():
    global transactions
    current_date = datetime.now().date()
    new_transactions = []

    for recurring_transaction in recurring_transactions:
        last_occurrence = datetime.strptime(recurring_transaction['date'], '%Y-%m-%d').date()
        interval = recurring_transaction['recurrence_interval']

        if interval == 'daily':
            days_to_add = 1
        elif interval == 'weekly':
            days_to_add = 7
        elif interval == 'monthly':
            days_to_add = 30
        elif interval == 'yearly':
            days_to_add = 365
        else:
            continue

        next_occurrence = last_occurrence + timedelta(days=days_to_add)

        while next_occurrence <= current_date:
            new_transaction = recurring_transaction.copy()
            new_transaction['id'] = len(transactions)
            new_transaction['date'] = next_occurrence.strftime('%Y-%m-%d')
            new_transaction['is_recurring'] = False
            new_transaction.pop('recurrence_interval', None)
            
            transactions.append(new_transaction)
            new_transactions.append(new_transaction)
            
            next_occurrence += timedelta(days=days_to_add)

        recurring_transaction['date'] = (next_occurrence - timedelta(days=days_to_add)).strftime('%Y-%m-%d')

    return jsonify(new_transactions), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
