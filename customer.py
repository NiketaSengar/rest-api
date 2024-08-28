from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/customer_data": {"origins": ["*"]}}, methods=["POST"],supports_credentials=True)

app.config['MYSQL_HOST'] = 'database-2.c9oweosgs3dx.us-east-1.rds.amazonaws.com'
app.config['MYSQL_PORT'] = 3315
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Hack#1997'
app.config['MYSQL_DB'] = 'db1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def get_db_connection():
    """Establish a database connection."""
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        port=app.config['MYSQL_PORT'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/customer_data', methods=['POST'])
def customer_data():
    data = request.json
    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'error': 'Customer ID not provided'}), 400
 # Connect to the database using a context manager
    with get_db_connection() as connection:
        # Create a cursor object using a context manager
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM db1.customer_view WHERE CustomerID = %s',(customer_id,))

            consumer_data = cursor.fetchall()

    return jsonify({'consumer_data': consumer_data})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)