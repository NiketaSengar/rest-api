import streamlit as st
import pandas as pd
import joblib
import pymysql
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy import text
import requests
from flask import Flask,url_for,request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/get_fraud_data": {"origins": ["*"]}}, methods=["POST"],supports_credentials=True)

model_filename = 'fraud_detection_model.joblib'
clf = joblib.load(model_filename)

# MySQL database connection parameters
host = 'database-2.c9oweosgs3dx.us-east-1.rds.amazonaws.com'
user = 'admin'
password = 'Hack#1997'
database = 'db1'
port = 3315
# Create a MySQL connection
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")


# Placeholder for additional features
additional_features_df = [pd.DataFrame() for _ in range(4)]
balance_1 = 0
address = ""
# Streamlit app
def get_geolocation(ip_address):
    api_key = '2369b51501bf66'  # Replace with your ipinfo.io API key
    url = f'https://ipinfo.io/{ip_address}?token={api_key}'
    response = requests.get(url)
    data = response.json()
    return data
def main():
    st.title("Mock Transaction API")

    # User input form
    st.header("Enter Transaction Details:")
    customer_id = st.number_input("Customer ID:", min_value=1001, max_value=2000)
    transaction_amount = st.number_input("Transaction Amount:")
    merchant_id = st.number_input("Merchant ID:", min_value=2001, max_value=3000)
    category = st.selectbox("Transaction Category:", ['Food', 'Retail', 'Travel', 'Online', 'Other'])

    # Fetch additional features from the MySQL database based on Customer ID
    query = f"SELECT Age FROM customer_data WHERE CustomerID = {customer_id}"
    query1 = f"SELECT AccountBalance FROM account_activity WHERE CustomerID = {customer_id}"
    query2 = f"SELECT SuspiciousFlag FROM suspicious_activity WHERE CustomerID = {customer_id}"
    query3 = f"SELECT Address FROM customer_view WHERE CustomerID = {customer_id}"

    additional_features_df[0] = pd.read_sql_query(query, engine)
    additional_features_df[1] = pd.read_sql_query(query1, engine)
    additional_features_df[2] = pd.read_sql_query(query2, engine)
    additional_features_df[3] = pd.read_sql_query(query3, engine)
    query4 = "select max(TransactionID) from transaction_records;"
    additional_features_neo = pd.read_sql_query(query4, engine)
    max_transaction = additional_features_neo.loc[0, 'max(TransactionID)']
    # Ensure that the query returned a result
    if not any(df.empty for df in additional_features_df):
        # Extract relevant features
        age = additional_features_df[0].loc[0, 'Age']
        account_balance = additional_features_df[1].loc[0, 'AccountBalance']
        SuspiciousFlag = additional_features_df[2].loc[0, 'SuspiciousFlag']
        balance_1 = account_balance
        address = additional_features_df[3].loc[0, 'Address']
        # Display additional features
        st.write(f"Age: {age}")
        st.write(f"Account Balance: {account_balance}")
        st.write(f"SuspiciousFlag: {SuspiciousFlag}")

        # Button to process transaction
        if st.button("Process Transaction"):
            # Placeholder for ML model prediction
            fraud_prediction = predict_fraud(transaction_amount, age, account_balance, SuspiciousFlag)

            # Update MySQL tables based on prediction
            update_mysql_tables(customer_id, transaction_amount, merchant_id, category, fraud_prediction,balance_1,max_transaction)

            # Display result
            if fraud_prediction:
                st.error("Suspicious/Fraudulent Transaction Detected!")
            else:
                st.success("Transaction Processed Successfully!")
    else:
        st.warning("No additional features found for the provided Customer ID.")

# Function to make predictions with the ML model
def predict_fraud(transaction_amount, age, account_balance, SuspiciousFlag):
    # Replace with your actual machine learning model prediction logic
    # Return 1 for fraud/suspicious transaction, 0 otherwise
    # Ensure that the input features are in the correct order and format
    input_features = [age, account_balance, transaction_amount, SuspiciousFlag]  # Assuming last login is not used in the model
    return clf.predict([input_features])[0]

@app.route('/get_fraud_data', methods=['POST'])
def get_fraud_data():
    query = "SELECT * FROM db1.frauds;"
    fraud_data = pd.read_sql_query(query, engine)
    fraud_json = fraud_data.to_json(orient='records')
    return jsonify({'fraud_data': fraud_json})


