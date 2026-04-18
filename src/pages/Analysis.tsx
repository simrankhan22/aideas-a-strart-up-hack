import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  ArrowLeft,
  Globe,
  MapPin,
  Building2,
  Tag,
  Loader2,
  Search,
  Users,
  ShieldAlert,
  TrendingUp,
  CalendarCheck,
  Copy,
  Check,
  Clock,
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

type Submission = {
  id: string;
  startup_name: string;
  website: string | null;
  industry: string | null;
  location: string | null;
  stage: string | null;
  description: string;
  goals: string | null;
  contact_email: string | null;
  status: string;
  created_at: string;
};

export default function Analysis() {
  const { id } = useParams<{ id: string }>();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    document.title = "Your AIdeas analysis";
  }, []);

  useEffect(() => {
    if (!id) return;
    const load = async () => {
      const { data, error } = await supabase
        .from("startup_submissions")
        .select("id, startup_name, website, industry, location, stage, description, goals, contact_email, status, created_at")
        .eq("id", id)
        .maybeSingle();
      if (error || !data) {
        setNotFound(true);
      } else {
        setSubmission(data as Submission);
      }
      setLoading(false);
    };
    load();
  }, [id]);

  const copyLink = async () => {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    toast.success("Link copied");
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading your analysis…
      </div>
    );
  }

  if (notFound || !submission) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-4 text-center">
        <h1 className="font-display text-2xl font-bold">Analysis not found</h1>
        <p className="text-sm text-muted-foreground">This link may be invalid or removed.</p>
        <Button asChild><Link to="/">Back to home</Link></Button>
      </div>
    );
  }

  const sections = [
    {
      icon: Search,
      title: "Market & landscape research",
      desc: `AIdeas is gathering public data, news, and regulatory filings about ${submission.industry || "your industry"}${submission.location ? ` in ${submission.location}` : ""}.`,
    },
    {
      icon: Users,
      title: "Key officials & contacts",
      desc: "Identifying the regulators, agencies, and decision-makers most relevant to your launch — with verified contact details.",
    },
    {
      icon: ShieldAlert,
      title: "Compliance & risks",
      desc: "Surfacing licensing requirements, common pitfalls, and the questions you’ll be asked before approval.",
    },
    {
      icon: TrendingUp,
      title: "Competitive intelligence",
      desc: "Mapping competitors, recent funding rounds, and positioning gaps in your space.",
    },
    {
      icon: CalendarCheck,
      title: "Outreach & bookings",
      desc: "Drafting personalized outreach to the right officials — and booking the calls that matter.",
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-background/80 backdrop-blur">
        <div className="container flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary text-primary-foreground shadow-glow">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-display text-lg font-bold tracking-tight">AIdeas</span>
          </Link>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={copyLink} className="gap-2">
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copied ? "Copied" : "Share"}
            </Button>
            <Button asChild variant="ghost" size="sm" className="gap-2">
              <Link to="/"><ArrowLeft className="h-4 w-4" /> Home</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="container max-w-4xl py-12 sm:py-16">
        {/* Status banner */}
        <div className="mb-8 flex items-start gap-3 rounded-xl border border-border bg-accent/40 p-4">
          <Clock className="mt-0.5 h-5 w-5 shrink-0 text-accent-foreground" />
          <div>
            <p className="text-sm font-medium text-foreground">Your Aides agents are working on this</p>
            <p className="mt-1 text-sm text-muted-foreground">
              We’ve received your submission. The full research brief, contacts, and bookings will appear here as agents complete their work.
              {submission.contact_email && <> We’ll also send updates to <span className="font-medium text-foreground">{submission.contact_email}</span>.</>}
            </p>
          </div>
        </div>

        {/* Submission summary */}
        <div className="mb-10">
          <p className="text-sm font-medium text-primary">Submission summary</p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">
            {submission.startup_name}
          </h1>

          <div className="mt-4 flex flex-wrap gap-2">
            {submission.industry && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs text-accent-foreground">
                <Tag className="h-3 w-3" /> {submission.industry}
              </span>
            )}
            {submission.location && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs text-accent-foreground">
                <MapPin className="h-3 w-3" /> {submission.location}
              </span>
            )}
            {submission.stage && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs text-accent-foreground">
                <Building2 className="h-3 w-3" /> {submission.stage}
              </span>
            )}
            {submission.website && (
              <a
                href={submission.website.startsWith("http") ? submission.website : `https://${submission.website}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs text-accent-foreground hover:underline"
              >
                <Globe className="h-3 w-3" /> {submission.website}
              </a>
            )}
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-border bg-card p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">What you’re building</p>
              <p className="mt-2 text-sm leading-relaxed text-foreground whitespace-pre-wrap">{submission.description}</p>
            </div>
            {submission.goals && (
              <div className="rounded-xl border border-border bg-card p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">What Aides should accomplish</p>
                <p className="mt-2 text-sm leading-relaxed text-foreground whitespace-pre-wrap">{submission.goals}</p>
              </div>
            )}
          </div>
        </div>

        {/* Analysis sections (placeholders for future agent output) */}
        <div>
          <h2 className="font-display text-2xl font-bold tracking-tight">Detailed analysis</h2>
          <p className="mt-2 text-sm text-muted-foreground">Agents are populating the sections below. Refresh this page to see updates.</p>

          <div className="mt-6 grid gap-4">
            {sections.map((s) => (
              <div key={s.title} className="rounded-2xl border border-border bg-card p-5">
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-accent-foreground">
                    <s.icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="font-display text-base font-semibold">{s.title}</h3>
                      <span className="inline-flex items-center gap-1 rounded-full bg-warning/10 px-2 py-0.5 text-xs font-medium text-warning">
                        <Loader2 className="h-3 w-3 animate-spin" /> In progress
                      </span>
                    </div>
                    <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-10 rounded-2xl border border-border bg-card p-6 text-center sm:p-8">
          <h3 className="font-display text-lg font-semibold">Bookmark this page</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            This URL is your private link to your analysis. Save it — your agents will keep updating this page.
          </p>
          <Button onClick={copyLink} variant="outline" className="mt-4 gap-2">
            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            {copied ? "Link copied" : "Copy link"}
          </Button>
        </div>
      </main>
    </div>
  );
}
