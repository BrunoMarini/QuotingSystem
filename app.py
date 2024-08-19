from database import ServiceDatabase
from flask import Flask, request, jsonify, render_template

db = ServiceDatabase()
app = Flask(__name__)

# Home Page holds the open quotations
@app.route('/')
def index():

    # TODO: Delete
    db.add_sample_data()

    quotations = db.get_open_quotations_with_customer_and_price()
    return render_template('index.html', services=quotations)

# AJAX to load quotation for specific user id
@app.route('/load_quotation', methods=['POST'])
def handle_click():
    # Retrieve JSON data from the request
    data = request.get_json()
    service_id = data.get('id')

    quotation_items = db.get_all_items_for_quotation(service_id)

    current_quotation = []
    for item in quotation_items:
        i = {}
        i['service'] = db.get_service_name(item['service_id'])
        i['quantity'] = item['quantity']
        i['total_price'] = item['total_price']
        current_quotation.append(i)
    return jsonify(current_quotation)

if __name__ == '__main__':
    app.run(debug=True)