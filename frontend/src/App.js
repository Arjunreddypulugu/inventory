import React, { useState } from 'react';
import axios from 'axios';
import BarcodeScanner from './components/BarcodeScanner';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [form, setForm] = useState({
    sku: '',
    manufacturer_part_number: '',
    location: '',
    quantity: 1,
    manufacturer: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleScan = (field) => (value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setMessage({ type: 'success', text: `${field.toUpperCase()} scanned and auto-filled!` });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const res = await axios.post(`${API_URL}/inventory/add`, {
        ...form,
        quantity: Number(form.quantity),
      });
      if (res.data.is_repeated) {
        setMessage({ type: 'warning', text: 'SKU already exists. Marked as repeated.' });
      } else {
        setMessage({ type: 'success', text: 'Item added successfully!' });
      }
      setForm({
        sku: '',
        manufacturer_part_number: '',
        location: '',
        quantity: 1,
        manufacturer: '',
      });
    } catch (err) {
      setMessage({ type: 'error', text: 'Error adding item. Please try again.' });
    }
    setSubmitting(false);
  };

  return (
    <div style={{ maxWidth: 500, margin: '2rem auto', padding: 24, background: '#f8f9fa', borderRadius: 12, boxShadow: '0 2px 8px #0001' }}>
      <h2 style={{ textAlign: 'center' }}>📦 Inventory Management</h2>
      <form onSubmit={handleSubmit}>
        <label>SKU*:</label>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            name="sku"
            value={form.sku}
            onChange={handleChange}
            required
            style={{ flex: 1, padding: 8, fontSize: 16 }}
            placeholder="Scan or enter SKU"
          />
          <BarcodeScanner onDetected={handleScan('sku')} label="SKU" />
        </div>
        <label>Manufacturer Part Number:</label>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            name="manufacturer_part_number"
            value={form.manufacturer_part_number}
            onChange={handleChange}
            style={{ flex: 1, padding: 8, fontSize: 16 }}
            placeholder="Scan or enter MPN"
          />
          <BarcodeScanner onDetected={handleScan('manufacturer_part_number')} label="MPN" />
        </div>
        <label>Location:</label>
        <input
          name="location"
          value={form.location}
          onChange={handleChange}
          style={{ width: '100%', padding: 8, fontSize: 16 }}
          placeholder="e.g., Warehouse A, Shelf 1"
        />
        <label>Quantity:</label>
        <input
          name="quantity"
          type="number"
          min={1}
          value={form.quantity}
          onChange={handleChange}
          style={{ width: '100%', padding: 8, fontSize: 16 }}
        />
        <label>Manufacturer:</label>
        <input
          name="manufacturer"
          value={form.manufacturer}
          onChange={handleChange}
          style={{ width: '100%', padding: 8, fontSize: 16 }}
          placeholder="e.g., Ford, Toyota, etc."
        />
        <button
          type="submit"
          disabled={submitting}
          style={{ width: '100%', marginTop: 18, padding: 12, fontSize: 18, background: '#007bff', color: '#fff', border: 'none', borderRadius: 8 }}
        >
          {submitting ? 'Submitting...' : 'Add to Inventory'}
        </button>
      </form>
      {message && (
        <div style={{ marginTop: 16, color: message.type === 'error' ? 'red' : message.type === 'warning' ? '#b8860b' : 'green', fontWeight: 600, textAlign: 'center' }}>
          {message.text}
        </div>
      )}
    </div>
  );
}

export default App;
