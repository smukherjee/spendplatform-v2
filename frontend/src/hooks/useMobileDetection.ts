import { useState, useEffect } from 'react';

interface MobileDetection {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  screenSize: 'mobile' | 'tablet' | 'desktop';
  touchDevice: boolean;
  deviceInfo: {
    userAgent: string;
    platform: string;
    vendor: string;
  };
}

export const useMobileDetection = (): MobileDetection => {
  const [detection, setDetection] = useState<MobileDetection>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    screenSize: 'desktop',
    touchDevice: false,
    deviceInfo: {
      userAgent: '',
      platform: '',
      vendor: ''
    }
  });

  const detectDevice = (): MobileDetection => {
    const userAgent = navigator.userAgent.toLowerCase();
    const platform = navigator.platform.toLowerCase();
    const vendor = navigator.vendor.toLowerCase();

    // Mobile device patterns
    const mobilePatterns = [
      /android.*mobile/,
      /iphone/,
      /ipod/,
      /blackberry/,
      /windows phone/,
      /mobile/
    ];

    // Tablet device patterns
    const tabletPatterns = [
      /ipad/,
      /android(?!.*mobile)/,
      /tablet/,
      /kindle/,
      /silk/,
      /playbook/
    ];

    // Check if it's a mobile device
    const isMobileDevice = mobilePatterns.some(pattern => pattern.test(userAgent));
    
    // Check if it's a tablet device
    const isTabletDevice = tabletPatterns.some(pattern => pattern.test(userAgent));
    
    // Check touch capability
    const isTouchDevice = 'ontouchstart' in window || 
                         navigator.maxTouchPoints > 0 || 
                         (window as any).DocumentTouch && document instanceof (window as any).DocumentTouch;

    // Screen size detection
    const screenWidth = window.innerWidth;
    const isSmallScreen = screenWidth < 768;
    const isMediumScreen = screenWidth >= 768 && screenWidth < 1024;
    const isLargeScreen = screenWidth >= 1024;

    // Combined logic for final determination
    let finalIsMobile = false;
    let finalIsTablet = false;
    let finalIsDesktop = false;
    let screenSize: 'mobile' | 'tablet' | 'desktop' = 'desktop';

    if (isMobileDevice || (isTouchDevice && isSmallScreen)) {
      finalIsMobile = true;
      screenSize = 'mobile';
    } else if (isTabletDevice || (isTouchDevice && isMediumScreen)) {
      finalIsTablet = true;
      screenSize = 'tablet';
    } else {
      finalIsDesktop = true;
      screenSize = 'desktop';
    }

    return {
      isMobile: finalIsMobile,
      isTablet: finalIsTablet,
      isDesktop: finalIsDesktop,
      screenSize,
      touchDevice: isTouchDevice,
      deviceInfo: {
        userAgent,
        platform,
        vendor
      }
    };
  };

  useEffect(() => {
    const updateDetection = () => {
      setDetection(detectDevice());
    };

    // Initial detection
    updateDetection();

    // Event listeners
    const handleResize = () => {
      updateDetection();
    };

    const handleOrientationChange = () => {
      // Small delay to account for orientation change completion
      setTimeout(updateDetection, 150);
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleOrientationChange);

    // Media query listeners for more precise breakpoint detection
    const mobileMediaQuery = window.matchMedia('(max-width: 767px)');
    const tabletMediaQuery = window.matchMedia('(min-width: 768px) and (max-width: 1023px)');
    
    const handleMobileChange = () => updateDetection();
    const handleTabletChange = () => updateDetection();

    if (mobileMediaQuery.addEventListener) {
      mobileMediaQuery.addEventListener('change', handleMobileChange);
      tabletMediaQuery.addEventListener('change', handleTabletChange);
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleOrientationChange);
      
      if (mobileMediaQuery.removeEventListener) {
        mobileMediaQuery.removeEventListener('change', handleMobileChange);
        tabletMediaQuery.removeEventListener('change', handleTabletChange);
      }
    };
  }, []);

  return detection;
};

// Utility functions for quick checks
export const isMobileDevice = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

export const isTouchDevice = (): boolean => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
};

export const getScreenSize = (): 'mobile' | 'tablet' | 'desktop' => {
  const width = window.innerWidth;
  if (width < 768) return 'mobile';
  if (width < 1024) return 'tablet';
  return 'desktop';
};

// Device-specific checks
export const isIOS = (): boolean => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent);
};

export const isAndroid = (): boolean => {
  return /Android/.test(navigator.userAgent);
};

export const isSafari = (): boolean => {
  return /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
};

export const isChrome = (): boolean => {
  return /Chrome/.test(navigator.userAgent);
};

export default useMobileDetection;