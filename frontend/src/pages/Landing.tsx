import { useState } from "react";
import { Link, useLocation } from "wouter";
import { motion } from "framer-motion";
import { 
  Sparkles, 
  Compass,
  Map,
  Rocket,
  Target,
  TrendingUp,
  Award,
  Users,
  ArrowRight,
  ChevronRight,
  GraduationCap,
  Briefcase,
  Brain,
  Zap
} from "lucide-react";
import { Button } from "@/components/ui/button";

// Interactive Puzzle Component
const InteractivePuzzle = () => {
  const [hoveredPiece, setHoveredPiece] = useState<number | null>(null);
  
  const puzzlePieces = [
    { id: 1, x: 0, y: 0, color: "#C5E500", delay: 0 },
    { id: 2, x: 1, y: 0, color: "#1B4D3E", delay: 0.1 },
    { id: 3, x: 2, y: 0, color: "transparent", delay: 0.2, border: true },
    { id: 4, x: 0, y: 1, color: "#1B4D3E", delay: 0.15 },
    { id: 5, x: 1, y: 1, color: "#C5E500", delay: 0.25 },
    { id: 6, x: 2, y: 1, color: "#C5E500", delay: 0.3 },
    { id: 7, x: 0, y: 2, color: "transparent", delay: 0.2, border: true },
    { id: 8, x: 1, y: 2, color: "#1B4D3E", delay: 0.35 },
    { id: 9, x: 2, y: 2, color: "#C5E500", delay: 0.4 },
  ];

  return (
    <div className="relative w-full max-w-md aspect-square">
      {/* Background grid dots */}
      <div className="absolute inset-0 opacity-20">
        {Array.from({ length: 8 }).map((_, row) =>
          Array.from({ length: 8 }).map((_, col) => (
            <div
              key={`${row}-${col}`}
              className="absolute w-1 h-1 bg-gray-400 rounded-full"
              style={{ left: `${col * 14}%`, top: `${row * 14}%` }}
            />
          ))
        )}
      </div>
      
      {/* Puzzle Grid */}
      <div className="absolute inset-0 grid grid-cols-3 gap-3 p-4">
        {puzzlePieces.map((piece) => (
          <motion.div
            key={piece.id}
            initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
            animate={{ 
              opacity: 1, 
              scale: hoveredPiece === piece.id ? 1.08 : 1,
              rotate: hoveredPiece === piece.id ? 5 : 0,
              y: hoveredPiece === piece.id ? -8 : 0
            }}
            transition={{ 
              delay: piece.delay,
              duration: 0.4,
              type: "spring",
              stiffness: 200
            }}
            onMouseEnter={() => setHoveredPiece(piece.id)}
            onMouseLeave={() => setHoveredPiece(null)}
            className="relative cursor-pointer"
          >
            {/* Puzzle piece shape */}
            <svg
              viewBox="0 0 100 100"
              className="w-full h-full drop-shadow-lg"
              style={{ filter: hoveredPiece === piece.id ? 'drop-shadow(0 10px 20px rgba(27, 77, 62, 0.3))' : '' }}
            >
              {/* Main puzzle piece with connectors */}
              <path
                d={`
                  M 15 5
                  L 35 5
                  C 35 5, 40 -5, 50 -5
                  C 60 -5, 65 5, 65 5
                  L 85 5
                  Q 95 5, 95 15
                  L 95 35
                  C 95 35, 105 40, 105 50
                  C 105 60, 95 65, 95 65
                  L 95 85
                  Q 95 95, 85 95
                  L 65 95
                  C 65 95, 60 105, 50 105
                  C 40 105, 35 95, 35 95
                  L 15 95
                  Q 5 95, 5 85
                  L 5 65
                  C 5 65, -5 60, -5 50
                  C -5 40, 5 35, 5 35
                  L 5 15
                  Q 5 5, 15 5
                  Z
                `}
                fill={piece.color}
                stroke={piece.border ? "#e5e7eb" : "none"}
                strokeWidth={piece.border ? 2 : 0}
                strokeDasharray={piece.border ? "4 4" : "0"}
                className="transition-all duration-300"
              />
              
              {/* Inner decoration for colored pieces */}
              {!piece.border && piece.color !== "transparent" && (
                <g>
                  {piece.color === "#C5E500" && (
                    <circle cx="50" cy="50" r="15" fill="#1B4D3E" opacity="0.15" />
                  )}
                  {piece.color === "#1B4D3E" && (
                    <>
                      <line x1="30" y1="50" x2="70" y2="50" stroke="#C5E500" strokeWidth="2" opacity="0.4" />
                      <line x1="50" y1="30" x2="50" y2="70" stroke="#C5E500" strokeWidth="2" opacity="0.4" />
                    </>
                  )}
                </g>
              )}
            </svg>
            
            {/* Glow effect on hover */}
            {hoveredPiece === piece.id && piece.color !== "transparent" && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 rounded-2xl"
                style={{
                  background: `radial-gradient(circle, ${piece.color}40 0%, transparent 70%)`,
                  filter: 'blur(10px)',
                  zIndex: -1
                }}
              />
            )}
          </motion.div>
        ))}
      </div>
      
      {/* Floating career icons around puzzle */}
      <motion.div
        animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        className="absolute -top-6 right-1/4 w-12 h-12 bg-white rounded-2xl shadow-lg flex items-center justify-center border border-gray-100"
      >
        <Briefcase className="w-6 h-6 text-[#1B4D3E]" />
      </motion.div>
      
      <motion.div
        animate={{ y: [0, 8, 0], rotate: [0, -5, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
        className="absolute top-1/4 -left-6 w-10 h-10 bg-[#C5E500] rounded-xl shadow-lg flex items-center justify-center"
      >
        <Target className="w-5 h-5 text-[#1B4D3E]" />
      </motion.div>
      
      <motion.div
        animate={{ y: [0, -8, 0], x: [0, 5, 0] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute bottom-1/4 -right-4 w-10 h-10 bg-white rounded-xl shadow-lg flex items-center justify-center border border-gray-100"
      >
        <GraduationCap className="w-5 h-5 text-[#1B4D3E]" />
      </motion.div>
      
      <motion.div
        animate={{ scale: [1, 1.1, 1], rotate: [0, 10, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.8 }}
        className="absolute -bottom-4 left-1/3 w-8 h-8 bg-[#1B4D3E] rounded-lg shadow-lg flex items-center justify-center"
      >
        <Rocket className="w-4 h-4 text-[#C5E500]" />
      </motion.div>
    </div>
  );
};

export default function Landing() {
  const [, setLocation] = useLocation();

  const careerPaths = [
    {
      icon: Brain,
      title: "AI & Machine Learning",
      description: "Build intelligent systems and shape the future of technology with cutting-edge AI skills.",
      growth: "+45%",
      salary: "$120k - $180k"
    },
    {
      icon: Briefcase,
      title: "Product Management",
      description: "Lead product strategy and drive innovation from concept to market success.",
      growth: "+32%",
      salary: "$100k - $160k"
    },
    {
      icon: TrendingUp,
      title: "Data Science",
      description: "Transform data into actionable insights and drive data-driven decision making.",
      growth: "+38%",
      salary: "$95k - $150k"
    },
    {
      icon: Zap,
      title: "Cloud Architecture",
      description: "Design scalable infrastructure and power the backbone of modern applications.",
      growth: "+41%",
      salary: "$130k - $190k"
    }
  ];

  const howItWorks = [
    {
      step: "01",
      title: "Share Your Profile",
      description: "Tell us about your education, skills, interests, and career aspirations.",
      icon: Users
    },
    {
      step: "02",
      title: "AI Analysis",
      description: "Our AI analyzes your profile against thousands of career paths and market trends.",
      icon: Brain
    },
    {
      step: "03",
      title: "Get Your Roadmap",
      description: "Receive personalized career recommendations with step-by-step learning paths.",
      icon: Map
    }
  ];

  const stats = [
    { value: "15,000+", label: "Career Paths Discovered" },
    { value: "95%", label: "User Satisfaction" },
    { value: "50,000+", label: "AI Recommendations" },
    { value: "300+", label: "Industries Covered" }
  ];

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100">
        <div className="container max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#1B4D3E] flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-[#C5E500]" />
            </div>
            <span className="text-lg font-semibold text-[#1B4D3E]">PathFinder</span>
          </Link>
          
          <nav className="hidden md:flex items-center gap-1">
            {[
              { label: "Home", active: true },
              { label: "How it works", active: false },
              { label: "Career Paths", active: false },
              { label: "Resources", active: false }
            ].map((item) => (
              <button
                key={item.label}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
                  item.active 
                    ? "bg-white border border-gray-200 text-gray-900 shadow-sm" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${item.active ? 'bg-[#1B4D3E]' : 'bg-gray-300'}`} />
                {item.label}
              </button>
            ))}
          </nav>
          
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => setLocation("/login")} className="text-gray-700 hover:text-[#1B4D3E]">
              Log In
            </Button>
            <Button 
              onClick={() => setLocation("/discover")}
              className="bg-[#1B4D3E] hover:bg-[#153D32] text-white rounded-full px-6"
            >
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-28 pb-12 relative overflow-hidden">
        <div className="container max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center min-h-[70vh]">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="max-w-xl"
            >
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-[1.1] mb-6">
                Discover the joy of{" "}
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="inline-flex items-center gap-2"
                >
                  <motion.span
                    whileHover={{ scale: 1.05 }}
                    className="bg-[#C5E500] px-3 py-1 rounded-lg"
                  >
                    effortless
                  </motion.span>
                  <motion.span
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                  >
                    <Compass className="w-10 h-10 text-[#1B4D3E]/60" />
                  </motion.span>
                </motion.span>{" "}
                career discovery{" "}
                <motion.span
                  whileHover={{ scale: 1.05 }}
                  className="bg-[#1B4D3E] text-white px-3 py-1 rounded-lg inline-block"
                >
                  with PathFinder.
                </motion.span>
              </h1>
              
              <p className="text-lg text-gray-600 mb-10 leading-relaxed">
                PathFinder's AI-powered career recommendation system is now available and ready to 
                revolutionize the way you think about your professional journey and growth.
              </p>
              
              {/* Feature Cards Row */}
              <div className="flex flex-wrap gap-4 mb-8">
                <Button 
                  size="lg"
                  onClick={() => setLocation("/discover")}
                  className="bg-[#1B4D3E] hover:bg-[#153D32] text-white rounded-full px-8 h-14 text-base font-semibold shadow-lg shadow-[#1B4D3E]/20"
                >
                  GET STARTED
                </Button>
              </div>
            </motion.div>
            
            {/* Right - Interactive Puzzle */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative flex justify-center items-center"
            >
              <InteractivePuzzle />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Feature Strip */}
      <section className="py-6 border-y border-gray-200 bg-white">
        <div className="container max-w-7xl mx-auto px-6">
          <div className="flex flex-wrap items-center justify-between gap-6">
            {[
              { icon: Compass, title: "A WORLD OF POSSIBILITIES", desc: "Discover career paths aligned with your unique skills and aspirations." },
              { icon: Award, title: "QUALITY RECOMMENDATIONS", desc: "AI-powered insights based on real market data and trends." },
              { icon: Rocket, title: "ACCELERATE YOUR GROWTH", desc: "Personalized roadmaps to reach your career goals faster." }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-4 flex-1 min-w-[280px] group cursor-pointer"
              >
                <div className="w-12 h-12 rounded-xl bg-gray-100 group-hover:bg-[#C5E500]/20 flex items-center justify-center transition-colors">
                  <item.icon className="w-6 h-6 text-[#1B4D3E]" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2 group-hover:text-[#1B4D3E] transition-colors">
                    {item.title}
                    <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="container max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="inline-block px-4 py-2 bg-[#C5E500]/20 text-[#1B4D3E] rounded-full text-sm font-medium mb-4">
              How It Works
            </span>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Your Career Journey in{" "}
              <span className="text-[#1B4D3E]">3 Simple Steps</span>
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our AI-powered platform makes career discovery simple, personalized, and actionable.
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {howItWorks.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15 }}
                className="relative group"
              >
                <div className="bg-gray-50 rounded-3xl p-8 border border-gray-100 hover:border-[#1B4D3E]/20 hover:shadow-xl transition-all duration-300 h-full">
                  {/* Step Number */}
                  <div className="flex items-center gap-4 mb-6">
                    <span className="text-5xl font-bold text-[#C5E500]">{item.step}</span>
                    <div className="w-12 h-12 rounded-2xl bg-[#1B4D3E] flex items-center justify-center">
                      <item.icon className="w-6 h-6 text-[#C5E500]" />
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{item.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{item.description}</p>
                </div>
                
                {/* Connector Arrow */}
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ArrowRight className="w-8 h-8 text-[#C5E500]" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Career Paths Section */}
      <section className="py-20 bg-[#FAFAFA]">
        <div className="container max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="inline-block px-4 py-2 bg-[#1B4D3E] text-white rounded-full text-sm font-medium mb-4">
              Trending Career Paths
            </span>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Explore High-Growth{" "}
              <span className="bg-[#C5E500] px-2 rounded">Careers</span>
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Discover the most in-demand career paths with strong growth potential and competitive salaries.
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {careerPaths.map((career, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8 }}
                className="bg-white rounded-2xl p-6 border border-gray-100 hover:border-[#1B4D3E]/20 hover:shadow-xl transition-all duration-300 cursor-pointer group"
              >
                <div className="w-14 h-14 rounded-2xl bg-[#C5E500]/20 group-hover:bg-[#C5E500] flex items-center justify-center mb-5 transition-colors">
                  <career.icon className="w-7 h-7 text-[#1B4D3E]" />
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-[#1B4D3E] transition-colors">
                  {career.title}
                </h3>
                <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                  {career.description}
                </p>
                
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="flex items-center gap-1 text-sm">
                    <TrendingUp className="w-4 h-4 text-[#C5E500]" />
                    <span className="font-semibold text-[#1B4D3E]">{career.growth}</span>
                  </div>
                  <span className="text-xs text-gray-500 font-medium">{career.salary}</span>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <Button 
              onClick={() => setLocation("/discover")}
              className="bg-[#1B4D3E] hover:bg-[#153D32] text-white rounded-full px-8 h-12"
            >
              Explore All Career Paths
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-[#C5E500]">
        <div className="container max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <p className="text-4xl lg:text-5xl font-bold text-[#1B4D3E]">{stat.value}</p>
                <p className="text-[#1B4D3E]/70 mt-2 font-medium">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-[#1B4D3E] relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#C5E500]/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-72 h-72 bg-[#C5E500]/10 rounded-full blur-3xl" />
        </div>
        
        <div className="container max-w-4xl mx-auto px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
              Ready to Find Your{" "}
              <span className="text-[#C5E500]">Dream Career?</span>
            </h2>
            <p className="text-white/70 mb-10 text-lg max-w-2xl mx-auto">
              Join thousands of professionals who have discovered their perfect career path with PathFinder's AI-powered recommendations.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button 
                size="lg"
                onClick={() => setLocation("/discover")}
                className="bg-[#C5E500] hover:bg-[#B5D500] text-[#1B4D3E] rounded-full px-10 h-14 font-bold text-base shadow-lg"
              >
                Start Your Journey
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                size="lg"
                variant="outline"
                onClick={() => setLocation("/login")}
                className="border-white/30 text-white hover:bg-white/10 rounded-full px-10 h-14"
              >
                Sign In
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1B4D3E] border-t border-white/10 py-12">
        <div className="container max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-[#C5E500]" />
              </div>
              <span className="text-lg font-semibold text-white">PathFinder</span>
            </div>
            
            <div className="flex items-center gap-8 text-sm text-white/60">
              <span className="hover:text-white cursor-pointer transition-colors">About</span>
              <span className="hover:text-white cursor-pointer transition-colors">Careers</span>
              <span className="hover:text-white cursor-pointer transition-colors">Privacy</span>
              <span className="hover:text-white cursor-pointer transition-colors">Terms</span>
            </div>
            
            <p className="text-white/50 text-sm">
              © {new Date().getFullYear()} PathFinder. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
