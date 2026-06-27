
export interface User {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  type_apprenant?: 'visuel' | 'auditif' | 'lecture';
  niveau_global?: 'débutant' | 'intermédiaire' | 'avancé';
  role_name?: string;
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
}

export interface ErrorResponse {
  detail?: string;
}

export interface ApiError {
  response?: {
    data?: ErrorResponse;
    status?: number;
  };
  message?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}