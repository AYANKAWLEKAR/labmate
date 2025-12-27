"use client";


import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FlaskConical, Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";

export default function SignUpPage() {
    // #region agent log
    if (typeof window !== 'undefined') {
        fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'signup/page.tsx:14',message:'Component mounted',data:{userAgent:navigator.userAgent,url:window.location.href},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
        const testEl = document.createElement('div');
        testEl.className = 'bg-background text-foreground';
        const computed = window.getComputedStyle(testEl);
        const bgValue = computed.backgroundColor;
        const textValue = computed.color;
        const cssVars = {
            background: getComputedStyle(document.documentElement).getPropertyValue('--background'),
            foreground: getComputedStyle(document.documentElement).getPropertyValue('--foreground'),
            primary: getComputedStyle(document.documentElement).getPropertyValue('--primary')
        };
        fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'signup/page.tsx:25',message:'CSS variables check',data:{cssVars,bgValue,textValue,hasTailwind:document.querySelector('style[data-next-hide-fouc]')!==null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    }
    // #endregion
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            setLoading(false);
            return;
        }
        
        try {
            const response = await fetch("/api/auth/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to sign up");
            }
            
            const data = await response.json();
            console.log(data.message);
            router.push("/auth/signin");
        } catch (error) {
            console.error(error);
            setError(error instanceof Error ? error.message : "Failed to sign up");
            setLoading(false);
        }
    }
    // #region agent log
    if (typeof window !== 'undefined') {
        const layoutCssUrl = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).find(l => (l as HTMLLinkElement).href?.includes('layout.css')) as HTMLLinkElement | undefined;
        if (layoutCssUrl?.href) {
            fetch(layoutCssUrl.href).then(r => r.text()).then(css => {
                const hasTailwindDirectives = css.includes('@tailwind') || css.includes('tailwind');
                const hasBgBackground = css.includes('.bg-background') || css.includes('bg-background');
                const hasMinHScreen = css.includes('.min-h-screen');
                const cssLength = css.length;
                const sampleCss = css.substring(0, 500);
                fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'signup/page.tsx:57',message:'CSS file content analysis',data:{layoutCssUrl,hasTailwindDirectives,hasBgBackground,hasMinHScreen,cssLength,sampleCss},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
            }).catch(e => {
                fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'signup/page.tsx:57',message:'Failed to fetch CSS',data:{error:String(e)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
            });
        }
    }
    // #endregion
    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
          <Card className="w-full max-w-md shadow-lg border-border" data-testid="signup-card">
            <CardHeader className="space-y-4 text-center pb-2">
              {/* Logo and Branding */}
              <div className="flex justify-center">
                <div className="p-3 rounded-full bg-primary/10">
                  <FlaskConical className="h-8 w-8 text-primary" />
                </div>
              </div>
              <div className="space-y-1">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                  Labmate
                </h1>
                <p className="text-sm text-muted-foreground">
                  Find your next research experience
                </p>
              </div>
              <div className="pt-2">
                <h2 className="text-xl font-semibold text-foreground">
                  Create your account
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Join thousands of researchers worldwide
                </p>
              </div>
            </CardHeader>
    
            <CardContent className="pt-4">
              <form onSubmit={handleSignUp} className="space-y-4">
                {/* Error Message */}
                {error && (
                  <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20">
                    <p className="text-sm text-destructive font-medium">{error}</p>
                  </div>
                )}
    
                {/* Email Input */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-foreground">
                    Email address
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>
    
                {/* Password Input */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-foreground">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10"
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
    
                {/* Confirm Password Input */}
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-foreground">
                    Confirm password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="pl-10 pr-10"
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      tabIndex={-1}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
    
                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full font-medium"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating account...
                    </>
                  ) : (
                    "Create Account"
                  )}
                </Button>
              </form>
            </CardContent>
    
            <CardFooter className="justify-center pt-2 pb-6">
              <p className="text-sm text-muted-foreground">
                Already have an account? Or Sign Up with Google or Github{" "}
                <Link
                  href="/auth/signin"
                  className="font-medium text-primary hover:underline"
                >
                  Sign in
                </Link>
              </p>
            </CardFooter>
          </Card>
        </div>
      );
    // #region agent log
    if (typeof window !== 'undefined') {
        setTimeout(() => {
            const card = document.querySelector('[data-testid="signup-card"]');
            if (card) {
                const computed = window.getComputedStyle(card);
                fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'signup/page.tsx:210',message:'After render - component styles check',data:{cardExists:!!card,backgroundColor:computed.backgroundColor,color:computed.color,width:computed.width,hasClasses:card.className.includes('Card')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            } else {
                fetch('http://127.0.0.1:7242/ingest/4602107a-e1df-493a-b467-d31eb221ce0f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'signup/page.tsx:210',message:'After render - card not found',data:{cardExists:false},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            }
        }, 100);
    }
    // #endregion

}
