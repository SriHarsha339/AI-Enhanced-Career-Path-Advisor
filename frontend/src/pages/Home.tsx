import { useState, useRef, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useLocation } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import {
  GraduationCap,
  Lightbulb,
  User,
  BrainCircuit,
  ArrowRight,
  Loader2,
  Sparkles,
  CheckCircle2,
  Zap,
  Palette,
  Target,
  Briefcase,
  TrendingUp,
  Search,
} from "lucide-react";

import { useCareerRecommendations } from "@/hooks/use-career";
import { insertCareerQuerySchema, type CareerQueryInput } from "@shared/schema";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TagInput } from "@/components/TagInput";

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 }
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

// Processing Visualization Component
function ProcessingVisualization() {
  const steps = [
    { icon: Search, label: "Analyzing Profile", desc: "Understanding your background" },
    { icon: BrainCircuit, label: "AI Processing", desc: "Matching career patterns" },
    { icon: Target, label: "Finding Matches", desc: "Identifying best opportunities" },
    { icon: Briefcase, label: "Building Roadmap", desc: "Creating your career path" },
  ];

  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-white/95 backdrop-blur-sm z-50 flex items-center justify-center"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-3xl p-8 shadow-2xl border border-gray-100 max-w-md w-full mx-4"
      >
        {/* Logo/Icon */}
        <div className="flex justify-center mb-6">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-16 h-16 bg-[#1B4D3E] rounded-2xl flex items-center justify-center"
          >
            <BrainCircuit className="w-8 h-8 text-white" />
          </motion.div>
        </div>

        <h3 className="text-xl font-bold text-center text-gray-900 mb-2">
          Analyzing Your Profile
        </h3>
        <p className="text-gray-500 text-center text-sm mb-8">
          Our AI is finding the best career matches for you
        </p>

        {/* Steps */}
        <div className="space-y-4">
          {steps.map((step, i) => {
            const StepIcon = step.icon;
            const isActive = i === currentStep;
            const isCompleted = i < currentStep;
            
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300 ${
                  isActive ? 'bg-[#1B4D3E]/5 border border-[#1B4D3E]/20' : 
                  isCompleted ? 'bg-[#C5E500]/10' : 'bg-gray-50'
                }`}
              >
                <motion.div
                  animate={isActive ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 1, repeat: isActive ? Infinity : 0 }}
                  className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    isCompleted ? 'bg-[#C5E500]' :
                    isActive ? 'bg-[#1B4D3E]' : 'bg-gray-200'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-[#1B4D3E]" />
                  ) : (
                    <StepIcon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-400'}`} />
                  )}
                </motion.div>
                
                <div className="flex-1">
                  <div className={`font-medium text-sm ${
                    isActive ? 'text-[#1B4D3E]' : 
                    isCompleted ? 'text-[#1B4D3E]' : 'text-gray-500'
                  }`}>
                    {step.label}
                  </div>
                  <div className={`text-xs ${
                    isActive ? 'text-[#1B4D3E]/70' : 'text-gray-400'
                  }`}>
                    {step.desc}
                  </div>
                </div>

                {isActive && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Loader2 className="w-5 h-5 text-[#1B4D3E]" />
                  </motion.div>
                )}
                
                {isCompleted && (
                  <CheckCircle2 className="w-5 h-5 text-[#1B4D3E]" />
                )}
              </motion.div>
            );
          })}
        </div>

        <motion.p 
          className="text-center text-sm text-gray-400 mt-6"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          This usually takes 10-20 seconds...
        </motion.p>
      </motion.div>
    </motion.div>
  );
}

