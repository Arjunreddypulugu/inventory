import React, { useRef, useEffect } from 'react';
import Quagga from '@ericblade/quagga2';

const BarcodeScanner = ({ onDetected, label }) => {
  const scannerRef = useRef(null);

  useEffect(() => {
    if (!scannerRef.current) return;

    Quagga.init({
      inputStream: {
        type: "LiveStream",
        target: scannerRef.current,
        constraints: {
          facingMode: "environment"
        }
      },
      decoder: {
        readers: [
          "code_128_reader",
          "ean_reader",
          "ean_8_reader",
          "code_39_reader",
          "upc_reader",
          "upc_e_reader"
        ]
      }
    }, (err) => {
      if (err) {
        console.error(err);
        return;
      }
      Quagga.start();
    });

    Quagga.onDetected(data => {
      if (data && data.codeResult && data.codeResult.code) {
        onDetected(data.codeResult.code);
        Quagga.stop();
      }
    });

    return () => {
      Quagga.stop();
      Quagga.offDetected();
    };
  }, [onDetected]);

  return (
    <div style={{ textAlign: 'center', margin: '1rem 0' }}>
      <button
        type="button"
        onClick={() => {
          if (scannerRef.current) {
            Quagga.stop();
            Quagga.offDetected();
          }
        }}
        style={{ padding: '10px 20px', fontSize: '1rem', borderRadius: 8, background: '#28a745', color: '#fff', border: 'none', marginBottom: 10 }}
      >
        Stop Scanner
      </button>
      <div ref={scannerRef} style={{ width: '100%', height: 240 }} />
    </div>
  );
};

export default BarcodeScanner; 