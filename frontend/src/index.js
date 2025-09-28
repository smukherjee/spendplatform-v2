import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <App />
);

reportWebVitals();

// Add performance monitoring for development
if (process.env.NODE_ENV === 'development') {
  // Track bundle size and performance
  import('./utils/performance').then(({ trackBundleSize, performanceMonitor }) => {
    trackBundleSize();
    
    // Log performance metrics when they're available
    performanceMonitor.subscribe((metrics) => {
      console.log('📊 Performance Metrics:', metrics);
    });
  }).catch(err => {
    console.warn('Failed to load performance monitoring:', err);
  });
}
