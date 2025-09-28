import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import { clearAllPermissionCaches } from '../services/permissions';

interface User {
  username: string;
  role: string;
  client_id: number;
  user_id: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (userData: User) => void;
  logout: () => void;
  checkAuthStatus: () => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Memoize the checkAuthStatus function to prevent recreation
  const checkAuthStatus = useCallback((): boolean => {
    try {
      const token = sessionStorage.getItem('access_token');
      const userData = sessionStorage.getItem('user_data');
      
      if (token && userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsLoading(false);
        return true;
      } else {
        setUser(null);
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setUser(null);
      setIsLoading(false);
      return false;
    }
  }, []);

  // Memoize the login function to prevent recreation
  const login = useCallback((userData: User) => {
    // Clear any existing permission cache before setting new user
    clearAllPermissionCaches();
    
    setUser(userData);
    sessionStorage.setItem('user_data', JSON.stringify(userData));
    console.log('User logged in:', userData);
  }, []);

  // Memoize the logout function to prevent recreation
  const logout = useCallback(() => {
    setUser(null);
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('token_type');
    sessionStorage.removeItem('user_data');
    
    // Clear permission cache to ensure fresh permissions for next login
    clearAllPermissionCaches();
    
    console.log('User logged out and permission cache cleared');
  }, []);

  // Check auth status on app load
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // PERFORMANCE FIX: Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo<AuthContextType>(() => ({
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    checkAuthStatus
  }), [user, isLoading, login, logout, checkAuthStatus]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}