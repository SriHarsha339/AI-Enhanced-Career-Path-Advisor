import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { Loader2, UserPlus, Eye, EyeOff, Sparkles, ArrowRight } from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { registerSchema, type RegisterInput } from "@shared/schema";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export default function Register() {
  const [, setLocation] = useLocation();
  const { register: registerUser } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  async function onSubmit(data: RegisterInput) {
    setIsLoading(true);
    try {
      await registerUser(data.name, data.email, data.password);
      toast({
        title: "Account created!",
        description: "Welcome to Career Recommender. Your journey begins now.",
      });
      setLocation("/");
    } catch (error: any) {
      toast({
        title: "Registration failed",
        description: error.message || "Could not create account. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Layout>
      <div className="min-h-screen bg-white flex items-center justify-center py-12 relative overflow-hidden">
        
        {/* Subtle Background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-[#C5E500]/10 to-transparent rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-gradient-to-tr from-[#1B4D3E]/5 to-transparent" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-md px-4 relative z-10"
        >
          <Card className="border border-gray-100 shadow-xl rounded-3xl overflow-hidden bg-white">
            {/* Accent Bar */}
            <div className="h-1.5 bg-gradient-to-r from-[#C5E500] via-[#1B4D3E]/80 to-[#1B4D3E]" />
            
            <CardHeader className="text-center space-y-4 pt-8 pb-2">
              <motion.div 
                className="mx-auto bg-[#C5E500]/20 p-4 rounded-2xl w-fit"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.1 }}
              >
                <Sparkles className="h-8 w-8 text-[#1B4D3E]" />
              </motion.div>
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900">Create Account</CardTitle>
                <CardDescription className="text-gray-500 mt-2">
                  Join PathFinder to save your history and get personalized insights
                </CardDescription>
              </div>
            </CardHeader>
            
            <CardContent className="px-8 pt-4">
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-700">Full Name</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="John Doe" 
                            className="h-12 bg-gray-50 border-gray-200 rounded-xl hover:bg-white hover:border-[#1B4D3E]/30 focus:border-[#1B4D3E] focus:ring-[#1B4D3E]/20 transition-colors"
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-700">Email</FormLabel>
                        <FormControl>
                          <Input 
                            type="email" 
                            placeholder="you@example.com" 
                            className="h-12 bg-gray-50 border-gray-200 rounded-xl hover:bg-white hover:border-[#1B4D3E]/30 focus:border-[#1B4D3E] focus:ring-[#1B4D3E]/20 transition-colors"
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-700">Password</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="••••••••"
                              className="h-12 bg-gray-50 border-gray-200 rounded-xl hover:bg-white hover:border-[#1B4D3E]/30 focus:border-[#1B4D3E] focus:ring-[#1B4D3E]/20 transition-colors pr-12"
                              {...field}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4 text-gray-400" />
                              ) : (
                                <Eye className="h-4 w-4 text-gray-400" />
                              )}
                            </Button>
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="confirmPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-gray-700">Confirm Password</FormLabel>
                        <FormControl>
                          <Input
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            className="h-12 bg-gray-50 border-gray-200 rounded-xl hover:bg-white hover:border-[#1B4D3E]/30 focus:border-[#1B4D3E] focus:ring-[#1B4D3E]/20 transition-colors"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
                    <Button 
                      type="submit" 
                      className="w-full h-12 bg-[#1B4D3E] hover:bg-[#163d32] text-white rounded-xl text-base font-semibold shadow-lg shadow-[#1B4D3E]/20 transition-all duration-300" 
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating account...
                        </>
                      ) : (
                        <>
                          <UserPlus className="mr-2 h-4 w-4" />
                          Create Account
                        </>
                      )}
                    </Button>
                  </motion.div>
                </form>
              </Form>
            </CardContent>

            <CardFooter className="flex flex-col gap-4 px-8 pb-8 pt-2">
              <div className="relative w-full">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-400">
                    Or
                  </span>
                </div>
              </div>

              <div className="text-center text-sm text-gray-600">
                Already have an account?{" "}
                <Button 
                  variant="ghost" 
                  className="p-0 h-auto font-semibold text-[#1B4D3E] hover:text-[#163d32] hover:bg-transparent underline-offset-4 hover:underline"
                  onClick={() => setLocation("/login")}
                >
                  Sign in
                </Button>
              </div>

              <Button 
                variant="ghost" 
                className="text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-xl"
                onClick={() => setLocation("/discover")}
              >
                Continue as guest
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardFooter>
          </Card>
        </motion.div>
      </div>
    </Layout>
  );
}
