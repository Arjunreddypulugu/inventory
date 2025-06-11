import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

const BarcodeScanner = ({ onDetected, onClose }) => {
  const scannerRef = useRef(null);
  const html5QrCodeRef = useRef(null);
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    if (!scannerRef.current) return;

    html5QrCodeRef.current = new Html5Qrcode(scannerRef.current.id);

    html5QrCodeRef.current.start(
      { facingMode: "environment" },
      {
        fps: 10,
        qrbox: { width: 300, height: 200 }
      },
      async (decodedText) => {
        if (!scanned) {
          setScanned(true);
          await html5QrCodeRef.current.stop();
          await html5QrCodeRef.current.clear();
          onDetected(decodedText);
          if (onClose) onClose();
        }
      },
      (errorMessage) => {}
    );

    return () => {
      if (html5QrCodeRef.current) {
        html5QrCodeRef.current.stop().catch(() => {});
        html5QrCodeRef.current.clear().catch(() => {});
      }
    };
  // Only run once on mount
  // eslint-disable-next-line
  }, []);

  return (
    <div id="reader" ref={scannerRef} style={{ width: '100%', height: 320, margin: '1rem 0' }} />
  );
};

export default BarcodeScanner; 