import { useEffect, useState, useRef } from "react";
import { useRoute, useLocation } from "wouter";
import { ArrowLeft, Download, Sparkles, MessageCircle, Briefcase, TrendingUp, Compass, CheckCircle2, BookOpen, GraduationCap, Clock, Target, Rocket, Award, X, Eye, Send, Bot, User, Newspaper, ExternalLink, MapPin, DollarSign } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { Button } from "@/components/ui/button";
import { Layout } from "@/components/Layout";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";

interface CourseItem {
  name: string;
  provider: string;
  duration: string;
  level: string;
  description: string;
}

interface RoadmapPhase {
  phase: string;
  title: string;
  duration: string;
  details: string;
  courses?: CourseItem[];
  milestones?: string[];
}

interface LandscapeItem {
  title: string;
  salary: string;
  demand: string;
  description: string;
  requiredSkills?: string[];
  growthRate?: string;
  roadmap?: RoadmapPhase[];
}

interface StructuredData {
  landscape: LandscapeItem[];
  featured: { title: string; alignment: string; passion: string; outlook: string; dayInLife?: string; challenges?: string };
  roadmap: RoadmapPhase[];
  steps: string[];
  marketInsights?: string[];
}

interface NewsItem {
  title: string;
  link: string;
  source: string;
  published: string;
}

