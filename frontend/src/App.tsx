import { useState, useEffect } from "react";
import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { AppLoader } from "@/components/AppLoader";
import { AnimatePresence } from "framer-motion";
import NotFound from "@/pages/not-found";
import Landing from "@/pages/Landing";
import Home from "@/pages/Home";
import Result from "@/pages/Result";
import History from "@/pages/History";
import CareerChat from "@/pages/CareerChat";
import Login from "@/pages/Login";
import Register from "@/pages/Register";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Landing} />
      <Route path="/discover" component={Home} />
      <Route path="/result/:id" component={Result} />
      <Route path="/history" component={History} />
      <Route path="/chat" component={CareerChat} />
      <Route path="/login" component={Login} />
      <Route path="/register" component={Register} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Show loader on initial load
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2500); // 2.5 seconds for the beautiful animation to play

    return () => clearTimeout(timer);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <AnimatePresence mode="wait">
            {isLoading && <AppLoader isLoading={isLoading} />}
          </AnimatePresence>
          <Toaster />
          <Router />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
