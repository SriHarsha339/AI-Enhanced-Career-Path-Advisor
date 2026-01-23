import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ============= Types =============

interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

interface StoredUser extends User {
  password: string; // Hashed for demo purposes
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (updates: Partial<User>) => void;
}

// ============= Storage Keys =============

const USERS_KEY = 'career_recommender_users';
const CURRENT_USER_KEY = 'career_recommender_current_user';

// ============= Context =============

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============= Helper Functions =============

// Simple hash function for demo (in production, use bcrypt on server)
function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(36);
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function getStoredUsers(): StoredUser[] {
  try {
    const data = localStorage.getItem(USERS_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

function saveUsers(users: StoredUser[]): void {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function getCurrentUser(): User | null {
  try {
    const data = localStorage.getItem(CURRENT_USER_KEY);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

function setCurrentUser(user: User | null): void {
  if (user) {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(CURRENT_USER_KEY);
  }
}

// ============= Provider Component =============

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = getCurrentUser();
    if (storedUser) {
      // Verify user still exists in users list
      const users = getStoredUsers();
      const exists = users.find(u => u.id === storedUser.id);
      if (exists) {
        setUser(storedUser);
      } else {
        setCurrentUser(null);
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    // Simulate async operation
    await new Promise(resolve => setTimeout(resolve, 300));

    const users = getStoredUsers();
    const hashedPassword = simpleHash(password);
    
    const matchedUser = users.find(
      u => u.email.toLowerCase() === email.toLowerCase() && u.password === hashedPassword
    );

    if (!matchedUser) {
      throw new Error('Invalid email or password');
    }

    // Create user object without password
    const userWithoutPassword: User = {
      id: matchedUser.id,
      name: matchedUser.name,
      email: matchedUser.email,
      createdAt: matchedUser.createdAt,
    };

    setCurrentUser(userWithoutPassword);
    setUser(userWithoutPassword);
  };

  const register = async (name: string, email: string, password: string): Promise<void> => {
    // Simulate async operation
    await new Promise(resolve => setTimeout(resolve, 300));

    const users = getStoredUsers();
    
    // Check if email already exists
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
      throw new Error('An account with this email already exists');
    }

    // Create new user
    const newUser: StoredUser = {
      id: generateId(),
      name,
      email: email.toLowerCase(),
      password: simpleHash(password),
      createdAt: new Date().toISOString(),
    };

    // Save to storage
    saveUsers([...users, newUser]);

    // Create user object without password
    const userWithoutPassword: User = {
      id: newUser.id,
      name: newUser.name,
      email: newUser.email,
      createdAt: newUser.createdAt,
    };

    setCurrentUser(userWithoutPassword);
    setUser(userWithoutPassword);
  };

  const logout = (): void => {
    setCurrentUser(null);
    setUser(null);
  };

  const updateProfile = (updates: Partial<User>): void => {
    if (!user) return;

    const updatedUser = { ...user, ...updates };
    
    // Update in users list
    const users = getStoredUsers();
    const userIndex = users.findIndex(u => u.id === user.id);
    if (userIndex >= 0) {
      users[userIndex] = { ...users[userIndex], ...updates };
      saveUsers(users);
    }

    setCurrentUser(updatedUser);
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ============= Hook =============

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
