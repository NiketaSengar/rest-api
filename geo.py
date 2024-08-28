from flask import Flask, jsonify
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/geolocation": {"origins": ["*"]}}, methods=["GET"], supports_credentials=True)

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

@app.route('/geolocation', methods=['GET'])
def geolocation():
    # Connect to the database using a context manager
    with get_db_connection() as connection:
        # Create a cursor object using a context manager
        with connection.cursor() as cursor:
            cursor.execute('SELECT Coordinates FROM db1.frauds;')
            geolocation_data = cursor.fetchall()

    # Process the coordinates string to extract latitude and longitude
    processed_data = [
        {
            'latitude': float(coord['Coordinates'].split(',')[0]),
            'longitude': float(coord['Coordinates'].split(',')[1]),
            'Coordinates': coord['Coordinates']
        }
        for coord in geolocation_data
    ]

    # Return the processed geolocation data as JSON
    return jsonify({'geolocation': processed_data})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
