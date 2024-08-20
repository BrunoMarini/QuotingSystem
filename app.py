from database import ServiceDatabase
from flask import Flask, request, jsonify, render_template

db = ServiceDatabase()
app = Flask(__name__)

# Home Page holds the open quotations
@app.route('/')
def index():

    # TODO: Delete
    #db.add_sample_data()

    quotations = db.get_open_quotations_with_customer_and_price()
    return render_template('index.html', services=quotations)

# AJAX to load quotation for specific user id
@app.route('/load_quotation', methods=['POST'])
def handle_click():
    data = request.get_json()

    quotation_items = db.get_all_items_for_quotation(data['id'])

    result = {}
    result['name'] = data['name']

    current_quotation = []
    for item in quotation_items:
        i = {}
        service = db.get_service_for_id(item['service_id'])
        i['service'] = service['name']
        i['service_price'] = service['price']
        i['item_id'] = item['id']
        i['quantity'] = item['quantity']
        i['total_price'] = item['total_price']
        current_quotation.append(i)

    result['items'] = current_quotation
    return jsonify(result)

@app.route('/delete_quotation_item', methods=['POST'])
def handle_delete_quotation_item():
    data = request.get_json()

    response = {}
    if (db.delete_quotation_item(data['id']) > 0):
        response['status'] = 'Ok'
    else:
        response['status'] = 'Error'

    return jsonify(response)




if __name__ == '__main__':
    app.run(debug=True)