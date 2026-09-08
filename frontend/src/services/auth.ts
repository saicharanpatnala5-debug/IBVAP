import { UserSession } from '../types';

const AUTH_KEY = 'ibvap_tactical_session';

export const TacticalAuth = {
  getSession(): UserSession | null {
    try {
      const data = localStorage.getItem(AUTH_KEY);
      if (!data) return null;
      return JSON.parse(data);
    } catch {
      return null;
    }
  },

  setSession(session: UserSession): void {
    localStorage.setItem(AUTH_KEY, JSON.stringify(session));
  },

  clearSession(): void {
    localStorage.removeItem(AUTH_KEY);
  },

  isAuthenticated(): boolean {
    return !!this.getSession();
  },

  getDefaultPreset(role: string): UserSession {
    switch (role) {
      case 'admin':
        return {
          user_id: 'USR-ADMIN',
          username: 'admin',
          email: 'admin@ibvap.gov.in',
          full_name: 'Commandant R. K. Verma',
          role: 'admin',
          token: 'jwt_tactical_token_admin_2026'
        };
      case 'supervisor':
        return {
          user_id: 'USR-SUPERVISOR',
          username: 'supervisor',
          email: 'supervisor@ibvap.gov.in',
          full_name: 'Inspector M. S. Gill',
          role: 'supervisor',
          token: 'jwt_tactical_token_supervisor_2026'
        };
      case 'operator':
      default:
        return {
          user_id: 'USR-OPERATOR',
          username: 'operator_sharma',
          email: 'sharma@ibvap.gov.in',
          full_name: 'Head Constable A. Sharma',
          role: 'cctv_operator',
          token: 'jwt_tactical_token_operator_2026'
        };
    }
  }
};