# Function to update MySQL tables
def update_mysql_tables(customer_id, transaction_amount, merchant_id, category, fraud_prediction,balance_1,max_transaction):
    # Update transaction_records table
    transaction_records_data = {
        'TransactionID': max_transaction+1,
        'CustomerID': customer_id
    }
    transaction_records_df = pd.DataFrame(transaction_records_data, index=[0])
    transaction_records_df.to_sql('transaction_records', engine, if_exists='append', index=False)

    # Update transaction_metadata table
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_metadata_data = {
        'TransactionID': max_transaction+1,
        'Timestamp': timestamp_now,
        'MerchantID': merchant_id
    }
    transaction_metadata_df = pd.DataFrame(transaction_metadata_data, index=[0])
    transaction_metadata_df.to_sql('transaction_metadata', engine, if_exists='append', index=False)

    # Update fraud_indicators table
    fraud_indicators_data = {
        'TransactionID': max_transaction+1,
        'FraudIndicator': fraud_prediction
    }
    fraud_indicators_df = pd.DataFrame(fraud_indicators_data, index=[0])
    fraud_indicators_df.to_sql('fraud_indicators', engine, if_exists='append', index=False)



    update_query = f"UPDATE account_activity SET AccountBalance = {balance_1 - transaction_amount}, LastLogin = \"{timestamp_now}\" WHERE CustomerID = {customer_id}"



    amount_data = {
        'TransactionID': max_transaction+1,
        'TransactionAmount': transaction_amount
    }
    amount_data_df = pd.DataFrame(amount_data, index=[0])
    amount_data_df.to_sql('amount_data', engine, if_exists='append', index=False)

    transaction_category_labels_data = {
        'TransactionID': max_transaction+1,
        'Category': category
    }
    transaction_category_labels_data_df = pd.DataFrame(transaction_category_labels_data, index=[0])
    transaction_category_labels_data_df.to_sql('transaction_category_labels', engine, if_exists='append', index=False)
    if fraud_prediction == 1:
        response = requests.get("https://httpbin.org/ip")
        public_ip = response.json().get("origin", "Unable to retrieve public IP")
        fraud_loc = get_geolocation(public_ip)
        frauds_data = {
            'TransactionID': max_transaction+1,
            'MerchantID': merchant_id,
            'CustomerID':customer_id,
            'Location':fraud_loc['city'],
            'TransactionAmount':transaction_amount,
            'TimeStamp':timestamp_now,
            'Coordinates':fraud_loc['loc'],
            'PostalCode': fraud_loc['postal'],
            'Region':fraud_loc['region'],
            'Country':fraud_loc['country'],
            'Timezone':fraud_loc['timezone'],
            'IPOrganization': fraud_loc['org']
        }

        def get_updated_fraud_data():
         query = "SELECT * FROM db1.frauds;"
         fraud_data = pd.read_sql_query(query, engine)
         fraud_json = fraud_data.to_json(orient='records')
         return fraud_json

        frauds_data_df = pd.DataFrame(frauds_data, index=[0])
        frauds_data_df.to_sql('frauds', engine, if_exists='append', index=False)
    update_query1 = f"UPDATE customer_view SET AccountBalance = {balance_1 - transaction_amount}, LastLogin = \"{timestamp_now}\" WHERE CustomerID = {customer_id}"
    update_query2 = f"INSERT INTO Age_Fraud_Chart (AgeRange, FraudCount) SELECT CONCAT(FLOOR((c.Age - 1) / 10) * 10, '-', FLOOR((c.Age - 1) / 10) * 10 + 10) AS AgeRange, COUNT(f.TransactionID) AS FraudCount FROM customer_data c JOIN frauds f ON c.CustomerID = f.CustomerID WHERE f.FraudIndicator = 1 GROUP BY AgeRange ORDER BY AgeRange ON DUPLICATE KEY UPDATE FraudCount=VALUES(FraudCount)"
    update_query3 = f"INSERT INTO category_chart(Category,FraudCount) select cc.Category, count(aa.TransactionID) as FraudCount from frauds aa join transaction_category_labels cc on aa.TransactionID = cc.TransactionID group by cc.Category ON DUPLICATE KEY UPDATE FraudCount=VALUES(FraudCount)"
    connection = pymysql.connect(host=host, user=user, password=password, database=database,port = port)
    cursor = connection.cursor()
    cursor.execute(update_query)
    connection.commit()
    cursor.execute(update_query1)
    connection.commit()
    cursor.close()
    connection.close()

    # Add similar updates for other tables based on your use case

if __name__ == "__main__":
    main()
    app.run(debug=True,host='0.0.0.0',port=5002)
