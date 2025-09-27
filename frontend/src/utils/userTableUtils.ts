// Performance utilities for User table operations

// User interface (should match the one in Users.tsx)
interface User {
  id: string | number;
  name: string;
  username: string;
  email: string;
  created_at?: string;
  updated_at?: string;
}

// Memoized search function
export const createSearchFunction = () => {
  const cache = new Map<string, User[]>();
  
  return (users: User[], searchTerm: string): User[] => {
    if (!searchTerm.trim()) return users;
    
    const cacheKey = `${users.length}-${searchTerm.toLowerCase()}`;
    if (cache.has(cacheKey)) {
      return cache.get(cacheKey)!;
    }
    
    const filtered = users.filter(user => 
      user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // Keep cache size reasonable
    if (cache.size > 50) {
      const firstKey = cache.keys().next().value;
      if (firstKey) {
        cache.delete(firstKey);
      }
    }
    
    cache.set(cacheKey, filtered);
    return filtered;
  };
};

// Debounced function factory
export const createDebouncer = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Batch operation utility
export const batchOperation = async <T, R>(
  items: T[],
  operation: (item: T) => Promise<R>,
  batchSize: number = 5,
  onProgress?: (completed: number, total: number) => void
): Promise<R[]> => {
  const results: R[] = [];
  
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(operation));
    results.push(...batchResults);
    
    if (onProgress) {
      onProgress(Math.min(i + batchSize, items.length), items.length);
    }
  }
  
  return results;
};

// Data validation utilities
export const validateUser = (user: Partial<User>): string[] => {
  const errors: string[] = [];
  
  if (!user.name?.trim()) {
    errors.push('Name is required');
  }
  
  if (!user.email?.trim()) {
    errors.push('Email is required');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.email)) {
    errors.push('Invalid email format');
  }
  
  if (!user.username?.trim()) {
    errors.push('Username is required');
  } else if (user.username.length < 3) {
    errors.push('Username must be at least 3 characters');
  }
  
  return errors;
};

// Sort utility with performance optimization
export const createSortFunction = () => {
  const cache = new Map<string, User[]>();
  
  return (users: User[], field: keyof User, order: 'asc' | 'desc'): User[] => {
    const cacheKey = `${users.length}-${String(field)}-${order}`;
    if (cache.has(cacheKey)) {
      return cache.get(cacheKey)!;
    }
    
    const sorted = [...users].sort((a, b) => {
      const aVal = a[field];
      const bVal = b[field];
      
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return order === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      
      if (aVal < bVal) return order === 'asc' ? -1 : 1;
      if (aVal > bVal) return order === 'asc' ? 1 : -1;
      return 0;
    });
    
    // Keep cache size reasonable
    if (cache.size > 20) {
      const firstKey = cache.keys().next().value;
      if (firstKey) {
        cache.delete(firstKey);
      }
    }
    
    cache.set(cacheKey, sorted);
    return sorted;
  };
};

// Memory monitoring utility
export const getMemoryUsage = (): string => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    return `Used: ${(memory.usedJSHeapSize / 1048576).toFixed(2)}MB / Total: ${(memory.totalJSHeapSize / 1048576).toFixed(2)}MB`;
  }
  return 'Memory monitoring not available';
};

// Performance timing utility
export const createPerformanceTracker = () => {
  const timings = new Map<string, number>();
  
  return {
    start: (label: string) => {
      timings.set(label, performance.now());
    },
    end: (label: string): number => {
      const startTime = timings.get(label);
      if (!startTime) return 0;
      
      const duration = performance.now() - startTime;
      timings.delete(label);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`⏱️ ${label}: ${duration.toFixed(2)}ms`);
      }
      
      return duration;
    },
    getAll: () => new Map(timings)
  };
};