from database import ServiceDatabase
from flask import Flask, request, jsonify, render_template

db = ServiceDatabase()
app = Flask(__name__)

# Home Page holds the open quotations
@app.route('/')
def index():

    # TODO: Delete
    db.add_sample_data()
    print(db.get_test())
    # <Name>
    # Orçamento Atual: R$ XXXX,XX
    # Criado em: HH:MM DD / MM / YYYY

    return render_template('index.html', services=db.get_open_quotations())


# AJAX to load quotation for specific user id
@app.route('/load_quotation', methods=['POST'])
def handle_click():
    # Retrieve JSON data from the request
    data = request.get_json()
    
    # Process the data (e.g., save to database, perform calculations, etc.)
    service_id = data.get('id')
    service_name = data.get('name')
    
    # Create a response message
    response_message = f"Received service ID: {service_id} with name: {service_name}"
    
    # Return a JSON response
    return jsonify({'message': response_message})

if __name__ == '__main__':
    app.run(debug=True)