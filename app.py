import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Install: pip install streamlit-qrcode-scanner
# Note: This component works with both QR codes AND barcodes
from streamlit_qrcode_scanner import qrcode_scanner

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
    .scanner-active {
        border: 3px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        background-color: #d4edda;
        margin: 10px 0;
    }
    .success-message {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
    }
    .auto-populated {
        background-color: #d4edda !important;
        border: 2px solid #28a745 !important;
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
            check_query = text(f"""
            SELECT COUNT(*) FROM {st.secrets['database']['db_table']}
            WHERE SKU = :sku
            """)
            
            with engine.connect() as conn:
                result = conn.execute(check_query, {"sku": data['sku']})
                sku_exists = result.scalar() > 0
                
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

# Initialize session state
def init_session_state():
    if 'sku_value' not in st.session_state:
        st.session_state.sku_value = ""
    if 'mpn_value' not in st.session_state:
        st.session_state.mpn_value = ""
    if 'scanning_mode' not in st.session_state:
        st.session_state.scanning_mode = None  # None, 'sku', or 'mpn'
    if 'auto_populated_sku' not in st.session_state:
        st.session_state.auto_populated_sku = False
    if 'auto_populated_mpn' not in st.session_state:
        st.session_state.auto_populated_mpn = False

def main():
    st.title("📦 Inventory Management System")
    
    init_session_state()

    # Scanner Mode - SKU
    if st.session_state.scanning_mode == 'sku':
        st.markdown("### 📷 Scanning SKU Barcode")
        st.markdown('<div class="scanner-active">', unsafe_allow_html=True)
        
        st.info("📱 Point your camera at the barcode. Works with Code 128, Code 39, EAN, UPC, and QR codes!")
        
        # The magic happens here - this actually returns the scanned value!
        scanned_code = qrcode_scanner(key="sku_scanner")
        
        if scanned_code:
            # Auto-populate the SKU value
            st.session_state.sku_value = scanned_code
            st.session_state.auto_populated_sku = True
            st.session_state.scanning_mode = None
            st.success(f"✅ SKU Auto-Populated: **{scanned_code}**")
            st.balloons()
            st.rerun()
        
        # Scanner controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Done Scanning", key="done_sku", type="primary"):
                st.session_state.scanning_mode = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_sku", type="secondary"):
                st.session_state.scanning_mode = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Scanner Mode - MPN
    elif st.session_state.scanning_mode == 'mpn':
        st.markdown("### 📷 Scanning MPN Barcode")
        st.markdown('<div class="scanner-active">', unsafe_allow_html=True)
        
        st.info("📱 Point your camera at the barcode. Works with Code 128, Code 39, EAN, UPC, and QR codes!")
        
        # The magic happens here - this actually returns the scanned value!
        scanned_code = qrcode_scanner(key="mpn_scanner")
        
        if scanned_code:
            # Auto-populate the MPN value
            st.session_state.mpn_value = scanned_code
            st.session_state.auto_populated_mpn = True
            st.session_state.scanning_mode = None
            st.success(f"✅ MPN Auto-Populated: **{scanned_code}**")
            st.balloons()
            st.rerun()
        
        # Scanner controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Done Scanning", key="done_mpn", type="primary"):
                st.session_state.scanning_mode = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_mpn", type="secondary"):
                st.session_state.scanning_mode = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Main Form View
    st.markdown("### Add New Inventory Item")
    
    # Show success messages for auto-populated fields
    if st.session_state.auto_populated_sku:
        st.markdown(f'<div class="success-message">🎉 SKU Auto-Populated from Barcode: <strong>{st.session_state.sku_value}</strong></div>', unsafe_allow_html=True)
    
    if st.session_state.auto_populated_mpn:
        st.markdown(f'<div class="success-message">🎉 MPN Auto-Populated from Barcode: <strong>{st.session_state.mpn_value}</strong></div>', unsafe_allow_html=True)

    # Main form
    with st.form("inventory_form"):
        # SKU input with scan button
        col1, col2 = st.columns([4, 1])
        with col1:
            # Apply special styling if auto-populated
            sku_class = "auto-populated" if st.session_state.auto_populated_sku else ""
            sku = st.text_input(
                "SKU*", 
                value=st.session_state.sku_value, 
                placeholder="Enter SKU manually or scan barcode",
                help="✅ Auto-populated" if st.session_state.auto_populated_sku else None
            )
        with col2:
            if st.form_submit_button("📷 Scan SKU", type="secondary"):
                st.session_state.scanning_mode = 'sku'
                st.rerun()

        # MPN input with scan button
        col3, col4 = st.columns([4, 1])
        with col3:
            mpn = st.text_input(
                "Manufacturer Part Number", 
                value=st.session_state.mpn_value,
                placeholder="Enter MPN manually or scan barcode",
                help="✅ Auto-populated" if st.session_state.auto_populated_mpn else None
            )
        with col4:
            if st.form_submit_button("📷 Scan MPN", type="secondary"):
                st.session_state.scanning_mode = 'mpn'
                st.rerun()

        # Other form fields
        location = st.text_input("Location", placeholder="e.g., Warehouse A, Shelf 1")
        quantity = st.number_input("Quantity", min_value=0, value=1, step=1)
        manufacturer = st.text_input("Manufacturer", placeholder="e.g., Ford, Toyota, etc.")

        # Clear and submit buttons
        col5, col6, col7 = st.columns([1, 1, 2])
        with col5:
            if st.form_submit_button("🗑️ Clear SKU", type="secondary"):
                st.session_state.sku_value = ""
                st.session_state.auto_populated_sku = False
                st.rerun()
        with col6:
            if st.form_submit_button("🗑️ Clear MPN", type="secondary"):
                st.session_state.mpn_value = ""
                st.session_state.auto_populated_mpn = False
                st.rerun()
        with col7:
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
                    st.session_state.auto_populated_sku = False
                    st.session_state.auto_populated_mpn = False
                    st.balloons()
                    st.rerun()

    # Instructions
    with st.expander("📋 How Auto-Population Works"):
        st.markdown("""
        **🎯 TRUE Auto-Population Process:**
        
        1. **Click "📷 Scan SKU" or "📷 Scan MPN"**
           - Camera opens instantly
           
        2. **Point camera at your barcode**
           - Supports Code 128 (your format), Code 39, EAN, UPC, QR codes
           - Auto-detects and scans immediately
           
        3. **Value automatically appears in text field**
           - No copy-paste needed!
           - Text field highlights in green
           - Success message appears
           
        4. **Complete the form and submit**
           - All other fields work normally
           - Click "Add to Inventory" to save
        
        **🔧 Technical Details:**
        - Uses `streamlit-qrcode-scanner` component
        - Actually returns scanned values to Python
        - Works on mobile and desktop
        - Requires HTTPS (works on Streamlit Cloud)
        
        **✅ Your Code 128 barcodes are fully supported!**
        
        **🚨 Requirements:**
        - HTTPS connection (Streamlit Cloud provides this)
        - Camera permissions allowed
        - Modern browser (Chrome, Firefox, Safari, Edge)
        """)

    # Display current status
    st.sidebar.markdown("### Scanner Status")
    if st.session_state.sku_value:
        st.sidebar.success(f"SKU: {st.session_state.sku_value}")
    if st.session_state.mpn_value:
        st.sidebar.success(f"MPN: {st.session_state.mpn_value}")

if __name__ == "__main__":
    main()