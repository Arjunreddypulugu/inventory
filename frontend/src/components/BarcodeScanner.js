import React, { useEffect, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

const BarcodeScanner = ({ onDetected }) => {
  const scannerRef = useRef(null);
  const html5QrCodeRef = useRef(null);

  useEffect(() => {
    if (!scannerRef.current) return;

    html5QrCodeRef.current = new Html5Qrcode(scannerRef.current.id);

    html5QrCodeRef.current.start(
      { facingMode: "environment" },
      {
        fps: 10,
        qrbox: { width: 300, height: 200 }
      },
      (decodedText) => {
        onDetected(decodedText);
        html5QrCodeRef.current.stop();
      },
      (errorMessage) => {
        // ignore errors for now
      }
    );

    return () => {
      if (html5QrCodeRef.current) {
        html5QrCodeRef.current.stop().catch(() => {});
        html5QrCodeRef.current.clear();
      }
    };
  }, [onDetected]);

  return (
    <div id="reader" ref={scannerRef} style={{ width: '100%', height: 320, margin: '1rem 0' }} />
  );
};

export default BarcodeScanner; 