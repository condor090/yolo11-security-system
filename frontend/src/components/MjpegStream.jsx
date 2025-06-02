import React from 'react';

// Componente simple MJPEG como fallback
export default function MjpegStream({ cameraId, className = "" }) {
  return (
    <img 
      src={`http://localhost:8889/api/cameras/${cameraId}/stream.mjpeg`}
      alt="Camera Stream"
      className={`w-full h-full object-contain ${className}`}
    />
  );
}