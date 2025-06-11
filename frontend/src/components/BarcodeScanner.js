import React, { useRef, useEffect } from 'react';
import Quagga from '@ericblade/quagga2';

const BarcodeScanner = ({ onDetected }) => {
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
          "code_39_vin_reader",
          "codabar_reader",
          "upc_reader",
          "upc_e_reader",
          "i2of5_reader",
          "2of5_reader",
          "code_93_reader"
        ]
      },
      locate: true,
      numOfWorkers: 1,
      frequency: 10
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
    <div ref={scannerRef} style={{ width: '100%', height: 320, margin: '1rem 0' }} />
  );
};

export default BarcodeScanner; 