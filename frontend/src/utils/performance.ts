// Performance monitoring utilities for development and production

import { getCLS, getFID, getFCP, getLCP, getTTFB, Metric } from 'web-vitals';
import { useState, useEffect } from 'react';

interface PerformanceMetrics {
  cls: number | null;
  fid: number | null;  
  fcp: number | null;
  lcp: number | null;
  ttfb: number | null;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    cls: null,
    fid: null,
    fcp: null, 
    lcp: null,
    ttfb: null
  };

  private callbacks: Array<(metrics: PerformanceMetrics) => void> = [];

  constructor() {
    this.initializeWebVitals();
  }

  private initializeWebVitals() {
    getCLS((metric: Metric) => {
      this.metrics.cls = metric.value;
      this.notifyCallbacks();
      this.logMetric('CLS', metric);
    });

    getFID((metric: Metric) => {
      this.metrics.fid = metric.value;
      this.notifyCallbacks();
      this.logMetric('FID', metric);
    });

    getFCP((metric: Metric) => {
      this.metrics.fcp = metric.value;
      this.notifyCallbacks();
      this.logMetric('FCP', metric);
    });

    getLCP((metric: Metric) => {
      this.metrics.lcp = metric.value;
      this.notifyCallbacks();
      this.logMetric('LCP', metric);
    });

    getTTFB((metric: Metric) => {
      this.metrics.ttfb = metric.value;
      this.notifyCallbacks();
      this.logMetric('TTFB', metric);
    });
  }

  private logMetric(name: string, metric: Metric) {
    const isGood = this.isMetricGood(name, metric.value);
    const color = isGood ? 'color: green' : 'color: red';
    
    console.log(
      `%c${name}: ${metric.value.toFixed(2)}ms ${isGood ? '✅' : '❌'}`,
      color
    );

    // Send to analytics in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToAnalytics(name, metric);
    }
  }

  private isMetricGood(name: string, value: number): boolean {
    const thresholds = {
      'CLS': 0.1,
      'FID': 100,
      'FCP': 1800,
      'LCP': 2500,
      'TTFB': 600
    };

    return value <= (thresholds[name as keyof typeof thresholds] || Infinity);
  }

  private sendToAnalytics(name: string, metric: Metric) {
    // Example: Send to Google Analytics, DataDog, etc.
    if (typeof (window as any).gtag !== 'undefined') {
      (window as any).gtag('event', name, {
        event_category: 'Web Vitals',
        value: Math.round(metric.value),
        non_interaction: true,
      });
    }
  }

  private notifyCallbacks() {
    this.callbacks.forEach(callback => callback(this.metrics));
  }

  public subscribe(callback: (metrics: PerformanceMetrics) => void) {
    this.callbacks.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.callbacks.indexOf(callback);
      if (index > -1) {
        this.callbacks.splice(index, 1);
      }
    };
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();



export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>(
    performanceMonitor.getMetrics()
  );

  useEffect(() => {
    const unsubscribe = performanceMonitor.subscribe(setMetrics);
    return unsubscribe;
  }, []);

  return metrics;
}

// Performance timing utilities
export class PerformanceTimer {
  private timings: Map<string, number> = new Map();

  start(label: string) {
    this.timings.set(label, performance.now());
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 Started: ${label}`);
    }
  }

  end(label: string): number {
    const startTime = this.timings.get(label);
    if (!startTime) {
      console.warn(`No start time found for: ${label}`);
      return 0;
    }

    const duration = performance.now() - startTime;
    this.timings.delete(label);

    if (process.env.NODE_ENV === 'development') {
      const color = duration > 16 ? 'color: red' : 'color: green';
      console.log(`%c⏱️ ${label}: ${duration.toFixed(2)}ms`, color);
    }

    return duration;
  }

  measure(label: string, fn: () => void): number;
  measure<T>(label: string, fn: () => T): T;
  measure<T>(label: string, fn: () => T): T {
    this.start(label);
    const result = fn();
    this.end(label);
    return result;
  }

  async measureAsync<T>(label: string, fn: () => Promise<T>): Promise<T> {
    this.start(label);
    try {
      const result = await fn();
      this.end(label);
      return result;
    } catch (error) {
      this.end(label);
      throw error;
    }
  }
}

// Global performance timer instance
export const performanceTimer = new PerformanceTimer();

// Memory monitoring utilities
export function getMemoryUsage(): {
  used: number;
  total: number;
  limit: number;
} | null {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    return {
      used: Math.round(memory.usedJSHeapSize / 1048576), // MB
      total: Math.round(memory.totalJSHeapSize / 1048576), // MB
      limit: Math.round(memory.jsHeapSizeLimit / 1048576) // MB
    };
  }
  return null;
}

// React hook for memory monitoring
export function useMemoryMonitor(interval: number = 5000) {
  const [memoryInfo, setMemoryInfo] = useState(getMemoryUsage());

  useEffect(() => {
    const updateMemoryInfo = () => {
      const info = getMemoryUsage();
      setMemoryInfo(info);
      
      if (info && process.env.NODE_ENV === 'development') {
        const percentage = (info.used / info.limit) * 100;
        if (percentage > 70) {
          console.warn(`🧠 Memory usage high: ${percentage.toFixed(1)}%`);
        }
      }
    };

    const intervalId = setInterval(updateMemoryInfo, interval);
    updateMemoryInfo(); // Initial check

    return () => clearInterval(intervalId);
  }, [interval]);

  return memoryInfo;
}

// Bundle size tracking (development only)
export function trackBundleSize() {
  if (process.env.NODE_ENV !== 'development') return;

  const scripts = document.querySelectorAll('script[src*="static/js"]');
  const stylesheets = document.querySelectorAll('link[href*="static/css"]');

  let totalSize = 0;

  const checkResourceSize = async (url: string, type: string) => {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      const size = response.headers.get('content-length');
      if (size) {
        const sizeKB = Math.round(parseInt(size) / 1024);
        totalSize += sizeKB;
        console.log(`📦 ${type}: ${sizeKB}KB - ${url.split('/').pop()}`);
      }
    } catch (error) {
      console.warn(`Failed to check size for ${url}:`, error);
    }
  };

  // Check script sizes
  scripts.forEach(script => {
    const scriptElement = script as HTMLScriptElement;
    if (scriptElement.src) {
      checkResourceSize(scriptElement.src, 'JS');
    }
  });

  // Check stylesheet sizes
  stylesheets.forEach(link => {
    const href = (link as HTMLLinkElement).href;
    if (href) {
      checkResourceSize(href, 'CSS');
    }
  });

  setTimeout(() => {
    console.log(`📦 Total bundle size: ~${totalSize}KB`);
  }, 1000);
}