import streamlit as st
import pyodbc
import pandas as pd
from streamlit.components.v1 import html
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .scanner-container {
        border: 2px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection function
@st.cache_resource
def init_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{st.secrets['database']['driver']}}};"
            f"SERVER={st.secrets['database']['db_server']};"
            f"DATABASE={st.secrets['database']['db_database']};"
            f"UID={st.secrets['database']['db_username']};"
            f"PWD={st.secrets['database']['db_password']}"
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

# Barcode scanner HTML component
def barcode_scanner_html():
    return """
    <div id="interactive" class="viewport"></div>
    <script src="https://unpkg.com/quagga@0.12.1/dist/quagga.min.js"></script>
    <script>
        function initScanner() {
            Quagga.init({
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: document.querySelector("#interactive"),
                    constraints: {
                        facingMode: "environment"
                    },
                },
                decoder: {
                    readers: ["code_128_reader", "ean_reader", "ean_8_reader", "code_39_reader", "upc_reader", "upc_e_reader"]
                }
            }, function(err) {
                if (err) {
                    console.error(err);
                    return;
                }
                Quagga.start();
            });

            Quagga.onDetected(function(result) {
                if (result.codeResult.code) {
                    window.parent.postMessage({
                        type: 'barcode-scanned',
                        value: result.codeResult.code
                    }, '*');
                    Quagga.stop();
                }
            });
        }

        // Initialize scanner when component is loaded
        window.addEventListener('load', initScanner);
    </script>
    """

# Function to insert data into database
def insert_inventory_data(data):
    try:
        conn = init_connection()
        if conn:
            cursor = conn.cursor()
            query = f"""
            INSERT INTO {st.secrets['database']['db_table']} (SKU, Manufacturer_Part_Number, Location, Quantity, Manufacturer, is_repeated)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                data['sku'],
                data['mpn'],
                data['location'],
                data['quantity'],
                data['manufacturer'],
                False
            ))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error inserting data: {str(e)}")
        return False

def main():
    st.title("📦 Inventory Management System")

    # Initialize session state for barcode scanning
    if 'scanned_sku' not in st.session_state:
        st.session_state.scanned_sku = ""
    if 'scanned_mpn' not in st.session_state:
        st.session_state.scanned_mpn = ""

    # Create form
    with st.form("inventory_form"):
        # SKU field with scanner
        col1, col2 = st.columns([3, 1])
        with col1:
            sku = st.text_input("SKU*", value=st.session_state.scanned_sku)
        with col2:
            if st.button("📷 Scan SKU"):
                st.session_state.show_sku_scanner = True

        # Manufacturer Part Number field with scanner
        col3, col4 = st.columns([3, 1])
        with col3:
            mpn = st.text_input("Manufacturer Part Number", value=st.session_state.scanned_mpn)
        with col4:
            if st.button("📷 Scan MPN"):
                st.session_state.show_mpn_scanner = True

        # Other fields
        location = st.text_input("Location")
        quantity = st.number_input("Quantity", min_value=0, value=0)
        manufacturer = st.text_input("Manufacturer")

        # Submit button
        submitted = st.form_submit_button("Add to Inventory")

        if submitted:
            if not sku:
                st.error("SKU is required!")
            else:
                data = {
                    'sku': sku,
                    'mpn': mpn,
                    'location': location,
                    'quantity': quantity,
                    'manufacturer': manufacturer
                }
                if insert_inventory_data(data):
                    st.success("Data added successfully!")
                    # Clear session state
                    st.session_state.scanned_sku = ""
                    st.session_state.scanned_mpn = ""

    # Display scanners when needed
    if st.session_state.get('show_sku_scanner'):
        st.markdown("### SKU Scanner")
        html(barcode_scanner_html(), height=400)
        if st.button("Close Scanner"):
            st.session_state.show_sku_scanner = False
            st.experimental_rerun()

    if st.session_state.get('show_mpn_scanner'):
        st.markdown("### MPN Scanner")
        html(barcode_scanner_html(), height=400)
        if st.button("Close Scanner"):
            st.session_state.show_mpn_scanner = False
            st.experimental_rerun()

    # JavaScript to handle barcode scanning
    st.markdown("""
        <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'barcode-scanned') {
                    // Send the scanned value back to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: event.data.value
                    }, '*');
                }
            });
        </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 