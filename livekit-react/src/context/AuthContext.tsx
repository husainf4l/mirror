import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const apiUrl = process.env.REACT_APP_API_URL || '';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if we have a valid auth cookie by making a request to a protected endpoint
        const response = await fetch(`${apiUrl}/api/mirror`, {
          credentials: 'include' // Include cookies
        });
        
        if (response.ok) {
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.log('Not authenticated');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (password: string): Promise<boolean> => {
    try {
      setLoading(true);
      
      // Create FormData for login
      const formData = new FormData();
      formData.append('password', password);
      
      const response = await fetch(`${apiUrl}/api/login`, {
        method: 'POST',
        body: formData,
        credentials: 'include' // Include cookies
      });
      
      if (response.ok) {
        setIsAuthenticated(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${apiUrl}/api/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
