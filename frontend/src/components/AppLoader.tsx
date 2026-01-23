import { motion } from "framer-motion";
import { Brain, GraduationCap, Target } from "lucide-react";

interface AppLoaderProps {
  isLoading: boolean;
}

export function AppLoader({ isLoading }: AppLoaderProps) {
  if (!isLoading) return null;

  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)' }}
    >
      {/* Subtle dots pattern */}
      <div className="absolute inset-0 opacity-30" style={{
        backgroundImage: `radial-gradient(circle, #cbd5e1 1px, transparent 1px)`,
        backgroundSize: '24px 24px',
      }} />

      {/* Main loader content */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Clean logo */}
        <motion.div
          className="relative mb-8"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="w-20 h-20 rounded-2xl flex items-center justify-center shadow-lg bg-white" style={{ 
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
          }}>
            <Brain className="w-10 h-10" style={{ color: '#3b5998' }} />
          </div>
          
          {/* Corner accent */}
          <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full" style={{ background: '#f97316' }} />
        </motion.div>

        {/* Project title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-10 max-w-2xl px-6"
        >
          <motion.h1 
            className="text-2xl md:text-3xl font-semibold tracking-tight leading-tight"
            style={{ color: '#1e3a5f' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            AI Career Path Advisor
          </motion.h1>
          <motion.p 
            className="text-sm md:text-base mt-2 font-normal"
            style={{ color: '#64748b' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            Personalized career guidance powered by AI
          </motion.p>
        </motion.div>

        {/* Loading indicator */}
        <div className="flex flex-col items-center gap-5">
          {/* Progress bar */}
          <div className="w-48 h-1 rounded-full overflow-hidden" style={{ background: '#e2e8f0' }}>
            <motion.div
              className="h-full rounded-full"
              style={{ background: 'linear-gradient(90deg, #3b5998, #5b7bb8)' }}
              initial={{ width: '0%' }}
              animate={{ width: '100%' }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
          </div>

          {/* Feature tags */}
          <motion.div 
            className="flex flex-wrap justify-center gap-3 mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {[
              { icon: Brain, text: "AI Analysis" },
              { icon: Target, text: "Career Matching" },
              { icon: GraduationCap, text: "Learning Paths" },
            ].map((item, i) => (
              <motion.div
                key={i}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white shadow-sm"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + i * 0.1 }}
                style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
              >
                <item.icon className="w-3.5 h-3.5" style={{ color: '#f97316' }} />
                <span className="text-xs font-medium" style={{ color: '#475569' }}>{item.text}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
