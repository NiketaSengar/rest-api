from flask import Flask, url_for, request, jsonify
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/pie_chart": {"origins": ["*"]}}, methods=["GET"], supports_credentials=True)
CORS(app, resources={r"/bar_chart": {"origins": ["*"]}}, methods=["GET"], supports_credentials=True)

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
@app.route('/pie_chart', methods=['GET'])
def pie_chart():
    # Connect to the database using a context manager
    with get_db_connection() as connection:
        # Create a cursor object using a context manager
        with connection.cursor() as cursor:
            cursor.execute('SELECT cc.Category,count(aa.TransactionID) as FraudCount from frauds aa join transaction_category_labels cc on aa.TransactionID=cc.TransactionID group by cc.Category;')
            pie_data = cursor.fetchall()
    return jsonify({'pie_data': pie_data})

@app.route('/bar_chart', methods=['GET'])
def bar_graph():
    # Connect to the database using a context manager
    with get_db_connection() as connection:
        # Create a cursor object using a context manager
        with connection.cursor() as cursor:
            cursor.execute('SELECT c.Age, COUNT(f.TransactionID) AS FraudCount FROM customer_data c JOIN frauds f ON c.CustomerID = f.CustomerID GROUP BY c.Age ORDER BY c.Age;')
            data = cursor.fetchall()

    # Calculate age ranges in Python
    age_ranges = {'0-10': 0, '11-20': 0, '21-30': 0, '31-40': 0, '41-50': 0, '51-60': 0, '61-70': 0, '71-80': 0, '81-90': 0, '91-100': 0}
    for entry in data:
        age = int(entry['Age'])
        for key in age_ranges:
            start, end = map(int, key.split('-'))
            if start <= age <= end:
                age_ranges[key] += entry['FraudCount']
                break

    result = [{'AgeRange': key, 'FraudCount': value} for key, value in age_ranges.items()]
    return jsonify({'bar_chart': result})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5003)
