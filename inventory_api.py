from flask import Flask, jsonify, request
import sqlite3
import threading
import time
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
CHECK_INTERVAL_SECONDS = 10 # 600=10min minutes
THRESHOLD_LOW = 5
THRESHOLD_REFILL = 2
USER_EMAIL = "parvjain123@yahoo.com"

# --------------- UTILITIES ---------------

def send_email(subject, body):
    sender ="jigar_shah35@yahoo.com"
    password = ""
    receiver = USER_EMAIL

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            #server.set_debuglevel(1)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            
            print("Email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_inventory_data(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    data = cursor.fetchall()
    conn.close()
    return data

def get_stock(db_name, product_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM inventory WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_stock(db_name, product_id, new_stock):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO inventory (product_id, stock) VALUES (?, ?)", (product_id, new_stock))
    conn.commit()
    conn.close()

# ------------ BACKGROUND MONITORING ------------

def monitor_stock():
    while True:
        print("Checking stock levels...")
        products = get_inventory_data("amazon_inventory.db")
        for product_id, stock in products:
            if stock == 5:
                send_email("Stock Low Warning", f"Product {product_id} stock is low (5 units).")
            if stock <= THRESHOLD_REFILL:
                # Try to refill from local
                local_stock = get_stock("local_inventory.db", product_id)
                if local_stock > 0:
                    refill = min(local_stock, 5)
                    update_stock("amazon_inventory.db", product_id, stock + refill)
                    update_stock("local_inventory.db", product_id, local_stock - refill)
                    send_email("Stock Refilled", f"Product {product_id} was refilled from local (added {refill}).")
                else:
                    # Try from wholesaler
                    wholesaler_stock = get_stock("wholesaler_inventory.db", product_id)
                    if wholesaler_stock > 0:
                        refill = min(wholesaler_stock, 5)
                        update_stock("amazon_inventory.db", product_id, stock + refill)
                        update_stock("wholesaler_inventory.db", product_id, wholesaler_stock - refill)
                        send_email("Stock Refilled", f"Product {product_id} was refilled from wholesaler (added {refill}).")
                    else:
                        send_email("Refill Failed", f"Product {product_id} could not be refilled from any source.")
        time.sleep(CHECK_INTERVAL_SECONDS)

# ------------------- ROUTES -------------------

@app.route("/amazon-inventory", methods=["GET"])
def get_amazon_inventory():
    data = get_inventory_data("amazon_inventory.db")
    return jsonify([{"product_id": row[0], "stock": row[1]} for row in data])

@app.route("/amazon-inventory", methods=["POST"])
def update_amazon_stock():
    data = request.get_json()
    product_id = data.get("product_id")
    stock = data.get("stock")
    update_stock("amazon_inventory.db", product_id, stock)
    return jsonify({"message": "Amazon stock updated"})

# ------------------- START -------------------

if __name__ == "__main__":
    monitor_thread = threading.Thread(target=monitor_stock, daemon=True)
    monitor_thread.start()
    app.run(debug=True, port=5000)
