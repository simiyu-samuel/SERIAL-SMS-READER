# SERIAL-SMS-READER

Python script designed to read, parse, and store SMS messages containing M-Pesa transaction details. This script can help you automate the process of capturing and storing M-Pesa transaction information for further processing, such as recording payments, generating invoices, or updating a database.
From a connected modem in a PC, the script captures all incoming mpesa sms and stores them in mysql database.

## Features

- Reads SMS messages from a configured SMS source. (Source example is a modem with a sim card)
- Parses M-Pesa transaction messages using regular expressions.
- Filters out non-M-Pesa messages.
- Stores parsed transaction data in a database, preventing duplicate entries.
- Logs all messages processed, including errors and parsed data.

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/yourusername/sms_reader.git
   cd sms_reader
   ```
2. **Install required Python packages: The script may require the following Python packages:**

   mysql-connector-python for MySQL database connection.
   re (Python standard library) for regular expression parsing.
## Mysql table
CREATE TABLE mpesa_transactions (
transaction_id VARCHAR(255) PRIMARY KEY,
amount DECIMAL(10, 2),
sender_name VARCHAR(255),
sender_phone VARCHAR(20),
transaction_date DATE,
transaction_time TIME
);

## Configure Database Connection: Update the database connection details within sms_reader.py:

## db_config = {

## 'user': 'your_db_user',

## 'password': 'your_db_password',

## 'host': 'your_db_host',

## 'database': 'your_db_name'

## }

**How It Works:**

The script reads SMS messages from a pre-defined source or API.
Each SMS message is processed to determine if it’s an M-Pesa transaction message.
If the message matches the M-Pesa format, it parses details like transaction ID, amount, sender name, phone number, date, and time.
The parsed data is then stored in the database.
Duplicate transactions are avoided by checking if the transaction ID already exists in the database.
Logging: The script logs each SMS message processed, including errors encountered. Logs are written to sms_processing.log and contain detailed information such as:

Processing results (e.g., successful parse, failed parse).
Database errors (e.g., if the database connection fails or a duplicate transaction is detected).


***Made with Love by Samuel Simiyu****
