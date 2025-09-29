import { api } from './api';
import { useState, useEffect, useMemo } from 'react';

interface PermissionCheckResponse {
  screen_route: string;
  has_access?: boolean; // legacy, not used
  has_permission: boolean; // correct property from backend
  source: string;
  message?: string;
}

class PermissionManager {
  private static instance: PermissionManager;
  private permissionCache: Map<string, PermissionCheckResponse> = new Map();
  private cacheExpiry: Map<string, number> = new Map();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  static getInstance(): PermissionManager {
    if (!PermissionManager.instance) {
      PermissionManager.instance = new PermissionManager();
    }
    return PermissionManager.instance;
  }

  async checkScreenPermission(screenRoute: string): Promise<boolean> {
    try {
      // Check cache first
      const cached = this.getCachedPermission(screenRoute);
      if (cached !== null) {
        // Use has_permission from backend response
        return cached.has_permission;
      }

  // Fetch from API
  const response = await api.get(`/screen-permissions/check?screen_route=${encodeURIComponent(screenRoute)}`);
  const permissionData: PermissionCheckResponse = response.data;
  // Debug log: print permission API response
  console.log(`🛡️ Permission API response for ${screenRoute}:`, permissionData);
  // Cache the result
  this.setCachedPermission(screenRoute, permissionData);
  // Use has_permission from backend response
  return permissionData.has_permission;
    } catch (error) {
      console.error(`Error checking permission for ${screenRoute}:`, error);
      // On error, deny access by default
      return false;
    }
  }

  async checkMultiplePermissions(screenRoutes: string[]): Promise<Map<string, boolean>> {
    const results = new Map<string, boolean>();
    
    // PERFORMANCE OPTIMIZATION: Use Promise.allSettled to handle parallel requests
    // even if some fail, and limit concurrency to avoid overwhelming the server
    const BATCH_SIZE = 5;
    const batches: string[][] = [];
    
    for (let i = 0; i < screenRoutes.length; i += BATCH_SIZE) {
      batches.push(screenRoutes.slice(i, i + BATCH_SIZE));
    }
    
    for (const batch of batches) {
      const promises = batch.map(async (route) => {
        try {
          const hasAccess = await this.checkScreenPermission(route);
          return { route, hasAccess, success: true };
        } catch (error) {
          console.error(`Failed to check permission for ${route}:`, error);
          return { route, hasAccess: false, success: false };
        }
      });
      
      const batchResults = await Promise.allSettled(promises);
      
      batchResults.forEach((result) => {
        if (result.status === 'fulfilled') {
          results.set(result.value.route, result.value.hasAccess);
        } else {
          // Handle rejected promises - default to no access
          console.error('Permission check failed:', result.reason);
        }
      });
    }
    
    return results;
  }

  private getCachedPermission(screenRoute: string): PermissionCheckResponse | null {
    const now = Date.now();
    const expiry = this.cacheExpiry.get(screenRoute);
    
    if (expiry && now < expiry) {
      return this.permissionCache.get(screenRoute) || null;
    }
    
    // Clean up expired cache
    this.permissionCache.delete(screenRoute);
    this.cacheExpiry.delete(screenRoute);
    
    return null;
  }

  private setCachedPermission(screenRoute: string, permission: PermissionCheckResponse): void {
    this.permissionCache.set(screenRoute, permission);
    this.cacheExpiry.set(screenRoute, Date.now() + this.CACHE_DURATION);
  }

  clearCache(): void {
    const cacheSize = this.permissionCache.size;
    this.permissionCache.clear();
    this.cacheExpiry.clear();
    console.log(`PermissionManager: Cleared ${cacheSize} cached permissions`);
  }

  // Clear cache for specific route (useful after permission updates)
  clearRouteCache(screenRoute: string): void {
    this.permissionCache.delete(screenRoute);
    this.cacheExpiry.delete(screenRoute);
  }
}

// Export singleton instance
export const permissionManager = PermissionManager.getInstance();

// External function to clear all caches (useful for logout)
export function clearAllPermissionCaches(): void {
  permissionManager.clearCache();
  console.log('Permission caches cleared');
}

// Function to invalidate cache after permission updates
export function invalidatePermissionCache(): void {
  permissionManager.clearCache();
  console.log('Permission cache invalidated after permission update');
}

// Function to invalidate cache for specific screens (useful for targeted updates)
export function invalidateScreenCache(screenRoutes: string[]): void {
  screenRoutes.forEach(route => {
    permissionManager.clearRouteCache(route);
  });
  console.log('Permission cache invalidated for screens:', screenRoutes);
}

// Utility functions for React components
export async function hasScreenAccess(screenRoute: string): Promise<boolean> {
  return await permissionManager.checkScreenPermission(screenRoute);
}

export async function filterAllowedRoutes(routes: string[]): Promise<string[]> {
  const permissions = await permissionManager.checkMultiplePermissions(routes);
  return routes.filter(route => permissions.get(route) === true);
}

// React hook for permission checking

export function usePermission(screenRoute: string, userKey?: string) {
  const [hasAccess, setHasAccess] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const checkPermission = async () => {
      try {
        setLoading(true);
        const access = await permissionManager.checkScreenPermission(screenRoute);
        
        if (isMounted) {
          setHasAccess(access);
        }
      } catch (error) {
        console.error('Permission check failed:', error);
        if (isMounted) {
          setHasAccess(false);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    checkPermission();

    return () => {
      isMounted = false;
    };
  }, [screenRoute, userKey]);

  return { hasAccess, loading };
}

// PERFORMANCE OPTIMIZED: React hook for multiple permissions
export function useMultiplePermissions(screenRoutes: string[], userKey?: string) {
  const [permissions, setPermissions] = useState<Map<string, boolean>>(new Map());
  const [loading, setLoading] = useState(true);
  
  // PERFORMANCE FIX: Proper memoization to prevent infinite re-renders
  const screenRoutesKey = useMemo(() => screenRoutes.join(','), [screenRoutes]);

  useEffect(() => {
    let isMounted = true;

    const checkPermissions = async () => {
      try {
        setLoading(true);
        const perms = await permissionManager.checkMultiplePermissions(screenRoutes);
        
        if (isMounted) {
          setPermissions(perms);
        }
      } catch (error) {
        console.error('Multiple permission check failed:', error);
        if (isMounted) {
          // Set all to false on error
          const deniedPerms = new Map<string, boolean>();
          screenRoutes.forEach(route => deniedPerms.set(route, false));
          setPermissions(deniedPerms);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (screenRoutes.length > 0) {
      checkPermissions();
    } else {
      setLoading(false);
    }

    return () => {
      isMounted = false;
    };
  }, [screenRoutesKey, userKey, screenRoutes]); // Include screenRoutes in dependencies

  return { permissions, loading };
}