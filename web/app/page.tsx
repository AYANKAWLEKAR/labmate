"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

const INSTITUTIONS = [
  "Rutgers",
  "NJIT",
  "Princeton",
  "Stevens Institute of Technology",
  "TCNJ",
  "Seton Hall",
];

interface Professor {
  id: string;
  name: string;
  institution: string;
  department: string;
  research_focus: string;
  lab_group?: string | null;
  profile_url?: string | null;
}

interface MatchResult {
  resume_profile: {
    skills: string[];
    interests: string[];
    experiences: string[];
  };
  top_professors: Professor[];
}

export default function HomePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [selectedInstitutions, setSelectedInstitutions] = useState<string[]>([]);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [selectedProfessor, setSelectedProfessor] = useState<Professor | null>(null);
  const [generatedEmail, setGeneratedEmail] = useState<string | null>(null);
  const [userName, setUserName] = useState("");
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  // Redirect to sign-in if unauthenticated (use useEffect to avoid calling during render)
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin");
    }
  }, [status, router]);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (status === "unauthenticated") {
    return null;
  }

  const toggleInstitution = (institution: string) => {
    setSelectedInstitutions((prev) =>
      prev.includes(institution)
        ? prev.filter((i) => i !== institution)
        : [...prev, institution]
    );
  };

  const handleMatch = async () => {
    if (!resumeFile || selectedInstitutions.length === 0) {
      setError("Please select a resume and at least one institution");
      return;
    }

    setLoadingMatch(true);
    setError(null);
    setMatchResult(null);
    setSelectedProfessor(null);
    setGeneratedEmail(null);

    try {
      const formData = new FormData();
      formData.append("resume", resumeFile);

      const institutionsParam = selectedInstitutions
        .map((inst) => `institutions=${encodeURIComponent(inst)}`)
        .join("&");

      const response = await fetch(
        `${apiBase}/match?${institutionsParam}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to match professors");
      }

      const data: MatchResult = await response.json();
      setMatchResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoadingMatch(false);
    }
  };

  const handleGenerateEmail = async () => {
    if (!selectedProfessor || !matchResult || !userName) {
      setError("Please select a professor and enter your name");
      return;
    }

    setLoadingEmail(true);
    setError(null);

    try {
      const response = await fetch(`${apiBase}/generate_email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_profile: matchResult.resume_profile,
          professor: selectedProfessor,
          user_name: userName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate email");
      }

      const data = await response.json();
      setGeneratedEmail(data.email_text);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoadingEmail(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4 py-8">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">Labmate</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-300">{session?.user?.email}</span>
            <button
              onClick={() => signOut({ callbackUrl: "/auth/signin" })}
              className="rounded-md bg-slate-700 px-4 py-2 text-sm text-white hover:bg-slate-600"
            >
              Sign out
            </button>
          </div>
        </header>

        {error && (
          <div className="mb-6 rounded-lg border border-red-500/50 bg-red-500/20 p-4 text-red-200">
            {error}
          </div>
        )}

        <section className="mb-8 rounded-xl border border-slate-700 bg-slate-800/50 p-6 shadow-lg">
          <h2 className="mb-4 text-xl font-semibold text-white">
            Step 1: Upload Resume & Select Institutions
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Resume (PDF)
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="mt-1 block w-full text-sm text-slate-300 file:mr-4 file:rounded-md file:border-0 file:bg-sky-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-sky-700"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Select Institutions
              </label>
              <div className="flex flex-wrap gap-2">
                {INSTITUTIONS.map((institution) => (
                  <button
                    key={institution}
                    type="button"
                    onClick={() => toggleInstitution(institution)}
                    className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                      selectedInstitutions.includes(institution)
                        ? "bg-sky-600 text-white"
                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    {institution}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={handleMatch}
              disabled={!resumeFile || selectedInstitutions.length === 0 || loadingMatch}
              className="w-full rounded-md bg-sky-600 px-4 py-2 font-semibold text-white shadow-sm hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            >
              {loadingMatch ? "Finding matches..." : "Find my top 3 professors"}
            </button>
          </div>
        </section>

        {matchResult && (
          <section className="mb-8 rounded-xl border border-slate-700 bg-slate-800/50 p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-semibold text-white">
              Step 2: Select a Professor
            </h2>
            <div className="grid gap-4 md:grid-cols-3">
              {matchResult.top_professors.map((prof) => (
                <button
                  key={prof.id}
                  type="button"
                  onClick={() => {
                    setSelectedProfessor(prof);
                    setGeneratedEmail(null);
                  }}
                  className={`rounded-lg border p-4 text-left transition ${
                    selectedProfessor?.id === prof.id
                      ? "border-sky-500 bg-sky-500/20"
                      : "border-slate-600 bg-slate-700/50 hover:border-slate-500"
                  }`}
                >
                  <h3 className="font-semibold text-white">{prof.name}</h3>
                  <p className="mt-1 text-sm text-slate-300">{prof.department}</p>
                  <p className="mt-1 text-xs text-slate-400">{prof.institution}</p>
                  <p className="mt-2 text-xs text-slate-300 line-clamp-3">
                    {prof.research_focus}
                  </p>
                  {prof.profile_url && (
                    <p className="mt-2 text-xs text-sky-400">View profile →</p>
                  )}
                </button>
              ))}
            </div>

            {selectedProfessor && (
              <div className="mt-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300">
                    Your name
                  </label>
                  <input
                    type="text"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    placeholder="How should we sign the email?"
                    className="mt-1 w-full rounded-md border border-slate-600 bg-slate-700/50 px-3 py-2 text-white placeholder-slate-400 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleGenerateEmail}
                  disabled={!userName || loadingEmail}
                  className="w-full rounded-md bg-sky-600 px-4 py-2 font-semibold text-white shadow-sm hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
                >
                  {loadingEmail ? "Generating email..." : "Generate cold email"}
                </button>
              </div>
            )}
          </section>
        )}

        {generatedEmail && (
          <section className="rounded-xl border border-slate-700 bg-slate-800/50 p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-semibold text-white">Generated Email</h2>
            <pre className="whitespace-pre-wrap rounded-lg bg-slate-900/80 p-4 text-sm text-slate-100">
              {generatedEmail}
            </pre>
          </section>
        )}
      </div>
    </div>
  );
}

