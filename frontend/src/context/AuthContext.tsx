import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';

export interface AuthUser {
  id: string;
  company_id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  designation?: string;
  roles: string[];
  permissions: string[];
  is_active: boolean;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('opspilot_access_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const storedToken = localStorage.getItem('opspilot_access_token');
      if (storedToken) {
        try {
          const profile = await apiClient.get<AuthUser>('/auth/me');
          setUser(profile);
          setToken(storedToken);
        } catch {
          // Token expired or invalid
          localStorage.removeItem('opspilot_access_token');
          localStorage.removeItem('opspilot_refresh_token');
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    }
    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    interface LoginResult {
      access_token: string;
      refresh_token: string;
      user: AuthUser;
    }
    const data = await apiClient.post<LoginResult>('/auth/login', { email, password });
    localStorage.setItem('opspilot_access_token', data.access_token);
    localStorage.setItem('opspilot_refresh_token', data.refresh_token);
    setToken(data.access_token);
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem('opspilot_access_token');
    localStorage.removeItem('opspilot_refresh_token');
    setUser(null);
    setToken(null);
  };

  const hasRole = (role: string) => {
    if (!user) return false;
    if (user.roles.includes('COMPANY_ADMIN')) return true;
    return user.roles.includes(role);
  };

  const hasPermission = (permission: string) => {
    if (!user) return false;
    if (user.roles.includes('COMPANY_ADMIN')) return true;
    return user.permissions.includes(permission);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasRole,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
