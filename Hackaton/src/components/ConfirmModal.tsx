import React from 'react';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({ isOpen, onClose, onConfirm, title, message }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-bg" onClick={(ev) => ev.target === ev.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: '400px', textAlign: 'center' }}>
        <div style={{ 
          width: '64px', height: '64px', background: 'rgba(220, 38, 38, 0.05)', 
          color: '#DC2626', borderRadius: '50%', display: 'flex', 
          alignItems: 'center', justifyContent: 'center', fontSize: '28px',
          margin: '0 auto 24px'
        }}>
          ⚠️
        </div>
        <h2 style={{ fontSize: '24px', marginBottom: '12px', letterSpacing: '-0.02em' }}>{title}</h2>
        <p className="text-muted" style={{ fontSize: '15px', marginBottom: '32px' }}>
          {message}
        </p>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            className="btn btn-ghost" 
            style={{ flex: 1 }} 
            onClick={onClose}
          >
            Cancelar
          </button>
          <button 
            className="btn btn-primary" 
            style={{ flex: 1, background: '#DC2626' }} 
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
};
