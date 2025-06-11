import React, { useState } from 'react';
import BarcodeScannerComponent from 'react-qr-barcode-scanner';

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
          <BarcodeScannerComponent
            width={350}
            height={250}
            onUpdate={(err, result) => {
              if (err) setError('Camera error or permission denied');
              if (result) {
                setScanning(false);
                setError(null);
                onDetected(result.text);
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