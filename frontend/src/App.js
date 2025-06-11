import React, { useState, useCallback, useRef, useEffect } from 'react';
import axios from 'axios';
import { openHtml5QrcodeModal } from './components/Html5QrcodeModal';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [form, setForm] = useState({
    SKU: '',
    manufacturer_part_number: '',
    Location: '',
    Quantity: '',
    manufacturer: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [message, setMessage] = useState(null);
  const [lastScannedField, setLastScannedField] = useState(null);

  const skuRef = useRef(null);
  const mpnRef = useRef(null);
  const locationRef = useRef(null);
  const quantityRef = useRef(null);
  const manufacturerRef = useRef(null);

  useEffect(() => {
    if (skuRef.current) skuRef.current.focus();
  }, []);

  const handleChange = useCallback((e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  }, []);

  const handleScanModal = useCallback((field) => {
    if (scanning || submitting) return;
    setScanning(true);
    openHtml5QrcodeModal({
      onScan: (value) => {
        setForm(prev => ({ ...prev, [field]: value }));
        setLastScannedField(field);
        setMessage({ type: 'success', text: `${field} scanned and auto-filled!` });
        setScanning(false);
      },
      onClose: () => {
        setScanning(false);
      },
    });
  }, [scanning, submitting]);

  // Refined useEffect for SKU -> MPN jump only
  useEffect(() => {
    if (lastScannedField === 'SKU' && form.SKU && mpnRef.current) {
      console.log('Attempting to focus MPN after SKU scan');
      mpnRef.current.focus(); // Immediate attempt
      setTimeout(() => {
        console.log('Delayed focus on MPN after SKU scan');
        mpnRef.current.focus();
        setLastScannedField(null);
      }, 200);
    }
  }, [form.SKU, lastScannedField]);

  // Focus next field after scan
  useEffect(() => {
    if (lastScannedField === 'SKU' && mpnRef.current) {
      mpnRef.current.focus();
      setLastScannedField(null);
    } else if (lastScannedField === 'manufacturer_part_number' && locationRef.current) {
      locationRef.current.focus();
      setLastScannedField(null);
    } else if (lastScannedField === 'Location' && quantityRef.current) {
      quantityRef.current.focus();
      setLastScannedField(null);
    } else if (lastScannedField === 'Quantity' && manufacturerRef.current) {
      manufacturerRef.current.focus();
      setLastScannedField(null);
    }
  }, [form, lastScannedField]);

  const handleKeyDown = (e) => {
    // Prevent Enter from submitting the form
    if (e.key === 'Enter') {
      e.preventDefault();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting || scanning) return; // Prevent submission while scanning or already submitting
    
    setSubmitting(true);
    setMessage(null);
    
    try {
      console.log('Submitting form:', form); // Debug log
      const res = await axios.post(`${API_URL}/inventory/add`, form);
      console.log('Server response:', res.data); // Debug log
      
      if (res.data.is_repeated === "yes") {
        setMessage({ type: 'warning', text: 'SKU already exists. Marked as repeated.' });
      } else {
        setMessage({ type: 'success', text: 'Item added successfully!' });
      }
      // Only reset form after successful submission
      setForm({
        SKU: '',
        manufacturer_part_number: '',
        Location: '',
        Quantity: '',
        manufacturer: '',
      });
    } catch (err) {
      console.error('Error submitting form:', err); // Debug log
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.detail || 'Error adding item. Please try again.' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  const downloadInventory = async () => {
    try {
      const res = await fetch(`${API_URL}/inventory/download`);
      if (!res.ok) throw new Error('Failed to download');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'inventory_export.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to download Excel file.' });
    }
  };

  const isFormValid = form.SKU.trim() !== ''; // Basic validation

  return (
    <div style={{ maxWidth: 500, margin: '2rem auto', padding: 24, background: '#f8f9fa', borderRadius: 12, boxShadow: '0 2px 8px #0001' }}>
      <h2 style={{ textAlign: 'center' }}>📦 Inventory Management</h2>
      <form onSubmit={handleSubmit}>
        <label>SKU*:</label>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            ref={skuRef}
            name="SKU"
            value={form.SKU}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            required
            style={{ flex: 1, padding: 8, fontSize: 16 }}
            placeholder="Scan or enter SKU"
            disabled={scanning || submitting}
          />
          <button 
            type="button" 
            onClick={() => handleScanModal('SKU')} 
            disabled={scanning || submitting}
            style={{ 
              padding: '8px 16px', 
              background: scanning ? '#6c757d' : '#28a745', 
              color: '#fff', 
              border: 'none', 
              borderRadius: 6,
              cursor: scanning || submitting ? 'not-allowed' : 'pointer'
            }}
          >
            {scanning ? 'Scanning...' : 'Scan SKU'}
          </button>
        </div>
        <label>Manufacturer Part Number:</label>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            ref={mpnRef}
            name="manufacturer_part_number"
            value={form.manufacturer_part_number}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            style={{ flex: 1, padding: 8, fontSize: 16 }}
            placeholder="Scan or enter MPN"
            disabled={scanning || submitting}
          />
          <button 
            type="button" 
            onClick={() => handleScanModal('manufacturer_part_number')} 
            disabled={scanning || submitting}
            style={{ 
              padding: '8px 16px', 
              background: scanning ? '#6c757d' : '#28a745', 
              color: '#fff', 
              border: 'none', 
              borderRadius: 6,
              cursor: scanning || submitting ? 'not-allowed' : 'pointer'
            }}
          >
            {scanning ? 'Scanning...' : 'Scan MPN'}
          </button>
        </div>
        <label>Location:</label>
        <input
          ref={locationRef}
          name="Location"
          value={form.Location}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          style={{ width: '100%', padding: 8, fontSize: 16 }}
          placeholder="e.g., Warehouse A, Shelf 1"
          disabled={scanning || submitting}
        />
        <label>Quantity:</label>
        <input
          ref={quantityRef}
          name="Quantity"
          type="text"
          value={form.Quantity}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          style={{ width: '100%', padding: 8, fontSize: 16 }}
          placeholder="Enter quantity"
          disabled={scanning || submitting}
        />
        <label>Manufacturer:</label>
        <input
          ref={manufacturerRef}
          name="manufacturer"
          value={form.manufacturer}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          style={{ width: '100%', padding: 8, fontSize: 16 }}
          placeholder="e.g., Ford, Toyota, etc."
          disabled={scanning || submitting}
        />
        <button
          type="submit"
          disabled={submitting || scanning || !isFormValid}
          style={{ 
            width: '100%', 
            marginTop: 18, 
            padding: 12, 
            fontSize: 18, 
            background: !isFormValid ? '#6c757d' : '#007bff', 
            color: '#fff', 
            border: 'none', 
            borderRadius: 8,
            cursor: (submitting || scanning || !isFormValid) ? 'not-allowed' : 'pointer'
          }}
        >
          {submitting ? 'Submitting...' : 'Add to Inventory'}
        </button>
        <button
          type="button"
          onClick={downloadInventory}
          style={{
            width: '100%',
            marginTop: 18,
            padding: 12,
            fontSize: 18,
            background: '#17a2b8',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
          }}
        >
          Download Inventory (Excel)
        </button>
      </form>
      {message && (
        <div style={{ 
          marginTop: 16, 
          padding: 12,
          borderRadius: 6,
          backgroundColor: message.type === 'error' ? '#f8d7da' : 
                          message.type === 'warning' ? '#fff3cd' : 
                          '#d4edda',
          color: message.type === 'error' ? '#721c24' : 
                 message.type === 'warning' ? '#856404' : 
                 '#155724',
          fontWeight: 600, 
          textAlign: 'center' 
        }}>
          {message.text}
        </div>
      )}
    </div>
  );
}

export default App;
