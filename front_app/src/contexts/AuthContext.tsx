
/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';


export interface User {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  type_apprenant?: 'visuel' | 'auditif' | 'lecture';
  niveau_global?: 'débutant' | 'intermédiaire' | 'avancé';
  role_name?: string;
  role_id?: number;
  est_actif?: boolean;
  date_inscription?: string;
  derniere_connexion?: string;
}

export interface RegisterData {
  email: string;
  password: string;
  nom: string;
  prenom: string;
  type_apprenant?: 'visuel' | 'auditif' | 'lecture';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id?: number;
  email?: string;
  role?: string;
  role_id?: number;
  expires_in?: number;
}

export interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
    status?: number;
  };
  message?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
  loading: boolean;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);

  const logout = useCallback((): void => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    toast.success('Déconnexion réussie');
  }, []);

  const fetchUser = useCallback(async (): Promise<void> => {
    console.log('🔍 fetchUser called, token:', token);
    
    if (!token) {
      console.log('❌ No token, setting loading false');
      setLoading(false);
      return;
    }
    
    try {
      console.log('📡 Fetching user data...');
      const response = await api.get<User>('/users/me');
      console.log('✅ User data received:', response.data);
      setUser(response.data);
    } catch (error) {
      console.error('❌ Failed to fetch user:', error);
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  
  const refreshUser = useCallback(async (): Promise<void> => {
    if (!token) {
      console.log('No token, cannot refresh user');
      return;
    }
    
    try {
      console.log('🔄 Refreshing user data...');
      const response = await api.get<User>('/users/me');
      console.log('✅ User data refreshed:', response.data);
      setUser(response.data);
      
    } catch (error) {
      console.error('❌ Failed to refresh user:', error);
      
    }
  }, [token]);

  useEffect(() => {
    console.log('🔍 useEffect - token:', token);
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token, fetchUser]);

  const login = async (username: string, password: string): Promise<void> => {
    console.log('🔐 Login attempt for:', username);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await api.post<LoginResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      const { access_token } = response.data;
      console.log('✅ Login success, token received:', access_token);
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      await fetchUser();
      
      toast.success('Connexion réussie !');
      console.log('🎉 Login complete, user set');
    } catch (error) {
      const apiError = error as ApiError;
      const errorMessage = apiError.response?.data?.detail || apiError.message || 'Erreur de connexion';
      console.error('❌ Login error:', errorMessage);
      toast.error(errorMessage);
      throw error;
    }
  };

  const register = async (userData: RegisterData): Promise<void> => {
    try {
      const response = await api.post('/auth/public-register', {
        email: userData.email,
        mot_de_passe: userData.password,
        nom: userData.nom,
        prenom: userData.prenom,
        type_apprenant: userData.type_apprenant
      });
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        setToken(response.data.access_token);
        await fetchUser();
        toast.success('Inscription et connexion réussies !');
      } else {
        toast.success('Inscription réussie ! Veuillez vous connecter.');
      }
    } catch (error) {
      const apiError = error as ApiError;
      const errorMessage = apiError.response?.data?.detail || apiError.message || "Erreur d'inscription";
      toast.error(errorMessage);
      throw error;
    }
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        token, 
        login, 
        register, 
        logout, 
        refreshUser,
        isAuthenticated: !!token && !!user,
        loading 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};