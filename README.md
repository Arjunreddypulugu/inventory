# Inventory Management System

A Streamlit-based inventory management system with barcode scanning capabilities.

## Features

- Barcode scanning for SKU and Manufacturer Part Number
- Manual data entry option
- SQL Server database integration
- Responsive web interface
- Real-time form validation

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your database credentials:
```
DB_SERVER=your_server_name
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

3. Make sure you have the SQL Server ODBC driver installed on your system.

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. The application will open in your default web browser
2. You can either scan barcodes or manually enter data
3. SKU is the only required field
4. Click "Add to Inventory" to save the data

## Barcode Scanning

- Click the "Scan SKU" or "Scan MPN" button to activate the barcode scanner
- Position the barcode in front of your camera
- The scanner will automatically detect and fill in the value
- Click "Close Scanner" when done

## Database Schema

The application expects a table named `inventory` with the following columns:
- SKU (varchar)
- Manufacturer_Part_Number (varchar)
- Location (varchar)
- Quantity (int)
- Manufacturer (varchar)
- is_repeated (bit)

## Deployment

To deploy on Streamlit Cloud:
1. Push your code to a GitHub repository
2. Connect your repository to Streamlit Cloud
3. Add your environment variables in the Streamlit Cloud dashboard
4. Deploy the application 