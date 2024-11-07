import mysql.connector
import re
import serial
import time
import logging

# Configure logging for debugging
logging.basicConfig(filename='sms_processing.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'icorerp_2'
}

# Connect to the database
def connect_to_db():
    try:
        connection = mysql.connector.connect(**db_config)
        logging.info("Database connection established.")
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        return None

# Parse M-Pesa transaction details from the SMS message

def parse_mpesa_message(message):
    # Updated regex to be more flexible with spacing and sender information
    match = re.search(
        r'([A-Z0-9]{10}) Confirmed\.You have received Ksh([\d,]+\.\d{2}) from (.+?) (\d{10}) on (\d{1,2}/\d{1,2}/\d{2}) at (\d{1,2}:\d{2} (?:AM|PM))',
        message
    )
    
    if match:
        transaction_id = match.group(1)
        amount = match.group(2).replace(',', '')  # Remove commas for numeric conversion
        sender_name = match.group(3).strip()  # Strip any leading/trailing spaces
        sender_phone = match.group(4)
        transaction_date = match.group(5)
        transaction_time = match.group(6)

        logging.debug(f"Transaction ID: {transaction_id}, Amount: {amount}, Sender Name: {sender_name}, Sender Phone: {sender_phone}, Date: {transaction_date}, Time: {transaction_time}")
        
        return {
            "transaction_id": transaction_id,
            "amount": amount,
            "sender_name": sender_name,
            "sender_phone": sender_phone,
            "transaction_date": transaction_date,
            "transaction_time": transaction_time
        }
    else:
        logging.warning("Failed to parse M-Pesa message: Pattern did not match.")
    
    return None


# Save SMS transaction to the database
def save_mpesa_transaction(parsed_data):
    # Check if the transaction already exists in the database
    transaction_id = parsed_data['transaction_id']
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Check if the transaction already exists
            cursor.execute("SELECT * FROM mpesa_transactions WHERE transaction_id = %s", (transaction_id,))
            result = cursor.fetchone()
            
            if result:
                logging.info(f"Transaction {transaction_id} already exists in the database. Skipping insert.")
            else:
                # Insert new transaction
                cursor.execute(
                    """
                    INSERT INTO mpesa_transactions (transaction_id, amount, sender_name, sender_phone, transaction_date, transaction_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        parsed_data['transaction_id'],
                        parsed_data['amount'],
                        parsed_data['sender_name'],
                        parsed_data['sender_phone'],
                        parsed_data['transaction_date'],
                        parsed_data['transaction_time']
                    )
                )
                connection.commit()
                logging.info(f"Saved M-Pesa transaction {transaction_id}.")
        except mysql.connector.Error as err:
            logging.error(f"Error saving M-Pesa transaction to database: {err}")
        finally:
            cursor.close()
            connection.close()

# Read SMS messages from the modem
def read_sms(ser):
    try:
        ser.write(b'AT+CMGF=1\r')
        time.sleep(1)
        ser.write(b'AT+CMGL="ALL"\r')
        time.sleep(1)

        response = ser.read_all().decode()
        logging.debug(f"Raw response from modem: {response}")

        if "+CMGL" in response:
            lines = response.splitlines()
            for line in lines:
                if line.startswith('+CMGL'):
                    message_content = lines[lines.index(line) + 1].strip()  # Actual message content
                    logging.debug(f"Processing message content: {message_content}")
                    
                    # Parse for M-Pesa
                    parsed_data = parse_mpesa_message(message_content)
                    logging.debug(f"Parsed M-Pesa data: {parsed_data}")

                    # If M-Pesa data was parsed successfully, save it
                    if parsed_data:
                        save_mpesa_transaction(parsed_data)
        else:
            logging.warning("No SMS messages found.")

    except Exception as e:
        logging.error(f"Error reading SMS: {e}")


# Main function to initialize modem connection and read SMS
def main():
    try:
        # Initialize serial connection with the modem
        ser = serial.Serial('COM10', baudrate=9600, timeout=5) #update with your respective port for your modem
        logging.info("Modem connected successfully.")

        while True:
            read_sms(ser)
            time.sleep(10)  # Wait before checking for new messages
    except serial.SerialException as e:
        logging.error(f"Error connecting to modem: {e}")
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            logging.info("Modem connection closed.")

# Run the main function
if __name__ == "__main__":
    main()
