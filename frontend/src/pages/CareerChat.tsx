import { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";
import { Send, MessageCircle, ArrowLeft, Sparkles, Briefcase, BookOpen, Lightbulb, Bot, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Layout } from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestedQuestions?: string[];
}

interface RecommendedRole {
  title: string;
  salary?: string;
  demand?: string;
}

export default function CareerChat() {
  const [, setLocation] = useLocation();
  useToast();
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [recommendedRoles, setRecommendedRoles] = useState<RecommendedRole[]>([]);
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "👋 Hi! I'm your AI Career Advisor. I can help you explore your recommended careers in depth.\n\n**Select a role above** to get specialized advice, or ask me anything about:\n\n• Day-to-day responsibilities\n• Required skills & how to learn them\n• Salary expectations & negotiation\n• Career progression paths\n• Interview preparation tips",
      suggestedQuestions: [
        "What skills should I learn first?",
        "How do I build a portfolio?",
        "What's the typical career path?"
      ]
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<{role: string, content: string}[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load recommended roles from session storage
  useEffect(() => {
    const lastRec = sessionStorage.getItem('lastRecommendation');
    if (lastRec) {
      try {
        const parsed = JSON.parse(lastRec);
        const landscape = parsed.structuredData?.landscape || [];
        const roles = landscape.map((item: any) => ({
          title: item.title,
          salary: item.salary,
          demand: item.demand
        }));
        setRecommendedRoles(roles);
        
        if (parsed.structuredData?.featured?.title) {
          setSelectedRole(parsed.structuredData.featured.title);
        }
      } catch (e) {
        console.error("Failed to parse recommendations:", e);
      }
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleRoleSelect = (role: string) => {
    setSelectedRole(role);
    
    const roleMessage: Message = {
      id: Date.now().toString(),
      role: "assistant",
      content: `🎯 Great choice! I'm now focused on helping you explore **${role}**.\n\nThis role has great potential. What would you like to know?\n\n• Daily responsibilities and work environment\n• Skills you need and how to develop them\n• Salary ranges and career progression\n• How to break into this field`,
      suggestedQuestions: [
        `What does a typical day look like for a ${role}?`,
        `What skills are essential for ${role}?`,
        `How do I get my first job as a ${role}?`
      ]
    };
    
    setMessages(prev => [...prev, roleMessage]);
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    const newHistory = [...conversationHistory, { role: "user", content: currentInput }];
    setConversationHistory(newHistory);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: currentInput,
          context: selectedRole,
          selectedRole: selectedRole,
          conversationHistory: newHistory.slice(-6)
        })
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response || "I'm here to discuss your career options. Feel free to ask more questions!",
        suggestedQuestions: data.suggestedQuestions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationHistory(prev => [...prev, { role: "assistant", content: data.response }]);
      
    } catch (error) {
      console.error("Chat error:", error);
      
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I'm having a brief connection issue, but I can still help! ${selectedRole ? `For a career in **${selectedRole}**, I recommend:

1. **Start Learning:** Take courses on Coursera, Udemy, or YouTube
2. **Build Projects:** Create a portfolio with 2-3 real projects
3. **Network:** Connect with professionals on LinkedIn
4. **Apply:** Look for internships and entry-level roles

What specific aspect would you like to explore?` : "Please select a role above to get specialized advice, or ask me general career questions!"}`,
        suggestedQuestions: [
          "What courses should I take?",
          "How do I create a portfolio?",
          "What companies are hiring?"
        ]
      };
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, i) => {
      line = line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-[#1B4D3E] font-semibold">$1</strong>');
      line = line.replace(/^#{1,3}\s+/, '');
      
      if (/^\d+\.\s/.test(line)) {
        const num = line.match(/^(\d+)\./)?.[1];
        line = line.replace(/^(\d+)\.\s*/, '');
        return (
          <div key={i} className="flex gap-2 items-start my-1">
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-[#1B4D3E]/10 text-[#1B4D3E] text-xs font-bold shrink-0">{num}</span>
            <span dangerouslySetInnerHTML={{ __html: line }} />
          </div>
        );
      }
      
      if (line.startsWith('• ') || line.startsWith('- ')) {
        line = line.replace(/^[•-]\s*/, '');
        return (
          <div key={i} className="flex gap-2 items-start my-0.5 pl-1">
            <span className="text-[#C5E500] mt-1.5">•</span>
            <span dangerouslySetInnerHTML={{ __html: line }} />
          </div>
        );
      }
      
      if (!line.trim()) {
        return <div key={i} className="h-2" />;
      }
      
      return <div key={i} dangerouslySetInnerHTML={{ __html: line }} className="leading-relaxed" />;
    });
  };

  return (
    <Layout>
      <div className="min-h-screen bg-white py-4 relative">
        
        {/* Subtle Background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-1/2 h-1/3 bg-gradient-to-bl from-[#1B4D3E]/5 to-transparent" />
          <div className="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-[#C5E500]/5 to-transparent" />
        </div>
        
        <div className="max-w-3xl mx-auto h-[85vh] flex flex-col space-y-4 px-4 relative z-10">
          {/* Header */}
          <motion.div 
            className="flex items-center justify-between"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Button 
              variant="ghost" 
              onClick={() => setLocation("/discover")} 
              className="gap-2 pl-0 hover:bg-transparent text-gray-500 hover:text-gray-800"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
            <div className="flex items-center gap-2 bg-[#1B4D3E]/10 px-4 py-2 rounded-full">
              <Sparkles className="h-4 w-4 text-[#1B4D3E]" />
              <span className="text-sm text-[#1B4D3E] font-medium">Career Advisor</span>
            </div>
          </motion.div>

          {/* Role Selection */}
          {recommendedRoles.length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.4 }}
              className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-[#1B4D3E]/10 rounded-xl flex items-center justify-center">
                  <Briefcase className="h-5 w-5 text-[#1B4D3E]" />
                </div>
                <span className="text-base font-semibold text-gray-800">Select a role to explore:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {recommendedRoles.map((role, idx) => (
                  <motion.button
                    key={role.title}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.15 + idx * 0.1 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRoleSelect(role.title)}
                    className={`
                      px-4 py-2.5 rounded-full text-sm font-medium transition-all duration-200
                      ${selectedRole === role.title 
                        ? 'bg-[#1B4D3E] text-white shadow-lg shadow-[#1B4D3E]/20' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}
                  `}
                  >
                    {role.title}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Chat Messages */}
          <Card className="flex-1 overflow-hidden rounded-2xl border-gray-100 bg-gray-50">
            <div className="h-full overflow-y-auto p-5 space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.role === "assistant" && (
                      <div className="w-9 h-9 rounded-xl bg-[#1B4D3E] flex items-center justify-center shrink-0">
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    )}
                    
                    <div className={`max-w-[80%] ${message.role === "user" ? "order-first" : ""}`}>
                      <div className={`p-4 rounded-2xl ${
                        message.role === "user" 
                          ? "bg-[#1B4D3E] text-white rounded-br-md" 
                          : "bg-white border border-gray-100 shadow-sm text-gray-700 rounded-bl-md"
                      }`}>
                        <div className="text-sm leading-relaxed">
                          {formatMessage(message.content)}
                        </div>
                      </div>
                      
                      {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {message.suggestedQuestions.map((q, i) => (
                            <motion.button
                              key={i}
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                              onClick={() => handleSuggestedQuestion(q)}
                              className="text-xs px-3 py-1.5 rounded-full bg-[#C5E500]/20 text-[#1B4D3E] hover:bg-[#C5E500]/30 transition-colors font-medium"
                            >
                              {q}
                            </motion.button>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    {message.role === "user" && (
                      <div className="w-9 h-9 rounded-xl bg-[#C5E500] flex items-center justify-center shrink-0">
                        <User className="w-5 h-5 text-[#1B4D3E]" />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="w-9 h-9 rounded-xl bg-[#1B4D3E] flex items-center justify-center shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white border border-gray-100 shadow-sm p-4 rounded-2xl rounded-bl-md">
                    <div className="flex gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#1B4D3E] animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 rounded-full bg-[#1B4D3E] animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 rounded-full bg-[#1B4D3E] animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </Card>

          {/* Input Area */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl border border-gray-100 p-3 shadow-lg"
          >
            <div className="flex gap-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                placeholder={selectedRole ? `Ask about ${selectedRole}...` : "Ask me anything about careers..."}
                className="flex-1 h-12 border-0 bg-gray-50 rounded-xl focus:ring-2 focus:ring-[#1B4D3E]/20 text-sm"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="h-12 px-5 bg-[#1B4D3E] hover:bg-[#163d32] text-white rounded-xl disabled:opacity-50 transition-all"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
            
            {/* Quick Action Chips */}
            <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-400">Quick actions:</span>
              {[
                { icon: BookOpen, label: "Learning path" },
                { icon: Lightbulb, label: "Career tips" },
                { icon: MessageCircle, label: "Interview prep" },
              ].map((action, i) => (
                <button
                  key={i}
                  onClick={() => setInput(`Tell me about ${action.label.toLowerCase()} for ${selectedRole || "my career"}`)}
                  className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600 hover:bg-[#1B4D3E]/10 hover:text-[#1B4D3E] transition-colors"
                >
                  <action.icon className="w-3 h-3" />
                  {action.label}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
}
