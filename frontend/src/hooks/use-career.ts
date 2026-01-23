import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";

const HISTORY_KEY = 'career_recommender_history';

export interface HistoryItem {
  id: number;
  createdAt: string;
  educationLevel: string;
  interests: string[];
  topCareer: string;
  recommendationResult: string;
  structuredData: any;
}

// Get history from localStorage
function getStoredHistory(): HistoryItem[] {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

// Save history to localStorage
function saveHistory(history: HistoryItem[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

// Add a new recommendation to history
export function addToHistory(item: Omit<HistoryItem, 'id' | 'createdAt'>): HistoryItem {
  const history = getStoredHistory();
  const newItem: HistoryItem = {
    ...item,
    id: Date.now(),
    createdAt: new Date().toISOString(),
  };
  history.unshift(newItem);
  saveHistory(history.slice(0, 50)); // Keep last 50
  return newItem;
}

// Delete a history item
export function deleteFromHistory(id: number) {
  const history = getStoredHistory();
  saveHistory(history.filter(item => item.id !== id));
}

// Clear all history
export function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}

export function useCareerRecommendations() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: any) => {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) throw new Error('Failed to get recommendation');
      const result = await response.json();
      
      // Save to localStorage history
      addToHistory({
        educationLevel: data.educationLevel,
        interests: data.interests || [],
        topCareer: result.structuredData?.featured?.title || 'Career Analysis',
        recommendationResult: result.recommendation,
        structuredData: result.structuredData,
      });
      
      // Save to sessionStorage for Result page
      sessionStorage.setItem('lastRecommendation', JSON.stringify(result));
      
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['career-history'] });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });
}

export function useCareerHistory() {
  return useQuery({
    queryKey: ['career-history'],
    queryFn: () => getStoredHistory(),
  });
}
