import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
import time
from sqlalchemy import create_engine, text

# Page config
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .scanner-container {
        border: 2px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .scanner-active {
        border-color: #28a745;
        background-color: #d4edda;
    }
    .scanned-result {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection function
@st.cache_resource
def init_connection():
    try:
        connection_string = f"mssql+pymssql://{st.secrets['database']['db_username']}:{st.secrets['database']['db_password']}@{st.secrets['database']['db_server']}/{st.secrets['database']['db_database']}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

# Function to insert data into database
def insert_inventory_data(data):
    try:
        engine = init_connection()
        if engine:
            # Check if SKU exists
            check_query = text(f"""
            SELECT COUNT(*) FROM {st.secrets['database']['db_table']}
            WHERE SKU = :sku
            """)
            
            with engine.connect() as conn:
                result = conn.execute(check_query, {"sku": data['sku']})
                sku_exists = result.scalar() > 0
                
                # Insert the data
                insert_query = text(f"""
                INSERT INTO {st.secrets['database']['db_table']} 
                (SKU, Manufacturer_Part_Number, Location, Quantity, Manufacturer, is_repeated)
                VALUES (:sku, :mpn, :location, :quantity, :manufacturer, :is_repeated)
                """)
                
                conn.execute(insert_query, {
                    "sku": data['sku'],
                    "mpn": data['mpn'],
                    "location": data['location'],
                    "quantity": data['quantity'],
                    "manufacturer": data['manufacturer'],
                    "is_repeated": sku_exists
                })
                conn.commit()
            
            if sku_exists:
                st.warning("⚠️ This SKU already exists in the database. Marked as repeated.")
            else:
                st.success("✅ New SKU added successfully!")
            return True
    except Exception as e:
        st.error(f"❌ Error inserting data: {str(e)}")
        return False

# Barcode scanner component that returns the scanned value
def barcode_scanner_component(key_suffix=""):
    scanner_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/quagga@0.12.1/dist/quagga.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: Arial, sans-serif;
            }}
            #scanner {{
                width: 100%;
                height: 300px;
                border: 2px solid #ddd;
                border-radius: 5px;
                position: relative;
                background-color: #000;
            }}
            .controls {{
                margin: 10px 0;
                text-align: center;
            }}
            button {{
                margin: 5px;
                padding: 10px 20px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            }}
            .start-btn {{
                background-color: #28a745;
                color: white;
            }}
            .stop-btn {{
                background-color: #dc3545;
                color: white;
            }}
            .result {{
                margin-top: 15px;
                padding: 15px;
                background-color: #e7f3ff;
                border: 2px solid #007bff;
                border-radius: 5px;
                display: none;
            }}
            .result.show {{
                display: block;
            }}
            .scanned-code {{
                font-family: monospace;
                font-size: 18px;
                font-weight: bold;
                color: #0056b3;
                word-break: break-all;
                margin: 10px 0;
            }}
            .status {{
                margin: 10px 0;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            .status.success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .status.error {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
        </style>
    </head>
    <body>
        <div class="controls">
            <button id="startBtn" class="start-btn" onclick="startScanner()">📷 Start Scanner</button>
            <button id="stopBtn" class="stop-btn" onclick="stopScanner()" style="display:none;">⏹️ Stop Scanner</button>
        </div>
        
        <div id="scanner"></div>
        
        <div id="status" class="status" style="display:none;"></div>
        
        <div id="result" class="result">
            <h4>✅ Barcode Detected!</h4>
            <div class="scanned-code" id="scannedCode"></div>
            <div class="controls">
                <button class="start-btn" onclick="useCode()">✅ Use This Code</button>
                <button class="start-btn" onclick="scanAgain()">🔄 Scan Another</button>
            </div>
        </div>

        <script>
            let scannerActive = false;
            let lastScannedCode = '';

            function showStatus(message, isError = false) {{
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = `status ${{isError ? 'error' : 'success'}}`;
                status.style.display = 'block';
                
                setTimeout(() => {{
                    status.style.display = 'none';
                }}, 3000);
            }}

            function startScanner() {{
                if (scannerActive) return;
                
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
                document.getElementById('result').classList.remove('show');
                
                showStatus('Initializing camera...');
                
                Quagga.init({{
                    inputStream: {{
                        name: "Live",
                        type: "LiveStream",
                        target: document.querySelector("#scanner"),
                        constraints: {{
                            width: 640,
                            height: 480,
                            facingMode: "environment"
                        }},
                    }},
                    decoder: {{
                        readers: [
                            "code_128_reader", 
                            "ean_reader", 
                            "ean_8_reader", 
                            "code_39_reader", 
                            "upc_reader", 
                            "upc_e_reader"
                        ]
                    }}
                }}, function(err) {{
                    if (err) {{
                        console.error('Scanner initialization error:', err);
                        showStatus('❌ Camera access denied or not available', true);
                        resetButtons();
                        return;
                    }}
                    
                    showStatus('✅ Scanner ready - point camera at barcode');
                    Quagga.start();
                    scannerActive = true;
                }});

                Quagga.onDetected(function(result) {{
                    const code = result.codeResult.code;
                    if (code && code.length > 2) {{
                        lastScannedCode = code;
                        document.getElementById('scannedCode').textContent = code;
                        document.getElementById('result').classList.add('show');
                        showStatus('✅ Barcode detected successfully!');
                        stopScanner();
                    }}
                }});
            }}

            function stopScanner() {{
                if (scannerActive) {{
                    Quagga.stop();
                    scannerActive = false;
                }}
                resetButtons();
            }}

            function resetButtons() {{
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
            }}

            function useCode() {{
                if (lastScannedCode) {{
                    // Return the scanned code to Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:componentData',
                        data: lastScannedCode
                    }}, '*');
                }}
            }}

            function scanAgain() {{
                document.getElementById('result').classList.remove('show');
                lastScannedCode = '';
                startScanner();
            }}

            // Cleanup on page unload
            window.addEventListener('beforeunload', function() {{
                if (scannerActive) {{
                    Quagga.stop();
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Return the HTML component and capture its return value
    return html(scanner_html, height=500)

# Initialize session state
def init_session_state():
    if 'sku_value' not in st.session_state:
        st.session_state.sku_value = ""
    if 'mpn_value' not in st.session_state:
        st.session_state.mpn_value = ""
    if 'scanner_mode' not in st.session_state:
        st.session_state.scanner_mode = None  # None, 'sku', or 'mpn'
    if 'last_scan_time' not in st.session_state:
        st.session_state.last_scan_time = 0

def main():
    st.title("📦 Inventory Management System")
    
    init_session_state()

    # Scanner mode handling
    if st.session_state.scanner_mode == 'sku':
        st.markdown("### 📷 Scanning SKU Barcode")
        st.markdown('<div class="scanner-container scanner-active">', unsafe_allow_html=True)
        
        # Create scanner and get result
        scanner_result = barcode_scanner_component("sku")
        
        # Check if we got a scanned result
        if scanner_result:
            st.session_state.sku_value = scanner_result
            st.session_state.scanner_mode = None
            st.success(f"✅ SKU scanned: {scanner_result}")
            time.sleep(1)  # Brief pause to show success message
            st.rerun()
        
        # Controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Done", key="done_sku_scan"):
                st.session_state.scanner_mode = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_sku_scan"):
                st.session_state.scanner_mode = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        return  # Don't show the form while scanning

    elif st.session_state.scanner_mode == 'mpn':
        st.markdown("### 📷 Scanning MPN Barcode")
        st.markdown('<div class="scanner-container scanner-active">', unsafe_allow_html=True)
        
        # Create scanner and get result
        scanner_result = barcode_scanner_component("mpn")
        
        # Check if we got a scanned result
        if scanner_result:
            st.session_state.mpn_value = scanner_result
            st.session_state.scanner_mode = None
            st.success(f"✅ MPN scanned: {scanner_result}")
            time.sleep(1)  # Brief pause to show success message
            st.rerun()
        
        # Controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Done", key="done_mpn_scan"):
                st.session_state.scanner_mode = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_mpn_scan"):
                st.session_state.scanner_mode = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        return  # Don't show the form while scanning

    # Main form (only shown when not scanning)
    st.markdown("### Add New Inventory Item")
    
    # Show scanned values if available
    if st.session_state.sku_value:
        st.markdown(f'<div class="scanned-result">📊 Current SKU: <strong>{st.session_state.sku_value}</strong></div>', 
                   unsafe_allow_html=True)
    
    if st.session_state.mpn_value:
        st.markdown(f'<div class="scanned-result">🏷️ Current MPN: <strong>{st.session_state.mpn_value}</strong></div>', 
                   unsafe_allow_html=True)

    # Form
    with st.form("inventory_form"):
        # SKU field with scanner button
        col1, col2 = st.columns([4, 1])
        with col1:
            sku = st.text_input("SKU*", value=st.session_state.sku_value, 
                               placeholder="Enter SKU or use scanner")
        with col2:
            if st.form_submit_button("📷 Scan SKU"):
                st.session_state.scanner_mode = 'sku'
                st.rerun()

        # Manufacturer Part Number field with scanner button  
        col3, col4 = st.columns([4, 1])
        with col3:
            mpn = st.text_input("Manufacturer Part Number", value=st.session_state.mpn_value,
                               placeholder="Enter MPN or use scanner")
        with col4:
            if st.form_submit_button("📷 Scan MPN"):
                st.session_state.scanner_mode = 'mpn'
                st.rerun()

        # Other fields
        location = st.text_input("Location", placeholder="e.g., Warehouse A, Shelf 1")
        quantity = st.number_input("Quantity", min_value=0, value=1, step=1)
        manufacturer = st.text_input("Manufacturer", placeholder="e.g., Ford, Toyota, etc.")

        # Clear buttons
        col5, col6, col7 = st.columns([1, 1, 2])
        with col5:
            if st.form_submit_button("🗑️ Clear SKU"):
                st.session_state.sku_value = ""
                st.rerun()
        with col6:
            if st.form_submit_button("🗑️ Clear MPN"):
                st.session_state.mpn_value = ""
                st.rerun()

        # Submit button
        submitted = st.form_submit_button("➕ Add to Inventory", type="primary")

        # Handle form submission
        if submitted:
            if not sku.strip():
                st.error("❌ SKU is required!")
            else:
                data = {
                    'sku': sku.strip(),
                    'mpn': mpn.strip(),
                    'location': location.strip(),
                    'quantity': quantity,
                    'manufacturer': manufacturer.strip()
                }
                
                if insert_inventory_data(data):
                    # Clear all values after successful submission
                    st.session_state.sku_value = ""
                    st.session_state.mpn_value = ""
                    st.balloons()
                    st.rerun()

    # Instructions
    with st.expander("📋 How to Use"):
        st.markdown("""
        **Step-by-step instructions:**
        
        1. **For SKU (Required):**
           - Type manually in the SKU field, OR
           - Click "📷 Scan" button to open barcode scanner
           
        2. **For MPN (Optional):**
           - Type manually in the MPN field, OR  
           - Click "📷 Scan" button to open barcode scanner
           
        3. **Scanning Process:**
           - Allow camera access when prompted
           - Point camera at barcode until it auto-detects
           - Click "✅ Use This Code" to apply the scanned value
           - Or click "🔄 Scan Another" to try again
           
        4. **Complete the form:**
           - Fill in Location, Quantity, and Manufacturer
           - Click "➕ Add to Inventory" to save
           
        **Supported barcode formats:** Code 128, Code 39, EAN, UPC
        
        **Your barcode type:** ✅ Compatible (Code 128)
        """)

if __name__ == "__main__":
    main()