// Helper function to parse and format overview text with highlighted keywords
const formatOverviewText = (text: string): JSX.Element[] => {
  // Clean up the text - remove array-like formatting and any existing markers
  let cleanText = text
    .replace(/\|\|\|HIGHLIGHT\|\|\|/g, '') // Remove any existing HIGHLIGHT markers
    .replace(/\|\|\|END\|\|\|/g, '') // Remove any existing END markers
    .replace(/^\[?'|'\]?$/g, '') // Remove leading/trailing brackets and quotes
    .replace(/'\s*,\s*'/g, '. ') // Replace ', ' with period and space for sentence breaks
    .replace(/^["']|["']$/g, '') // Remove outer quotes
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim();
  
  // Split into sentences
  const sentences = cleanText.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 10);
  
  // Keywords to highlight in green (case-insensitive matching)
  const highlightKeywords = [
    // Education & Learning
    'secondary education', '10th Class', '12th class', 'higher studies', 'Bachelor', 'Master', 
    'degree', 'diploma', 'certification', 'course', 'training', 'workshop', 'internship',
    'online course', 'bootcamp', 'university', 'college', 'instructional design', 'curriculum',
    'ADDIE model', 'lessons', 'platform', 'Udemy', 'Teachable', 'Unacademy', 'Coursera',
    // Skills
    'skills', 'programming', 'coding', 'development', 'design', 'communication', 'leadership',
    'problem-solving', 'critical thinking', 'creativity', 'analytical', 'technical',
    'content creation', 'digital media', 'social media', 'video editing', 'graphic design',
    'photography', 'writing', 'language skills', 'mastery',
    // Career related
    'portfolio', 'resume', 'interview', 'networking', 'experience', 'project', 'freelance',
    'job', 'career', 'profession', 'industry', 'company', 'startup', 'business',
    // Platforms & Tools
    'Instagram', 'YouTube', 'LinkedIn', 'GitHub', 'Twitter', 'Medium', 'blog',
    // Action words
    'Learn', 'develop', 'build', 'create', 'practice', 'explore', 'master', 'achieve',
    'focus', 'improve', 'enhance', 'secure', 'complete', 'pursue', 'Choose', 'Design'
  ];
  
  // Create a regex pattern for all keywords (word boundaries for accuracy)
  const keywordPattern = new RegExp(
    `\\b(${highlightKeywords.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`,
    'gi'
  );
  
  return sentences.map((sentence, idx) => {
    // Split sentence by keywords while preserving them
    const parts: { text: string; highlight: boolean }[] = [];
    let lastIndex = 0;
    let match;
    
    // Reset regex lastIndex
    keywordPattern.lastIndex = 0;
    
    while ((match = keywordPattern.exec(sentence)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        parts.push({ text: sentence.slice(lastIndex, match.index), highlight: false });
      }
      // Add the matched keyword
      parts.push({ text: match[0], highlight: true });
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < sentence.length) {
      parts.push({ text: sentence.slice(lastIndex), highlight: false });
    }
    
    // If no parts were created (no matches), just add the whole sentence
    if (parts.length === 0) {
      parts.push({ text: sentence, highlight: false });
    }
    
    return (
      <p key={idx} className="text-sm text-gray-700 leading-relaxed mb-3 last:mb-0">
        {parts.map((part, partIdx) => (
          part.highlight ? (
            <span key={partIdx} className="text-[#1B4D3E] font-semibold bg-[#C5E500]/25 px-1 py-0.5 rounded">
              {part.text}
            </span>
          ) : (
            <span key={partIdx}>{part.text}</span>
          )
        ))}
      </p>
    );
  });
};

// Floating 3D career elements for decoration
const FloatingCareerElements = () => (
  <>
    {/* Briefcase */}
    <motion.div
      className="absolute -top-4 -right-4 w-16 h-16 opacity-20"
      animate={{ 
        y: [0, -10, 0],
        rotate: [0, 5, -5, 0]
      }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
    >
      <svg viewBox="0 0 24 24" fill="none" className="w-full h-full text-[#1B4D3E]">
        <path d="M20 7H4C2.89543 7 2 7.89543 2 9V19C2 20.1046 2.89543 21 4 21H20C21.1046 21 22 20.1046 22 19V9C22 7.89543 21.1046 7 20 7Z" fill="currentColor"/>
        <path d="M16 7V5C16 3.89543 15.1046 3 14 3H10C8.89543 3 8 3.89543 8 5V7" stroke="currentColor" strokeWidth="2"/>
        <path d="M12 11V17M12 11L9 14M12 11L15 14" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    </motion.div>
    
    {/* Graduation Cap */}
    <motion.div
      className="absolute top-1/4 -left-6 w-14 h-14 opacity-15"
      animate={{ 
        y: [0, 8, 0],
        x: [0, 3, 0],
        rotate: [-5, 5, -5]
      }}
      transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
    >
      <svg viewBox="0 0 24 24" fill="none" className="w-full h-full text-[#1B4D3E]">
        <path d="M12 3L1 9L12 15L23 9L12 3Z" fill="currentColor"/>
        <path d="M5 13V17C5 17 8 20 12 20C16 20 19 17 19 17V13" stroke="currentColor" strokeWidth="2" fill="none"/>
        <path d="M21 9V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    </motion.div>
    
    {/* Target/Goal */}
    <motion.div
      className="absolute bottom-1/4 -right-5 w-12 h-12 opacity-15"
      animate={{ 
        scale: [1, 1.1, 1],
        rotate: [0, 10, 0]
      }}
      transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
    >
      <svg viewBox="0 0 24 24" fill="none" className="w-full h-full text-[#C5E500]">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
        <circle cx="12" cy="12" r="6" stroke="currentColor" strokeWidth="2"/>
        <circle cx="12" cy="12" r="2" fill="currentColor"/>
      </svg>
    </motion.div>
    
    {/* Rocket */}
    <motion.div
      className="absolute -bottom-2 left-1/4 w-10 h-10 opacity-20"
      animate={{ 
        y: [0, -15, 0],
        x: [0, 5, 0]
      }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1.5 }}
    >
      <svg viewBox="0 0 24 24" fill="none" className="w-full h-full text-[#1B4D3E]">
        <path d="M12 2C12 2 8 6 8 12C8 18 12 22 12 22C12 22 16 18 16 12C16 6 12 2 12 2Z" fill="currentColor"/>
        <path d="M5 18L8 15M19 18L16 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        <circle cx="12" cy="10" r="2" fill="white"/>
      </svg>
    </motion.div>
    
    {/* Light bulb / Idea */}
    <motion.div
      className="absolute top-1/2 -right-8 w-10 h-10 opacity-15"
      animate={{ 
        opacity: [0.15, 0.3, 0.15],
        scale: [1, 1.05, 1]
      }}
      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.8 }}
    >
      <svg viewBox="0 0 24 24" fill="none" className="w-full h-full text-[#C5E500]">
        <path d="M12 2C8.13 2 5 5.13 5 9C5 11.38 6.19 13.47 8 14.74V17C8 17.55 8.45 18 9 18H15C15.55 18 16 17.55 16 17V14.74C17.81 13.47 19 11.38 19 9C19 5.13 15.87 2 12 2Z" fill="currentColor"/>
        <path d="M9 21H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        <path d="M10 18V21M14 18V21" stroke="currentColor" strokeWidth="1.5"/>
      </svg>
    </motion.div>
    
    {/* Star */}
    <motion.div
      className="absolute -top-2 left-1/3 w-8 h-8 opacity-20"
      animate={{ 
        rotate: [0, 360],
        scale: [1, 1.2, 1]
      }}
      transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
    >
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-full h-full text-[#C5E500]">
        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
      </svg>
    </motion.div>
  </>
);

