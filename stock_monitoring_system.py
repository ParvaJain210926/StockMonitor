# stock_monitoring_system.py
import sqlite3
import time
import smtplib
from email.message import EmailMessage
import requests
import random

# ------------------ SETUP DUMMY DATABASES ------------------
def create_databases():
    # Local Inventory DB
    local_conn = sqlite3.connect("local_inventory.db")
    local_cursor = local_conn.cursor()
    local_cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            stock INTEGER
        )
    """)
    local_cursor.executemany("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", [
        ("p1", "Product A", 20),
        ("p2", "Product B", 20),
        ("p3", "Product C", 20),
    ])
    local_conn.commit()
    local_conn.close()

    # Wholesaler Inventory DB
    wholesaler_conn = sqlite3.connect("wholesaler_inventory.db")
    wholesaler_cursor = wholesaler_conn.cursor()
    wholesaler_cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            stock INTEGER
        )
    """)
    wholesaler_cursor.executemany("INSERT OR REPLACE INTO inventory VALUES (?, ?)", [
        ("p1", 50),
        ("p2", 50),
        ("p3", 50),
    ])
    wholesaler_conn.commit()
    wholesaler_conn.close()

    # Amazon Inventory (Dummy API simulation with local data)
    amazon_conn = sqlite3.connect("amazon_inventory.db")
    amazon_cursor = amazon_conn.cursor()
    amazon_cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            stock INTEGER
        )
    """)
    amazon_cursor.executemany("INSERT OR REPLACE INTO inventory VALUES (?, ?)", [
        ("p1",10),
        ("p2", 10),
        ("p3", 10),
    ])
    
    amazon_conn.commit()
    amazon_conn.close()


# ------------------ MAIN LOOP ------------------
def main():
    create_databases()

if __name__ == "__main__":
    main()
