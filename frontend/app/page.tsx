"use client";

import { useSession, signOut } from "next-auth/react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, Search, Mail, LogOut, User } from "lucide-react";
import { API_BASE_URL } from "@/lib/utils";

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
  lab_group?: string;
  profile_url?: string;
}

export default function HomePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [selectedInstitutions, setSelectedInstitutions] = useState<string[]>([]);
  const [resumeProfile, setResumeProfile] = useState<any>(null);
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [selectedProfessor, setSelectedProfessor] = useState<Professor | null>(null);
  const [userName, setUserName] = useState("");
  const [emailText, setEmailText] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin");
    }
  }, [status, router]);

  const handleInstitutionToggle = (institution: string) => {
    setSelectedInstitutions((prev) =>
      prev.includes(institution)
        ? prev.filter((i) => i !== institution)
        : [...prev, institution]
    );
  };

  const handleMatch = async () => {
    if (!resumeFile || selectedInstitutions.length === 0) {
      setError("Please upload a resume and select at least one institution");
      return;
    }

    setLoading(true);
    setError(null);
    setEmailText("");
    setSelectedProfessor(null);

    try {
      const formData = new FormData();
      formData.append("resume", resumeFile);
      const institutionsParam = selectedInstitutions
        .map((inst) => `institutions=${encodeURIComponent(inst)}`)
        .join("&");
      const url = `${API_BASE_URL}/match?${institutionsParam}`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          ...(session?.user?.id && { "X-User-Id": session.user.id }),
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get matches");
      }

      const data = await response.json();
      setResumeProfile(data.resume_profile);
      setProfessors(data.top_professors);
    } catch (err: any) {
      setError(err.message || "An error occurred while matching");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateEmail = async () => {
    if (!selectedProfessor || !userName.trim() || !resumeProfile) {
      setError("Please select a professor and enter your name");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/generate_email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_profile: resumeProfile,
          professor: selectedProfessor,
          user_name: userName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate email");
      }

      const data = await response.json();
      setEmailText(data.email_text);
    } catch (err: any) {
      setError(err.message || "An error occurred while generating email");
    } finally {
      setLoading(false);
    }
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Labmate</h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span className="text-sm">{session.user?.email}</span>
            </div>
            <Button variant="outline" onClick={() => signOut()}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Find Your Research Match</h2>
          <p className="text-muted-foreground">
            Upload your resume and discover professors at top institutions who match your research interests.
          </p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-destructive/10 border border-destructive rounded-md text-destructive">
            {error}
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Step 1: Upload Resume</CardTitle>
              <CardDescription>Upload your resume in PDF format</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="resume">Resume (PDF)</Label>
                <Input
                  id="resume"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  className="mt-2"
                />
                {resumeFile && (
                  <p className="text-sm text-muted-foreground mt-2">
                    Selected: {resumeFile.name}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Step 2: Select Institutions</CardTitle>
              <CardDescription>Choose one or more institutions to search</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {INSTITUTIONS.map((institution) => (
                  <label
                    key={institution}
                    className="flex items-center space-x-2 cursor-pointer p-2 rounded hover:bg-accent"
                  >
                    <input
                      type="checkbox"
                      checked={selectedInstitutions.includes(institution)}
                      onChange={() => handleInstitutionToggle(institution)}
                      className="rounded"
                    />
                    <span className="text-sm">{institution}</span>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-6 flex justify-center">
          <Button
            onClick={handleMatch}
            disabled={loading || !resumeFile || selectedInstitutions.length === 0}
            size="lg"
            className="min-w-[200px]"
          >
            {loading ? (
              "Matching..."
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Find My Top 3 Professors
              </>
            )}
          </Button>
        </div>

        {professors.length > 0 && (
          <div className="mt-8">
            <h3 className="text-2xl font-bold mb-4">Your Matches</h3>
            <div className="grid gap-4 md:grid-cols-3">
              {professors.map((professor) => (
                <Card
                  key={professor.id}
                  className={`cursor-pointer transition-all ${
                    selectedProfessor?.id === professor.id
                      ? "ring-2 ring-primary"
                      : "hover:shadow-lg"
                  }`}
                  onClick={() => setSelectedProfessor(professor)}
                >
                  <CardHeader>
                    <CardTitle className="text-lg">{professor.name}</CardTitle>
                    <CardDescription>
                      {professor.institution} • {professor.department}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {professor.research_focus}
                    </p>
                    {professor.profile_url && (
                      <a
                        href={professor.profile_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline mt-2 inline-block"
                        onClick={(e) => e.stopPropagation()}
                      >
                        View Profile →
                      </a>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {selectedProfessor && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Step 3: Generate Cold Email</CardTitle>
              <CardDescription>
                Selected: {selectedProfessor.name} at {selectedProfessor.institution}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="userName">Your Name</Label>
                <Input
                  id="userName"
                  placeholder="Enter your full name"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  className="mt-2"
                />
              </div>
              <Button
                onClick={handleGenerateEmail}
                disabled={loading || !userName.trim()}
                className="w-full"
              >
                {loading ? (
                  "Generating..."
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Generate Cold Email
                  </>
                )}
              </Button>

              {emailText && (
                <div className="mt-4 p-4 bg-muted rounded-md">
                  <pre className="whitespace-pre-wrap text-sm font-mono">
                    {emailText}
                  </pre>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => {
                      navigator.clipboard.writeText(emailText);
                      alert("Email copied to clipboard!");
                    }}
                  >
                    Copy to Clipboard
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
