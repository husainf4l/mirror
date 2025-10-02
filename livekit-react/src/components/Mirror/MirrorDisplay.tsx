import React from 'react';
import './MirrorDisplay.css';

interface MirrorDisplayProps {
  mirrorText: string;
}

const MirrorDisplay: React.FC<MirrorDisplayProps> = ({ mirrorText }) => {
  return (
    <>
      <div className="stars">
        {/* Original 8 stars */}
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        <i className="star fas fa-star primary-star"></i>
        
        {/* Additional stars for vertical displays */}
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        <i className="star fas fa-star vertical-star"></i>
        
        {/* Extra decorative stars */}
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        <i className="star fas fa-star extra-star"></i>
        
        {/* Elegant corner stars */}
        <i className="star fas fa-star corner-star"></i>
        <i className="star fas fa-star corner-star"></i>
        <i className="star fas fa-star corner-star"></i>
        <i className="star fas fa-star corner-star"></i>
        
        {/* Subtle background stars */}
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
        <i className="star fas fa-star bg-star"></i>
      </div>

      <div className="mirror-container">
        <div 
          className="mirror-text" 
          dangerouslySetInnerHTML={{ __html: mirrorText }}
        />
      </div>
    </>
  );
};

export default MirrorDisplay;
