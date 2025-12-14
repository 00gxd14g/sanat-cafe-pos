import React, { useEffect } from 'react';
import { XCircle, CheckCircle, AlertTriangle } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  type: 'success' | 'error' | 'info';
  title: string;
  message: string;
  onClose: () => void;
  autoClose?: number;
}

const Modal: React.FC<ModalProps> = ({ isOpen, type, title, message, onClose, autoClose }) => {
  useEffect(() => {
    if (isOpen && autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, autoClose);
      return () => clearTimeout(timer);
    }
  }, [isOpen, autoClose, onClose]);

  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-12 h-12 text-green-500 mb-4 animate-bounce" />;
      case 'error':
        return <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />;
      default:
        return <XCircle className="w-12 h-12 text-blue-500 mb-4" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm transition-opacity">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-4 flex flex-col items-center text-center transform transition-all scale-100">
        {getIcon()}
        <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600">{message}</p>
        
        {!autoClose && (
          <button
            onClick={onClose}
            className="mt-6 px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Kapat
          </button>
        )}
      </div>
    </div>
  );
};

export default Modal;