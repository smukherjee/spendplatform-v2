import { api } from './api';
import { useState, useEffect, useMemo } from 'react';

interface PermissionCheckResponse {
  screen_route: string;
  has_access: boolean;
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
        return cached.has_access;
      }

      // Fetch from API
      const response = await api.get(`/screen-permissions/check?screen_route=${encodeURIComponent(screenRoute)}`);
      const permissionData: PermissionCheckResponse = response.data;
      
      // Cache the result
      this.setCachedPermission(screenRoute, permissionData);
      
      return permissionData.has_access;
    } catch (error) {
      console.error(`Error checking permission for ${screenRoute}:`, error);
      // On error, deny access by default
      return false;
    }
  }

  async checkMultiplePermissions(screenRoutes: string[]): Promise<Map<string, boolean>> {
    const results = new Map<string, boolean>();
    
    // Check all permissions in parallel
    const promises = screenRoutes.map(async (route) => {
      const hasAccess = await this.checkScreenPermission(route);
      return { route, hasAccess };
    });
    
    const permissionResults = await Promise.all(promises);
    
    permissionResults.forEach(({ route, hasAccess }) => {
      results.set(route, hasAccess);
    });
    
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

// React hook for multiple permissions
export function useMultiplePermissions(screenRoutes: string[], userKey?: string) {
  const [permissions, setPermissions] = useState<Map<string, boolean>>(new Map());
  const [loading, setLoading] = useState(true);
  
  // Create stable reference for screenRoutes to prevent infinite re-renders
  const screenRoutesKey = useMemo(() => screenRoutes.join(','), [screenRoutes.join(',')]);

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
  }, [screenRoutesKey, userKey]);

  return { permissions, loading };
}