import React, { createContext, useContext, useState, useEffect } from 'react';

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

const AuthContext = createContext(null as any);

export function AuthProvider({ children }: { children: any }) {
  const [user, setUser] = useState(null as any);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = (): boolean => {
    try {
      const token = localStorage.getItem('access_token');
      const userData = localStorage.getItem('user_data');
      
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
  };

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user_data', JSON.stringify(userData));
    console.log('User logged in:', userData);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user_data');
    console.log('User logged out');
  };

  const contextValue: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    checkAuthStatus
  };

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