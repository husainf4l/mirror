import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Suppress ResizeObserver errors
const suppressResizeObserverErrors = () => {
  const resizeObserverErrDiv = document.getElementById('webpack-dev-server-client-overlay-div');
  if (resizeObserverErrDiv) {
    resizeObserverErrDiv.style.display = 'none';
  }
  
  // Suppress the actual errors
  window.addEventListener('error', (e) => {
    if (e.message && (
      e.message.includes('ResizeObserver loop limit exceeded') ||
      e.message.includes('ResizeObserver loop completed with undelivered notifications')
    )) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
  });
  
  // Also handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (e) => {
    if (e.reason && e.reason.message && (
      e.reason.message.includes('ResizeObserver loop limit exceeded') ||
      e.reason.message.includes('ResizeObserver loop completed with undelivered notifications')
    )) {
      e.preventDefault();
      return false;
    }
  });
};

// Run the suppression immediately
suppressResizeObserverErrors();

// Also run it after a short delay to catch any delayed errors
setTimeout(suppressResizeObserverErrors, 1000);

import ErrorBoundary from './ErrorBoundary';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
