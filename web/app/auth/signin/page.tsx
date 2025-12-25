"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCredentialsSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    if (result?.error) {
      setError("Invalid email or password");
      setLoading(false);
    } else {
      router.push("/");
    }
  };

  const handleGitHubSignIn = async () => {
    await signIn("github", { callbackUrl: "/" });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4">
      <div className="w-full max-w-md space-y-8 rounded-xl border border-slate-700 bg-slate-800/50 p-8 shadow-2xl">
        <div>
          <h1 className="text-center text-3xl font-bold text-white">Labmate</h1>
          <p className="mt-2 text-center text-sm text-slate-400">
            Sign in to find research opportunities
          </p>
        </div>

        {error && (
          <div className="rounded-md bg-red-500/20 border border-red-500/50 p-3 text-sm text-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleCredentialsSignIn} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-slate-600 bg-slate-700/50 px-3 py-2 text-white placeholder-slate-400 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-slate-600 bg-slate-700/50 px-3 py-2 text-white placeholder-slate-400 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-sky-600 px-4 py-2 font-semibold text-white shadow-sm hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-600"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-slate-800/50 px-2 text-slate-400">Or continue with</span>
          </div>
        </div>

        <button
          onClick={handleGitHubSignIn}
          className="w-full rounded-md border border-slate-600 bg-slate-700/50 px-4 py-2 font-semibold text-white shadow-sm hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-slate-800"
        >
          Continue with GitHub
        </button>
      </div>
    </div>
  );
}

