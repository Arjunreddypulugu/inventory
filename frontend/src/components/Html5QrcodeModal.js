import { Html5Qrcode } from 'html5-qrcode';

// Utility to open a modal and scan a barcode using html5-qrcode outside React
export function openHtml5QrcodeModal({ onScan, onClose }) {
  // Create modal DOM
  const modal = document.createElement('div');
  modal.style.position = 'fixed';
  modal.style.top = 0;
  modal.style.left = 0;
  modal.style.width = '100vw';
  modal.style.height = '100vh';
  modal.style.background = 'rgba(0,0,0,0.8)';
  modal.style.display = 'flex';
  modal.style.alignItems = 'center';
  modal.style.justifyContent = 'center';
  modal.style.zIndex = 9999;

  // Modal content
  const content = document.createElement('div');
  content.style.background = '#fff';
  content.style.borderRadius = '12px';
  content.style.padding = '16px';
  content.style.boxShadow = '0 2px 16px #0005';
  content.style.position = 'relative';
  content.style.width = '340px';
  content.style.maxWidth = '95vw';

  // Close button
  const closeBtn = document.createElement('button');
  closeBtn.innerText = '✕';
  closeBtn.style.position = 'absolute';
  closeBtn.style.top = '8px';
  closeBtn.style.right = '8px';
  closeBtn.style.background = 'transparent';
  closeBtn.style.border = 'none';
  closeBtn.style.fontSize = '1.5rem';
  closeBtn.style.cursor = 'pointer';
  closeBtn.onclick = cleanup;

  // Scanner div
  const scannerDiv = document.createElement('div');
  scannerDiv.id = 'html5-qrcode-modal-scanner';
  scannerDiv.style.width = '300px';
  scannerDiv.style.height = '240px';
  scannerDiv.style.margin = '0 auto';

  content.appendChild(closeBtn);
  content.appendChild(scannerDiv);
  modal.appendChild(content);
  document.body.appendChild(modal);

  let html5QrCode = new Html5Qrcode('html5-qrcode-modal-scanner');
  let scanned = false;

  html5QrCode.start(
    { facingMode: 'environment' },
    { fps: 10, qrbox: { width: 250, height: 180 } },
    async (decodedText) => {
      if (!scanned) {
        scanned = true;
        await html5QrCode.stop();
        await html5QrCode.clear();
        cleanup();
        if (onScan) onScan(decodedText);
      }
    },
    (errorMessage) => {}
  );

  function cleanup() {
    try {
      html5QrCode.stop().catch(() => {});
      html5QrCode.clear().catch(() => {});
    } catch {}
    if (modal.parentNode) modal.parentNode.removeChild(modal);
    if (onClose) onClose();
  }

  // Allow closing with Escape key
  function escListener(e) {
    if (e.key === 'Escape') cleanup();
  }
  window.addEventListener('keydown', escListener);
  // Remove listener on cleanup
  const origCleanup = cleanup;
  cleanup = function() {
    window.removeEventListener('keydown', escListener);
    origCleanup();
  };
} 