import React, { useRef, useEffect, useState } from 'react';
import { readJWT } from '../utils';

// Note: In a real React app, you'd use a package like 'qrcode.react'
// This implementation assumes 'QRCode' is available globally or via a library.
declare const QRCode: any;

interface QRPageProps {
  user: any;
}

export const QRPage: React.FC<QRPageProps> = ({ user }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [done, setDone] = useState(false);
  const tok = localStorage.getItem('mc_token') || '';
  const decoded = readJWT(tok);
  // QR points to login with flag ?qr=1
  const qrUrl = window.location.origin + '/?qr=1';

  useEffect(() => {
    if (ref.current && !done && typeof QRCode !== 'undefined') {
      ref.current.innerHTML = '';
      new QRCode(ref.current, {
        text: qrUrl,
        width: 220,
        height: 220,
        colorDark: '#0a5940',
        colorLight: '#ffffff',
        correctLevel: 1 // QRCode.CorrectLevel.M
      });
      setDone(true);
    }
  }, [qrUrl, done]);

  return (
    <main>
      <div style={{ maxWidth: 500, margin: '0 auto' }}>
        <div className="sec-hd" style={{ textAlign: 'center' }}>
          <h2>Tu código QR de acceso</h2>
          <p>Preséntalo en recepción o escanéalo para iniciar sesión automáticamente</p>
        </div>
        <div className="card">
          <div className="qr-wrap">
            <div className="alert alert-info" style={{ width: '100%', textAlign: 'center', justifyContent: 'center' }}>
              📱 Escanear abre la pantalla de login en <strong>{qrUrl}</strong>
            </div>
            <div id="qrdiv" ref={ref} />
            <div className="qr-chip">
              <div className="qr-chip-name">{user.name}</div>
              <div className="qr-chip-sub">CURP: {user.curp}</div>
              {decoded && (
                <div style={{ fontSize: 11.5, color: 'var(--green2)', marginTop: 3 }}>
                  Token válido hasta: {new Date(decoded.exp).toLocaleDateString('es-MX')}
                </div>
              )}
            </div>
            <div className="divider" style={{ width: '100%' }} />
            <div style={{ fontSize: 11, color: 'var(--ink3)', fontFamily: 'monospace', wordBreak: 'break-all', background: 'var(--page)', padding: '10px 12px', borderRadius: 8, width: '100%' }}>
              JWT: {tok.substring(0, 70)}…
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};
