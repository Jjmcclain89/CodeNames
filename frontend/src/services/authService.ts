export interface LoginResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    username: string;
  };
  error?: string;
}

class AuthService {
  // Use empty string for relative URLs - Vite proxy will handle routing
  private readonly API_URL = import.meta.env.VITE_API_URL || '';

  async login(username: string): Promise<LoginResponse> {
    try {
      console.log('🔑 Attempting login to:', `${this.API_URL}/api/auth/login`);
      console.log('🔑 Username:', username);
      
      const response = await fetch(`${this.API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      });

      console.log('🔑 Login response status:', response.status);
      
      if (!response.ok) {
        console.error('🔑 Login response not OK:', response.statusText);
        return {
          success: false,
          error: `Server error: ${response.status} ${response.statusText}`
        };
      }

      const data = await response.json();
      console.log('🔑 Login response data:', data);
      
      if (data.success && data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        console.log('🔑 Login successful, token saved');
      }

      return data;
    } catch (error) {
      console.error('🔑 Login network error:', error);
      return {
        success: false,
        error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  async verifyToken(token: string): Promise<LoginResponse> {
    try {
      console.log('🔍 Verifying token...');
      
      const response = await fetch(`${this.API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      console.log('🔍 Token verification response status:', response.status);

      if (!response.ok) {
        console.error('🔍 Token verification failed:', response.statusText);
        return {
          success: false,
          error: `Token verification failed: ${response.status}`
        };
      }

      const result = await response.json();
      console.log('🔍 Token verification result:', result);
      
      return result;
    } catch (error) {
      console.error('🔍 Token verification network error:', error);
      return {
        success: false,
        error: `Network error during token verification: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  logout(): void {
    console.log('🚪 Logging out, clearing local storage');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getUser(): any {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
export default authService;