export default function Home() {
  const [, setLocation] = useLocation();
  const { mutate, isPending } = useCareerRecommendations();
  const [llmStatus, setLlmStatus] = useState<"checking" | "connected" | "offline">("checking");
  const containerRef = useRef<HTMLDivElement>(null);

  // Check LLM status on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch("/api/health");
        if (response.ok) {
          const data = await response.json();
          setLlmStatus(data.llm === "connected" ? "connected" : "offline");
        } else {
          setLlmStatus("offline");
        }
      } catch {
        setLlmStatus("offline");
      }
    };
    checkHealth();
  }, []);

  const form = useForm<CareerQueryInput>({
    resolver: zodResolver(insertCareerQuerySchema),
    defaultValues: {
      educationLevel: "",
      interests: [],
      hobbies: [],
      skills: [],
      personalityTraits: [],
      extraInfo: "",
    },
  });

  function onSubmit(data: CareerQueryInput) {
    mutate(data, {
      onSuccess: (response) => {
        sessionStorage.setItem('lastRecommendation', JSON.stringify(response));
        setLocation(`/result/${response.queryId}`);
      },
    });
  }

  const educationLevels = [
    "10th Class",
    "12th Class",
    "High School Diploma",
    "Associate's Degree",
    "Bachelor's Degree",
    "Master's Degree",
    "PhD / Doctorate",
    "Trade School Certification",
    "Self-Taught / Bootcamp",
    "Diploma (Polytechnic)",
    "Other"
  ];

  const sampleData: CareerQueryInput[] = [
    {
      educationLevel: "12th Class",
      interests: ["Technology", "Creative Writing", "Gaming"],
      hobbies: ["Building PCs", "Digital Illustration", "Chess"],
      skills: ["Logic", "Visual Design", "Python Basics"],
      personalityTraits: ["Analytical", "Creative", "Quiet"],
      extraInfo: "I prefer working on a computer and enjoy solving complex puzzles."
    },
    {
      educationLevel: "Bachelor's Degree",
      interests: ["Biology", "Social Work", "Teaching"],
      hobbies: ["Gardening", "Volunteering", "Public Speaking"],
      skills: ["Empathy", "Communication", "Scientific Research"],
      personalityTraits: ["Extroverted", "Caring", "Organized"],
      extraInfo: "I want a career where I can help people directly and see the impact of my work."
    },
    {
      educationLevel: "10th Class",
      interests: ["Cars", "Mechanical Systems", "Sports"],
      hobbies: ["Fixing Bicycles", "Football", "Drawing"],
      skills: ["Hands-on Coordination", "Teamwork", "Basic Math"],
      personalityTraits: ["Active", "Practical", "Reliable"],
      extraInfo: "I'm not interested in long college degrees. I want to start working practically soon."
    }
  ];

  const fillSampleData = () => {
    const randomData = sampleData[Math.floor(Math.random() * sampleData.length)];
    form.reset(randomData);
  };

  return (
    <Layout>
      <div ref={containerRef} className="min-h-screen bg-white py-12 relative overflow-hidden">
        
        {/* Subtle Background Pattern */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-to-bl from-[#1B4D3E]/5 to-transparent" />
          <div className="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-[#C5E500]/10 to-transparent" />
        </div>

        <motion.div 
          className="max-w-5xl mx-auto px-4 relative z-10"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Hero Section */}
          <motion.div variants={itemVariants} className="text-center mb-12">
            <motion.div 
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#C5E500]/20 text-[#1B4D3E] rounded-full text-sm font-medium mb-6"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <Sparkles className="w-4 h-4" />
              AI-Powered Career Discovery
            </motion.div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
              Find Your Perfect
              <span className="block text-[#1B4D3E]">Career Path</span>
            </h1>
            
            <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-6">
              Our AI analyzes your education, skills, and personality to recommend career paths that perfectly match who you are.
            </p>
            
            {/* LLM Status */}
            <div className="flex items-center justify-center gap-2">
              {llmStatus === "checking" && (
                <Badge className="gap-1 bg-gray-100 text-gray-600 border-0">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Checking AI Status...
                </Badge>
              )}
              {llmStatus === "connected" && (
                <Badge className="gap-1 bg-[#1B4D3E]/10 text-[#1B4D3E] border-0">
                  <CheckCircle2 className="w-3 h-3" />
                  AI Connected
                </Badge>
              )}
              {llmStatus === "offline" && (
                <Badge className="gap-1 bg-amber-50 text-amber-700 border-0">
                  <Zap className="w-3 h-3" />
                  Smart Fallback Mode
                </Badge>
              )}
            </div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div 
            variants={itemVariants}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
          >
            {[
              { icon: GraduationCap, title: "Education Based", desc: "Leverage your academic background" },
              { icon: Lightbulb, title: "Interest Matching", desc: "Turn passions into professions" },
              { icon: User, title: "Personality Fit", desc: "Careers that suit your nature" },
              { icon: TrendingUp, title: "Market Insights", desc: "Real-time industry data" },
            ].map((feature, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <Card className="border border-gray-100 bg-white hover:border-[#1B4D3E]/20 hover:shadow-lg transition-all duration-300 rounded-2xl h-full">
                  <CardContent className="p-5">
                    <div className="w-10 h-10 bg-[#1B4D3E]/10 rounded-xl flex items-center justify-center mb-3">
                      <feature.icon className="w-5 h-5 text-[#1B4D3E]" />
                    </div>
                    <h3 className="font-semibold text-sm text-gray-900 mb-1">{feature.title}</h3>
                    <p className="text-xs text-gray-500">{feature.desc}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* Main Form Card */}
          <motion.div variants={itemVariants} className="flex justify-center">
            <Card className="w-full max-w-2xl border border-gray-100 bg-white shadow-xl rounded-3xl overflow-hidden">
              {/* Card Header Accent */}
              <div className="h-1.5 bg-gradient-to-r from-[#1B4D3E] via-[#1B4D3E]/80 to-[#C5E500]" />
              
              <CardHeader className="pb-4 pt-8">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl text-gray-900">Tell us about yourself</CardTitle>
                    <CardDescription className="text-gray-500">
                      The more details you provide, the better the recommendation.
                    </CardDescription>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={fillSampleData}
                    className="rounded-full border-[#1B4D3E]/20 text-[#1B4D3E] hover:bg-[#1B4D3E]/5 hover:border-[#1B4D3E]/40"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Try Sample
                  </Button>
                </div>
              </CardHeader>
              
              <CardContent className="pb-8">
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    
                    {/* Education Level */}
                    <FormField
                      control={form.control}
                      name="educationLevel"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="flex items-center gap-2 text-gray-700">
                            <GraduationCap className="w-4 h-4 text-[#1B4D3E]" /> 
                            Education Level
                          </FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger className="h-12 bg-gray-50 border-gray-200 rounded-xl hover:bg-white hover:border-[#1B4D3E]/30 transition-colors focus:ring-[#1B4D3E]/20 focus:border-[#1B4D3E]">
                                <SelectValue placeholder="Select your highest education" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {educationLevels.map((level) => (
                                <SelectItem key={level} value={level}>{level}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Interests */}
                    <FormField
                      control={form.control}
                      name="interests"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="flex items-center gap-2 text-gray-700">
                            <Palette className="w-4 h-4 text-[#1B4D3E]" />
                            Interests
                          </FormLabel>
                          <FormControl>
                            <TagInput
                              tags={field.value || []}
                              onTagsChange={field.onChange}
                              placeholder="e.g. Photography, Gaming, Writing..."
                            />
                          </FormControl>
                          <FormDescription className="text-gray-400">
                            Things you enjoy doing in your free time.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Hobbies */}
                    <FormField
                      control={form.control}
                      name="hobbies"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="flex items-center gap-2 text-gray-700">
                            <Sparkles className="w-4 h-4 text-[#1B4D3E]" />
                            Hobbies
                          </FormLabel>
                          <FormControl>
                            <TagInput
                              tags={field.value || []}
                              onTagsChange={field.onChange}
                              placeholder="e.g. Chess, Hiking, Coding..."
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid sm:grid-cols-2 gap-4">
                      {/* Skills */}
                      <FormField
                        control={form.control}
                        name="skills"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="flex items-center gap-2 text-gray-700">
                              <BrainCircuit className="w-4 h-4 text-[#1B4D3E]" />
                              Skills
                            </FormLabel>
                            <FormControl>
                              <TagInput
                                tags={field.value || []}
                                onTagsChange={field.onChange}
                                placeholder="e.g. Java, Leadership..."
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      {/* Personality */}
                      <FormField
                        control={form.control}
                        name="personalityTraits"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="flex items-center gap-2 text-gray-700">
                              <User className="w-4 h-4 text-[#1B4D3E]" />
                              Personality Traits
                            </FormLabel>
                            <FormControl>
                              <TagInput
                                tags={field.value || []}
                                onTagsChange={field.onChange}
                                placeholder="e.g. Introvert, Analytical..."
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    {/* Extra Info */}
                    <FormField
                      control={form.control}
                      name="extraInfo"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-gray-700">Anything else?</FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="I prefer remote work, I want to travel, I dislike math..."
                              className="bg-gray-50 border-gray-200 min-h-[100px] rounded-xl hover:bg-white hover:border-[#1B4D3E]/30 transition-colors focus:ring-[#1B4D3E]/20 focus:border-[#1B4D3E]"
                              {...field}
                              value={field.value || ""}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Submit Button */}
                    <motion.div
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <Button 
                        type="submit" 
                        disabled={isPending}
                        className="w-full h-14 text-lg font-semibold bg-[#1B4D3E] hover:bg-[#163d32] text-white rounded-xl transition-all duration-300 shadow-lg shadow-[#1B4D3E]/20"
                      >
                        {isPending ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Analyzing Your Profile...
                          </>
                        ) : (
                          <>
                            Find My Career Path
                            <ArrowRight className="ml-2 h-5 w-5" />
                          </>
                        )}
                      </Button>
                    </motion.div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Trust Indicators */}
          <motion.div 
            variants={itemVariants}
            className="mt-12 text-center"
          >
            <p className="text-sm text-gray-400 mb-4">Trusted by students and professionals</p>
            <div className="flex items-center justify-center gap-8 text-gray-300 flex-wrap">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#C5E500]" />
                <span className="text-sm text-gray-500">10,000+ Career Matches</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#C5E500]" />
                <span className="text-sm text-gray-500">AI-Powered Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#C5E500]" />
                <span className="text-sm text-gray-500">Free to Use</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
        
        {/* Processing Visualization */}
        <AnimatePresence>
          {isPending && <ProcessingVisualization />}
        </AnimatePresence>
      </div>
    </Layout>
  );
}
