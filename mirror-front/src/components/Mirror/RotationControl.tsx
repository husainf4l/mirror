'use client';

import React, { useEffect } from 'react';
import './RotationControl.css';

interface RotationControlProps {
  rotation: number;
  onRotate: () => void;
}

const RotationControl: React.FC<RotationControlProps> = ({ rotation, onRotate }) => {
  const handleClick = () => {
    onRotate();
  };
  
  return (
    <button 
      className="rotation-btn" 
      onClick={handleClick}
      title={`Rotate Display (Current: ${rotation}°)`}
    >
      <i className="fas fa-star"></i>
    </button>
  );
};

export default RotationControl;