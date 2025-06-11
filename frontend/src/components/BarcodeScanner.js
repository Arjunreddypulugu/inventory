import React, { useState } from 'react';
import BarcodeReader from 'react-barcode-reader';

const BarcodeScanner = ({ onDetected, label }) => {
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);

  return (
    <div style={{ textAlign: 'center', margin: '1rem 0' }}>
      <button
        type="button"
        onClick={() => setScanning((s) => !s)}
        style={{ padding: '10px 20px', fontSize: '1rem', borderRadius: 8, background: '#28a745', color: '#fff', border: 'none', marginBottom: 10 }}
      >
        {scanning ? `Stop ${label} Scanner` : `Scan ${label}`}
      </button>
      {scanning && (
        <div style={{ margin: '1rem auto', maxWidth: 400 }}>
          <BarcodeReader
            onError={err => setError('Camera error or permission denied')}
            onScan={result => {
              if (result) {
                setScanning(false);
                setError(null);
                onDetected(result);
              }
            }}
          />
          {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
        </div>
      )}
    </div>
  );
};

export default BarcodeScanner; 