export default function Result() {
  const [, params] = useRoute("/result/:id");
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [recommendation, setRecommendation] = useState<string | null>(null);
  const [structuredData, setStructuredData] = useState<StructuredData | null>(null);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [newsInsight, setNewsInsight] = useState<string>("");
  const [_isLoadingNews, setIsLoadingNews] = useState(false);
  const [selectedCareerIndex, setSelectedCareerIndex] = useState(0);
  const [expandedPhase, setExpandedPhase] = useState<RoadmapPhase | null>(null);
  const [expandedPhaseIndex, setExpandedPhaseIndex] = useState<number>(0);
  const [showPhaseChat, setShowPhaseChat] = useState(false);
  const [phaseChatMessages, setPhaseChatMessages] = useState<{role: string; content: string}[]>([]);
  const [phaseChatInput, setPhaseChatInput] = useState("");
  const [isPhaseChatLoading, setIsPhaseChatLoading] = useState(false);
  const phaseChatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('lastRecommendation');
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.queryId.toString() === params?.id) {
        setRecommendation(parsed.recommendation);
        setStructuredData(parsed.structuredData);
        
        if (parsed.structuredData?.featured?.title) {
          fetchCareerNews(parsed.structuredData.featured.title);
        }
        
        if (parsed.structuredData?.marketInsights) {
          setNewsInsight(parsed.structuredData.marketInsights[0] || "");
        }
        return;
      }
    }
    
    toast({
      title: "Note",
      description: "Result data is transient in this demo. Check history if persistent storage is enabled.",
    });
  }, [params?.id, toast]);

  const fetchCareerNews = async (career: string) => {
    setIsLoadingNews(true);
    try {
      const response = await fetch(`/api/news/${encodeURIComponent(career)}`);
      if (response.ok) {
        const data = await response.json();
        setNewsItems(data.articles || []);
        if (data.insights) {
          setNewsInsight(data.insights);
        }
      }
    } catch (error) {
      console.error("Failed to fetch news:", error);
    } finally {
      setIsLoadingNews(false);
    }
  };

  const openPhaseChat = () => {
    setShowPhaseChat(true);
    setPhaseChatMessages([{
      role: "assistant",
      content: `🎓 Hi! I'm your **Phase Learning Assistant**. I'm here to help you with everything about:\n\n**${expandedPhase?.title}**\n\nAsk me anything about:\n• How to achieve the milestones\n• Course recommendations and alternatives\n• Time management tips\n• Resources and study materials`
    }]);
  };

  const handlePhaseChatSend = async () => {
    if (!phaseChatInput.trim() || !expandedPhase) return;

    const userMessage = { role: "user", content: phaseChatInput };
    setPhaseChatMessages(prev => [...prev, userMessage]);
    const currentInput = phaseChatInput;
    setPhaseChatInput("");
    setIsPhaseChatLoading(true);

    const phaseContext = `
Career: ${structuredData?.landscape[selectedCareerIndex]?.title || structuredData?.featured?.title}
Current Phase: ${expandedPhase.title}
Duration: ${expandedPhase.duration}
Phase Details: ${expandedPhase.details}
Milestones: ${expandedPhase.milestones?.join(", ") || "None"}
Recommended Courses: ${expandedPhase.courses?.map(c => `${c.name} (${c.provider})`).join(", ") || "None"}
    `.trim();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: `[PHASE-SPECIFIC QUESTION] The user is asking about this specific phase of their career journey:\n\n${phaseContext}\n\nUser's question: ${currentInput}\n\nProvide helpful, specific advice focused on this phase only.`,
          context: phaseContext,
          selectedRole: structuredData?.landscape[selectedCareerIndex]?.title || "",
          conversationHistory: phaseChatMessages.slice(-4)
        })
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();
      setPhaseChatMessages(prev => [...prev, {
        role: "assistant",
        content: data.response || "I'm here to help with this phase! Feel free to ask more questions."
      }]);
    } catch (error) {
      setPhaseChatMessages(prev => [...prev, {
        role: "assistant",
        content: `I'd love to help with "${expandedPhase.title}"! Here are some tips:\n\n1. **Focus on milestones** - Break them into weekly goals\n2. **Start with the recommended courses** - They're selected for this phase\n3. **Track your progress** - Use a simple checklist\n\nWhat specific aspect would you like to explore?`
      }]);
    } finally {
      setIsPhaseChatLoading(false);
      setTimeout(() => {
        phaseChatRef.current?.scrollTo({ top: phaseChatRef.current.scrollHeight, behavior: "smooth" });
      }, 100);
    }
  };

  if (!recommendation) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-4">
          <div className="w-16 h-16 bg-[#1B4D3E]/10 rounded-2xl flex items-center justify-center animate-pulse">
            <Sparkles className="h-8 w-8 text-[#1B4D3E]" />
          </div>
          <h2 className="text-xl font-semibold text-gray-800">Loading your results...</h2>
          <Button variant="outline" onClick={() => setLocation("/history")} className="rounded-full">
            Go to History
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-10">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={() => setLocation("/")} className="gap-2 pl-0 hover:bg-transparent text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <Button variant="outline" onClick={() => window.print()} className="rounded-full border-gray-200">
            <Download className="h-4 w-4 mr-2" />
            Save
          </Button>
        </div>

        {/* Title Section */}
        <div className="text-center space-y-3">
          <motion.div 
            initial={{ opacity: 0, y: 8 }} 
            animate={{ opacity: 1, y: 0 }} 
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#C5E500]/20 text-[#1B4D3E] rounded-full text-sm font-medium"
          >
            <Sparkles className="w-4 h-4" />
            Career Strategy
          </motion.div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            Your Career Blueprint
          </h1>
        </div>

        {/* Featured Recommendation Card */}
        {structuredData?.featured && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card className="bg-[#1B4D3E] text-white overflow-hidden rounded-3xl border-0">
              <div className="flex flex-col md:flex-row">
                <div className="p-8 md:p-10 md:w-2/3 space-y-6">
                  <div className="space-y-3">
                    <Badge className="bg-[#C5E500] hover:bg-[#C5E500] text-[#1B4D3E] font-semibold">
                      Best Match
                    </Badge>
                    <h2 className="text-3xl md:text-4xl font-bold">{structuredData.featured.title}</h2>
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-white/80">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-white font-medium">
                        <CheckCircle2 className="w-4 h-4 text-[#C5E500]" /> Alignment
                      </div>
                      <p className="text-sm leading-relaxed">{structuredData.featured.alignment}</p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-white font-medium">
                        <Compass className="w-4 h-4 text-[#C5E500]" /> Passion Match
                      </div>
                      <p className="text-sm leading-relaxed">{structuredData.featured.passion}</p>
                    </div>
                  </div>
                </div>
                <div className="hidden md:flex md:w-1/3 bg-white/5 items-center justify-center border-l border-white/10">
                  <Briefcase className="w-24 h-24 text-white/20" />
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Career Opportunities Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-5">
            <h3 className="text-lg font-semibold flex items-center gap-2 text-gray-800">
              <TrendingUp className="w-5 h-5 text-[#1B4D3E]" /> Career Opportunities
              <span className="text-sm font-normal text-gray-400 ml-1">(Click for roadmap)</span>
            </h3>
            <div className="grid gap-3">
              {structuredData?.landscape.map((item, i) => (
                <motion.div
                  key={i}
                  whileHover={{ y: -2 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card 
                    className={`cursor-pointer transition-all duration-300 rounded-2xl ${
                      selectedCareerIndex === i 
                        ? 'border-[#1B4D3E] bg-[#1B4D3E]/5 shadow-lg' 
                        : 'border-gray-100 hover:border-[#1B4D3E]/30 hover:shadow-md'
                    }`}
                    onClick={() => setSelectedCareerIndex(i)}
                  >
                    <CardContent className="p-5 flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-gray-900">{item.title}</h4>
                          {selectedCareerIndex === i && (
                            <Badge className="bg-[#1B4D3E] text-white text-xs">Selected</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 line-clamp-1">{item.description}</p>
                      </div>
                      <div className="text-right shrink-0 ml-4">
                        <div className="flex items-center gap-1 font-semibold text-gray-900">
                          <DollarSign className="w-4 h-4 text-[#C5E500]" />
                          {item.salary}
                        </div>
                        <Badge className="bg-[#C5E500]/20 text-[#1B4D3E] text-xs font-medium border-0">
                          {item.demand}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Action Plan */}
          <div className="space-y-5">
            <h3 className="text-lg font-semibold text-gray-800">Action Plan</h3>
            <Card className="bg-gray-50 border-gray-100 rounded-2xl">
              <CardContent className="p-5">
                <ul className="space-y-3">
                  {structuredData?.steps.map((step, i) => (
                    <li key={i} className="flex gap-3 items-start">
                      <div className="w-6 h-6 rounded-full bg-[#1B4D3E] text-white flex items-center justify-center shrink-0 text-xs font-medium mt-0.5">
                        {i + 1}
                      </div>
                      <p className="text-sm text-gray-600 leading-relaxed">{step}</p>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Learning Roadmap Section */}
        <div className="space-y-5 bg-white rounded-3xl border border-gray-100 p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <h3 className="text-lg font-semibold flex items-center gap-2 text-gray-800">
              <div className="p-2 bg-[#1B4D3E]/10 rounded-xl">
                <Compass className="w-5 h-5 text-[#1B4D3E]" />
              </div>
              Learning Roadmap
            </h3>
            <motion.div 
              key={selectedCareerIndex}
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#1B4D3E]/5 border border-[#1B4D3E]/20"
            >
              <Target className="w-4 h-4 text-[#1B4D3E]" />
              <span className="font-medium text-sm text-[#1B4D3E]">
                {structuredData?.landscape[selectedCareerIndex]?.title || structuredData?.featured?.title}
              </span>
            </motion.div>
          </div>
          
          {/* Career Selector Pills */}
          <div className="flex flex-wrap gap-2 pb-3">
            <span className="text-xs text-gray-500 self-center mr-1">Career:</span>
            {structuredData?.landscape.map((career, i) => (
              <motion.button
                key={i}
                onClick={() => setSelectedCareerIndex(i)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  selectedCareerIndex === i
                    ? 'bg-[#1B4D3E] text-white shadow-md'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                }`}
              >
                {career.title}
              </motion.button>
            ))}
          </div>
          
          {/* Phase Cards */}
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedCareerIndex}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.25 }}
              className="relative"
            >
              <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {(structuredData?.landscape[selectedCareerIndex]?.roadmap || structuredData?.roadmap)?.map((item, i) => (
                  <motion.div
                    key={`${selectedCareerIndex}-${i}`}
                    initial={{ opacity: 0, scale: 0.95, y: 12 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ delay: i * 0.08, duration: 0.3 }}
                  >
                    {/* Phase Number */}
                    <div className="flex justify-center mb-3">
                      <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: i * 0.08 + 0.15, type: "spring", stiffness: 200 }}
                        className="w-8 h-8 rounded-full bg-[#1B4D3E] flex items-center justify-center"
                      >
                        <span className="font-medium text-sm text-white">{i + 1}</span>
                      </motion.div>
                    </div>
                    
                    {/* Phase Card */}
                    <motion.div
                      whileHover={{ y: -4 }}
                      className="bg-white rounded-2xl overflow-hidden h-full border border-gray-100 hover:border-[#1B4D3E]/30 hover:shadow-lg transition-all duration-300"
                    >
                      <div className="p-4 bg-[#1B4D3E]/5 border-b border-gray-100">
                        <div className="flex items-center gap-2 text-xs font-medium mb-1 text-[#1B4D3E]">
                          <Clock className="w-3.5 h-3.5" />
                          {item.duration}
                        </div>
                        <h4 className="font-semibold text-sm leading-tight text-gray-900 line-clamp-2">
                          {item.title}
                        </h4>
                      </div>
                      
                      <div className="p-4 space-y-3">
                        <p className="text-xs text-gray-600 leading-relaxed line-clamp-2">
                          {item.details}
                        </p>
                        
                        {item.milestones && item.milestones.length > 0 && (
                          <div className="space-y-1.5">
                            <div className="text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                              <CheckCircle2 className="w-3 h-3 text-[#C5E500]" /> Milestones
                            </div>
                            <div className="space-y-1 max-h-16 overflow-y-auto">
                              {item.milestones.slice(0, 2).map((milestone, mIdx) => (
                                <div key={mIdx} className="flex items-start gap-1.5 text-xs text-gray-600">
                                  <CheckCircle2 className="w-3 h-3 text-[#C5E500] shrink-0 mt-0.5" />
                                  <span className="line-clamp-1">{milestone}</span>
                                </div>
                              ))}
                              {item.milestones.length > 2 && (
                                <span className="text-xs text-gray-400">+{item.milestones.length - 2} more</span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {item.courses && item.courses.length > 0 && (
                          <div className="pt-2 border-t border-dashed border-gray-200">
                            <div className="text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                              <GraduationCap className="w-3 h-3" /> Courses
                            </div>
                            <div className="bg-gray-50 rounded-lg p-2 text-xs">
                              <div className="font-medium text-gray-700 line-clamp-1">{item.courses[0].name}</div>
                              <Badge variant="outline" className="text-[10px] px-2 py-0 mt-1 border-gray-200">{item.courses[0].provider}</Badge>
                            </div>
                            {item.courses.length > 1 && (
                              <span className="text-xs text-gray-400 mt-1 block">+{item.courses.length - 1} more</span>
                            )}
                          </div>
                        )}
                        
                        <button
                          onClick={() => { setExpandedPhase(item); setExpandedPhaseIndex(i); }}
                          className="w-full mt-2 py-2 px-3 rounded-xl text-xs font-medium flex items-center justify-center gap-2 transition-all bg-[#1B4D3E]/10 text-[#1B4D3E] hover:bg-[#1B4D3E] hover:text-white"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          View Details
                        </button>
                      </div>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
              
              {/* Journey Completion */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="flex justify-center pt-6"
              >
                <div className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#C5E500]/20 border border-[#C5E500]/40">
                  <Rocket className="w-4 h-4 text-[#1B4D3E]" />
                  <span className="font-medium text-[#1B4D3E]">Ready to Launch</span>
                  <Award className="w-4 h-4 text-[#1B4D3E]" />
                </div>
              </motion.div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Phase Detail Modal */}
        <AnimatePresence>
          {expandedPhase && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setExpandedPhase(null)}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50"
              />
              
              <motion.div
                initial={{ opacity: 0, x: "100%" }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: "100%" }}
                transition={{ type: "spring", damping: 28, stiffness: 250 }}
                className="fixed right-0 top-0 bottom-0 w-full md:w-[520px] lg:w-[580px] bg-white shadow-2xl z-50 overflow-y-auto"
              >
                {/* Floating 3D Career Elements */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                  <FloatingCareerElements />
                </div>

                {/* Modal Header */}
                <div className="sticky top-0 z-10 p-5 bg-white/95 backdrop-blur-sm border-b border-gray-100">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-8 h-8 rounded-full bg-[#1B4D3E] flex items-center justify-center">
                          <span className="font-medium text-white text-sm">{expandedPhaseIndex + 1}</span>
                        </div>
                        <Badge className="border border-[#1B4D3E]/20 bg-[#1B4D3E]/5 text-[#1B4D3E] text-xs">
                          <Clock className="w-3 h-3 mr-1" /> {expandedPhase.duration}
                        </Badge>
                      </div>
                      <h2 className="text-lg font-bold leading-tight text-gray-900">
                        {expandedPhase.title}
                      </h2>
                    </div>
                    <button
                      onClick={() => setExpandedPhase(null)}
                      className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-500 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Modal Content */}
                <div className="relative z-10 p-5 space-y-5">
                  <div className="bg-gradient-to-br from-white to-gray-50/50 rounded-2xl p-4 border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                      <BookOpen className="w-4 h-4" /> Overview
                    </h3>
                    <div className="space-y-1">
                      {formatOverviewText(expandedPhase.details)}
                    </div>
                  </div>

                  {expandedPhase.milestones && expandedPhase.milestones.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-[#C5E500]" /> Milestones ({expandedPhase.milestones.length})
                      </h3>
                      <div className="space-y-2">
                        {expandedPhase.milestones.map((milestone, mIdx) => (
                          <motion.div
                            key={mIdx}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: mIdx * 0.05 }}
                            className="flex items-start gap-3 p-3 bg-[#1B4D3E]/5 rounded-xl border border-[#1B4D3E]/10"
                          >
                            <div className="w-5 h-5 rounded-full bg-[#C5E500] flex items-center justify-center shrink-0 mt-0.5">
                              <CheckCircle2 className="w-3 h-3 text-[#1B4D3E]" />
                            </div>
                            <span className="text-sm text-gray-700">{milestone}</span>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}

                  {expandedPhase.courses && expandedPhase.courses.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                        <GraduationCap className="w-4 h-4" /> Courses ({expandedPhase.courses.length})
                      </h3>
                      <div className="space-y-3">
                        {expandedPhase.courses.map((course, cIdx) => (
                          <motion.div
                            key={cIdx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: cIdx * 0.05 }}
                            className="bg-gray-50 rounded-xl p-4 border border-gray-100"
                          >
                            <div className="flex items-start justify-between gap-3 mb-2">
                              <h4 className="font-medium text-sm text-gray-800">{course.name}</h4>
                              <Badge className="shrink-0 text-xs bg-[#1B4D3E]/10 text-[#1B4D3E] border-0">
                                {course.level}
                              </Badge>
                            </div>
                            <p className="text-xs text-gray-600 mb-3">{course.description}</p>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="flex items-center gap-1.5 bg-white px-2.5 py-1 rounded-lg border border-gray-100">
                                <MapPin className="w-3 h-3" /> {course.provider}
                              </span>
                              <span className="flex items-center gap-1.5 bg-white px-2.5 py-1 rounded-lg border border-gray-100">
                                <Clock className="w-3 h-3" /> {course.duration}
                              </span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Chat Button & Interface */}
                  <div className="pt-4 border-t border-gray-100 space-y-3">
                    {!showPhaseChat && (
                      <button
                        onClick={openPhaseChat}
                        className="w-full py-3 px-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 bg-[#1B4D3E]/10 text-[#1B4D3E] hover:bg-[#1B4D3E] hover:text-white border border-[#1B4D3E]/20"
                      >
                        <MessageCircle className="w-4 h-4" />
                        Ask AI About This Phase
                      </button>
                    )}
                    
                    <AnimatePresence>
                      {showPhaseChat && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="border border-gray-200 rounded-xl overflow-hidden"
                        >
                          <div className="px-4 py-3 flex items-center justify-between bg-[#1B4D3E] border-b border-[#1B4D3E]">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 rounded-full bg-[#C5E500] flex items-center justify-center">
                                <Bot className="w-4 h-4 text-[#1B4D3E]" />
                              </div>
                              <span className="font-medium text-sm text-white">Phase Assistant</span>
                            </div>
                            <button onClick={() => setShowPhaseChat(false)} className="text-white/70 hover:text-white">
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                          
                          <div ref={phaseChatRef} className="h-64 overflow-y-auto p-4 space-y-3 bg-gray-50">
                            {phaseChatMessages.map((msg, idx) => (
                              <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                              >
                                {msg.role === "assistant" && (
                                  <div className="w-7 h-7 rounded-full bg-[#1B4D3E] flex items-center justify-center shrink-0">
                                    <Bot className="w-4 h-4 text-white" />
                                  </div>
                                )}
                                <div className={`max-w-[80%] p-3 rounded-xl text-sm ${
                                  msg.role === "user" 
                                    ? "bg-[#1B4D3E] text-white rounded-br-sm" 
                                    : "bg-white text-gray-700 rounded-bl-sm border border-gray-100"
                                }`}>
                                  {msg.content.split('\n').map((line, i) => {
                                    const formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                                    if (line.startsWith('•')) {
                                      return <div key={i} className="flex gap-2 my-0.5" dangerouslySetInnerHTML={{ __html: formattedLine }} />;
                                    }
                                    return <div key={i} dangerouslySetInnerHTML={{ __html: formattedLine }} />;
                                  })}
                                </div>
                                {msg.role === "user" && (
                                  <div className="w-7 h-7 rounded-full bg-[#C5E500] flex items-center justify-center shrink-0">
                                    <User className="w-4 h-4 text-[#1B4D3E]" />
                                  </div>
                                )}
                              </motion.div>
                            ))}
                            {isPhaseChatLoading && (
                              <div className="flex gap-2 justify-start">
                                <div className="w-7 h-7 rounded-full bg-[#1B4D3E] flex items-center justify-center shrink-0">
                                  <Bot className="w-4 h-4 text-white" />
                                </div>
                                <div className="bg-white p-3 rounded-xl rounded-bl-sm border border-gray-100">
                                  <div className="flex gap-1">
                                    <span className="w-2 h-2 rounded-full bg-[#1B4D3E] animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="w-2 h-2 rounded-full bg-[#1B4D3E] animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="w-2 h-2 rounded-full bg-[#1B4D3E] animate-bounce" style={{ animationDelay: '300ms' }} />
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                          
                          <div className="p-3 border-t border-gray-200 bg-white">
                            <div className="flex gap-2">
                              <input
                                type="text"
                                value={phaseChatInput}
                                onChange={(e) => setPhaseChatInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handlePhaseChatSend()}
                                placeholder="Ask about this phase..."
                                className="flex-1 px-4 py-2 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-[#1B4D3E]/20 focus:border-[#1B4D3E]"
                              />
                              <button
                                onClick={handlePhaseChatSend}
                                disabled={isPhaseChatLoading || !phaseChatInput.trim()}
                                className="px-4 py-2 rounded-xl bg-[#1B4D3E] text-white font-medium disabled:opacity-50 transition-opacity"
                              >
                                <Send className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                    
                    <button
                      onClick={() => { setExpandedPhase(null); setShowPhaseChat(false); }}
                      className="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
                    >
                      <X className="w-4 h-4" />
                      Close
                    </button>
                  </div>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Market News Section */}
        {(newsItems.length > 0 || newsInsight) && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            <h3 className="text-xl font-bold flex items-center gap-3 text-gray-900">
              <Newspaper className="w-5 h-5 text-[#1B4D3E]" /> Market News & Insights
            </h3>
            
            {newsInsight && (
              <Card className="bg-[#C5E500]/10 border-[#C5E500]/30 rounded-2xl">
                <CardContent className="p-5">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-xl bg-[#C5E500]">
                      <Sparkles className="w-4 h-4 text-[#1B4D3E]" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-[#1B4D3E] mb-1">Market Insight</h4>
                      <p className="text-sm text-gray-700 leading-relaxed">{newsInsight}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {newsItems.length > 0 && (
              <div className="grid md:grid-cols-2 gap-4">
                {newsItems.slice(0, 4).map((news, i) => (
                  <motion.a
                    key={i}
                    href={news.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * i }}
                    className="group"
                  >
                    <Card className="h-full border-gray-100 hover:border-[#1B4D3E]/30 hover:shadow-md transition-all duration-200 rounded-2xl">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="text-sm font-medium text-gray-800 group-hover:text-[#1B4D3E] transition-colors line-clamp-2">
                            {news.title}
                          </h4>
                          <ExternalLink className="w-4 h-4 text-gray-400 shrink-0 group-hover:text-[#1B4D3E] transition-colors" />
                        </div>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                          <Badge className="text-[10px] bg-gray-100 text-gray-600 border-0">{news.source}</Badge>
                          <span>{news.published}</span>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.a>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Bottom Action Cards */}
        <div className="grid sm:grid-cols-3 gap-6 pt-8 border-t border-gray-100">
          <motion.div 
            whileHover={{ y: -4 }}
            className="bg-[#1B4D3E]/5 hover:bg-[#1B4D3E]/10 rounded-3xl p-6 flex items-center justify-between cursor-pointer transition-colors" 
            onClick={() => setLocation("/chat")}
          >
            <div className="space-y-1">
              <h4 className="text-lg font-bold text-gray-900">Career Assistant</h4>
              <p className="text-sm text-gray-500">Discuss options in detail</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-[#1B4D3E] text-white flex items-center justify-center">
              <MessageCircle className="w-6 h-6" />
            </div>
          </motion.div>
          
          <motion.div 
            whileHover={{ y: -4 }}
            className="bg-[#C5E500]/10 hover:bg-[#C5E500]/20 rounded-3xl p-6 flex items-center justify-between cursor-pointer transition-colors" 
            onClick={() => {
              if (structuredData?.featured?.title) {
                fetchCareerNews(structuredData.featured.title);
              }
            }}
          >
            <div className="space-y-1">
              <h4 className="text-lg font-bold text-[#1B4D3E]">Market Insights</h4>
              <p className="text-sm text-gray-500">Latest industry trends</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-[#C5E500] text-[#1B4D3E] flex items-center justify-center">
              <Newspaper className="w-6 h-6" />
            </div>
          </motion.div>
          
          <motion.div 
            whileHover={{ y: -4 }}
            className="bg-gray-50 hover:bg-gray-100 rounded-3xl p-6 flex items-center justify-between cursor-pointer transition-colors" 
            onClick={() => setLocation("/")}
          >
            <div className="space-y-1">
              <h4 className="text-lg font-bold text-gray-900">New Analysis</h4>
              <p className="text-sm text-gray-500">Explore different paths</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-white border border-gray-200 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-gray-400" />
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
}
