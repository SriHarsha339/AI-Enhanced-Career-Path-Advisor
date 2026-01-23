import { useCareerHistory } from "@/hooks/use-career";
import { useAuth } from "@/contexts/AuthContext";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Calendar, BookOpen, ArrowRight, LogIn, Sparkles, Clock, FolderOpen, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { motion } from "framer-motion";

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] }
  }
};

export default function History() {
  const { data: history, isLoading } = useCareerHistory();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [, setLocation] = useLocation();

  const handleViewResult = (item: any) => {
    sessionStorage.setItem('lastRecommendation', JSON.stringify({
      recommendation: item.recommendationResult,
      queryId: item.id,
      structuredData: item.structuredData
    }));
    setLocation(`/result/${item.id}`);
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  if (authLoading || isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-[60vh]">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-4"
          >
            <div className="w-16 h-16 bg-[#1B4D3E]/10 rounded-2xl flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-[#1B4D3E]" />
            </div>
            <p className="text-gray-500">Loading your history...</p>
          </motion.div>
        </div>
      </Layout>
    );
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <Layout>
        <motion.div 
          className="max-w-md mx-auto text-center py-20 space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div 
            className="w-20 h-20 bg-[#1B4D3E]/10 rounded-3xl flex items-center justify-center mx-auto"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.2 }}
          >
            <LogIn className="w-10 h-10 text-[#1B4D3E]" />
          </motion.div>
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">Sign In to View History</h1>
            <p className="text-gray-500">
              Create an account or sign in to save your career recommendations and access them anytime.
            </p>
          </div>
          <div className="flex flex-col gap-3">
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button 
                onClick={() => setLocation("/login")} 
                className="gap-2 w-full bg-[#1B4D3E] hover:bg-[#163d32] text-white rounded-xl h-12 shadow-lg shadow-[#1B4D3E]/20"
              >
                <LogIn className="w-4 h-4" />
                Sign In
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button 
                variant="outline" 
                onClick={() => setLocation("/register")} 
                className="gap-2 w-full border-[#1B4D3E]/20 text-[#1B4D3E] hover:bg-[#1B4D3E]/5 rounded-xl h-12"
              >
                <Sparkles className="w-4 h-4" />
                Create Account
              </Button>
            </motion.div>
          </div>
          <p className="text-sm text-gray-400 pt-4">
            You can still use the app as a guest, but your history won't be saved.
          </p>
          <Button 
            variant="ghost" 
            onClick={() => setLocation("/discover")}
            className="text-gray-500 hover:text-gray-700"
          >
            Continue as Guest
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </motion.div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-white py-8 relative overflow-hidden">
        
        {/* Subtle Background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-1/2 h-1/3 bg-gradient-to-bl from-[#1B4D3E]/5 to-transparent" />
          <div className="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-[#C5E500]/5 to-transparent" />
        </div>

        <motion.div 
          className="max-w-6xl mx-auto px-4 space-y-8 relative z-10"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Header */}
          <motion.div variants={itemVariants} className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-gray-900">History</h1>
              <p className="text-gray-500">Your past career explorations.</p>
            </div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button 
                onClick={() => setLocation("/discover")} 
                className="gap-2 bg-[#1B4D3E] hover:bg-[#163d32] text-white rounded-xl shadow-lg shadow-[#1B4D3E]/20"
              >
                <Sparkles className="w-4 h-4" />
                Start New Analysis
              </Button>
            </motion.div>
          </motion.div>

          {/* Empty State */}
          {history?.length === 0 ? (
            <motion.div 
              variants={itemVariants}
              className="text-center py-20 bg-gray-50 rounded-3xl border border-gray-100"
            >
              <div className="w-16 h-16 bg-[#1B4D3E]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-[#1B4D3E]" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900">No history yet</h3>
              <p className="text-gray-500 mb-6">Start your first career analysis to see it here.</p>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button 
                  onClick={() => setLocation("/discover")}
                  className="bg-[#1B4D3E] hover:bg-[#163d32] text-white rounded-xl"
                >
                  Get Started
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </motion.div>
            </motion.div>
          ) : (
            /* History Grid */
            <motion.div 
              className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
              variants={containerVariants}
            >
              {history?.map((item) => (
                <motion.div
                  key={item.id}
                  variants={itemVariants}
                  whileHover={{ y: -4, transition: { duration: 0.2 } }}
                >
                  <Card className="overflow-hidden bg-white border border-gray-100 hover:border-[#1B4D3E]/30 hover:shadow-xl transition-all duration-300 rounded-2xl group">
                    <CardHeader className="bg-gradient-to-br from-gray-50 to-white pb-4">
                      <div className="flex justify-between items-start mb-3">
                        <Badge className="bg-[#1B4D3E]/10 text-[#1B4D3E] border-0 rounded-lg">
                          {item.educationLevel}
                        </Badge>
                        <span className="text-xs text-gray-400 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {item.createdAt && formatDate(item.createdAt)}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-[#1B4D3E] rounded-xl flex items-center justify-center">
                          <Briefcase className="w-5 h-5 text-white" />
                        </div>
                        <CardTitle className="text-lg line-clamp-1 text-gray-900">
                          {item.topCareer || `Analysis #${item.id}`}
                        </CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <div className="space-y-4">
                        {/* Interest Tags */}
                        <div className="flex flex-wrap gap-1.5">
                          {item.interests.slice(0, 3).map((tag: string, i: number) => (
                            <span key={i} className="text-xs bg-[#C5E500]/20 text-[#1B4D3E] px-2.5 py-1 rounded-lg font-medium">
                              {tag}
                            </span>
                          ))}
                          {item.interests.length > 3 && (
                            <span className="text-xs text-gray-400 px-2 py-1">
                              +{item.interests.length - 3} more
                            </span>
                          )}
                        </div>
                        
                        {/* View Button */}
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button 
                            className="w-full bg-gray-100 text-gray-700 hover:bg-[#1B4D3E] hover:text-white transition-all duration-300 rounded-xl group-hover:bg-[#1B4D3E] group-hover:text-white"
                            variant="secondary"
                            onClick={() => handleViewResult(item)}
                          >
                            View Result
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </motion.div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Stats Footer */}
          {history && history.length > 0 && (
            <motion.div 
              variants={itemVariants}
              className="flex items-center justify-center gap-8 pt-8 border-t border-gray-100"
            >
              <div className="flex items-center gap-2 text-gray-500">
                <FolderOpen className="w-4 h-4 text-[#1B4D3E]" />
                <span className="text-sm">{history.length} analysis{history.length !== 1 ? 'es' : ''} saved</span>
              </div>
              <div className="flex items-center gap-2 text-gray-500">
                <Clock className="w-4 h-4 text-[#C5E500]" />
                <span className="text-sm">Last updated {history[0]?.createdAt && formatDate(history[0].createdAt)}</span>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </Layout>
  );
}
