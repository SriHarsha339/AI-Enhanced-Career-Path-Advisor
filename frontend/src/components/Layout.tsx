import { Link, useLocation } from "wouter";
import { Compass, History, MessageCircle, LogOut, User, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Layout({ children }: { children: React.ReactNode }) {
  const [location, setLocation] = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const navItems = [
    { href: "/discover", label: "Discover", icon: Compass },
    { href: "/chat", label: "Chat", icon: MessageCircle },
    { href: "/history", label: "History", icon: History },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Header - Prometheus Style */}
      <motion.header 
        className="sticky top-0 z-50 w-full bg-white border-b border-gray-100"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="container flex h-16 items-center justify-between px-6 md:px-8 max-w-7xl mx-auto">
          <Link href="/" className="flex items-center gap-3 group">
            <motion.div 
              className="flex items-center gap-2"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="w-8 h-8 rounded-lg bg-[#1B4D3E] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-[#C5E500]" />
              </div>
              <span className="text-lg font-semibold text-[#1B4D3E]">
                PathFinder
              </span>
            </motion.div>
          </Link>
          
          <div className="flex items-center gap-6">
            {/* Navigation Links */}
            <nav className="hidden md:flex items-center gap-8">
              {navItems.map((item) => {
                const isActive = location === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "text-sm font-medium transition-colors duration-200",
                      isActive 
                        ? "text-[#1B4D3E]" 
                        : "text-gray-600 hover:text-[#1B4D3E]"
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            {/* Mobile Nav */}
            <nav className="flex md:hidden items-center gap-1">
              {navItems.map((item) => {
                const isActive = location === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "p-2.5 rounded-full transition-all duration-200",
                      isActive 
                        ? "bg-[#1B4D3E] text-white" 
                        : "text-gray-500 hover:bg-gray-100"
                    )}
                  >
                    <Icon className="h-5 w-5" />
                  </Link>
                );
              })}
            </nav>

            <div className="flex items-center gap-3">
              {/* Auth Section */}
              {isAuthenticated ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="gap-2 rounded-full hover:bg-gray-100 text-gray-700 h-10 px-4">
                      <div className="w-8 h-8 rounded-full bg-[#1B4D3E] flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                      <span className="hidden sm:inline font-medium">{user?.name}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="rounded-2xl border-gray-200 shadow-xl w-56 p-2">
                    <DropdownMenuItem disabled className="text-gray-400 text-sm rounded-xl">
                      {user?.email}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="bg-gray-100" />
                    <DropdownMenuItem onClick={() => setLocation("/history")} className="gap-3 rounded-xl cursor-pointer hover:bg-gray-50">
                      <History className="h-4 w-4 text-[#1B4D3E]" />
                      My History
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="bg-gray-100" />
                    <DropdownMenuItem onClick={logout} className="text-red-600 gap-3 rounded-xl cursor-pointer hover:bg-red-50">
                      <LogOut className="h-4 w-4" />
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <>
                  <Button 
                    variant="ghost" 
                    className="text-gray-700 hover:text-[#1B4D3E] hover:bg-transparent font-medium"
                    onClick={() => setLocation("/login")}
                  >
                    Log In
                  </Button>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button 
                      className="rounded-full bg-[#1B4D3E] hover:bg-[#153D32] text-white h-10 px-6 font-medium shadow-lg shadow-[#1B4D3E]/20"
                      onClick={() => setLocation("/register")}
                    >
                      Sign Up Now
                    </Button>
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer - Prometheus Style */}
      <footer className="bg-[#1B4D3E] text-white py-16 mt-auto">
        <div className="container max-w-7xl mx-auto px-6 md:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-[#C5E500]" />
                </div>
                <span className="text-lg font-semibold">PathFinder</span>
              </div>
              <p className="text-white/60 text-sm leading-relaxed">
                AI-powered career recommendations to help you find your perfect path.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white/90">Support</h4>
              <ul className="space-y-3 text-sm text-white/60">
                <li className="hover:text-white cursor-pointer transition-colors">Support Center</li>
                <li className="hover:text-white cursor-pointer transition-colors">FAQs</li>
                <li className="hover:text-white cursor-pointer transition-colors">Feedback</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white/90">Products</h4>
              <ul className="space-y-3 text-sm text-white/60">
                <li className="hover:text-white cursor-pointer transition-colors">Career Discovery</li>
                <li className="hover:text-white cursor-pointer transition-colors">AI Chat</li>
                <li className="hover:text-white cursor-pointer transition-colors">Roadmaps</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white/90">Resources</h4>
              <ul className="space-y-3 text-sm text-white/60">
                <li className="hover:text-white cursor-pointer transition-colors">Documentation</li>
                <li className="hover:text-white cursor-pointer transition-colors">Tutorials</li>
                <li className="hover:text-white cursor-pointer transition-colors">Blog</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white/90">Company</h4>
              <ul className="space-y-3 text-sm text-white/60">
                <li className="hover:text-white cursor-pointer transition-colors">About Us</li>
                <li className="hover:text-white cursor-pointer transition-colors">Careers</li>
                <li className="hover:text-white cursor-pointer transition-colors">Contact</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-white/50 text-sm">
              © {new Date().getFullYear()} PathFinder. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm text-white/50">
              <span className="hover:text-white cursor-pointer transition-colors">Privacy Policy</span>
              <span className="hover:text-white cursor-pointer transition-colors">Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
