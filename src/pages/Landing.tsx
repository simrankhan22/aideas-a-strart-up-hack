import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Search,
  PhoneCall,
  Database,
  CalendarCheck,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Clock,
  Building2,
  Check,
} from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Deep web research",
    desc: "Aides scans the web, regulatory sites, news, and public records to build a complete intel brief on your startup’s landscape.",
  },
  {
    icon: PhoneCall,
    title: "Calls the right officials",
    desc: "Identifies the relevant officials, agencies, and decision-makers — then reaches out on your behalf with the right context.",
  },
  {
    icon: Database,
    title: "Everything in one place",
    desc: "Notes, transcripts, documents, and contact info are stored in a single, searchable workspace you actually want to use.",
  },
  {
    icon: CalendarCheck,
    title: "Books meetings for you",
    desc: "When a meeting is needed, Aides handles the back-and-forth and puts it on your calendar. You just show up.",
  },
];

const steps = [
  {
    n: "01",
    title: "Tell Aides about your startup",
    desc: "Drop in your company name, what you’re building, and where you operate. That’s it.",
  },
  {
    n: "02",
    title: "Aides goes to work",
    desc: "It researches the market, finds the right officials, and reaches out — calls, emails, forms, the lot.",
  },
  {
    n: "03",
    title: "Get a clean, actionable brief",
    desc: "All findings, contacts, and confirmed bookings land in your workspace. Ready to act on.",
  },
];

const benefits = [
  { icon: Clock, label: "Save 20+ hours per week of manual research and outreach" },
  { icon: ShieldCheck, label: "Sources cited on every fact — never guess what’s real" },
  { icon: Building2, label: "Built for founders dealing with regulators, partners, and gov officials" },
];

export default function Landing() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    document.title = "Aides — AI Research & Outreach Agent for Startups";
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Nav */}
      <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur">
        <div className="container flex h-16 items-center justify-between">
          <a href="#" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-display text-lg font-bold tracking-tight">Aides</span>
          </a>
          <nav className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How it works</a>
            <a href="#waitlist" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Waitlist</a>
          </nav>
          <Button asChild size="sm">
            <a href="#waitlist">Join waitlist</a>
          </Button>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="container relative overflow-hidden py-20 sm:py-28 lg:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-success" />
              Now in private beta
            </div>
            <h1 className="font-display text-4xl font-bold leading-tight tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Your AI research &<br />
              <span className="text-primary">outreach agent</span> for founders
            </h1>
            <p className="mt-6 text-lg text-muted-foreground sm:text-xl">
              Tell Aides about your startup. It researches the web, contacts the right officials,
              collects critical information, and books your meetings — automatically.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button asChild size="lg" className="gap-2 w-full sm:w-auto">
                <a href="#waitlist">Get early access <ArrowRight className="h-4 w-4" /></a>
              </Button>
              <Button asChild size="lg" variant="outline" className="w-full sm:w-auto">
                <a href="#how">See how it works</a>
              </Button>
            </div>
            <p className="mt-4 text-xs text-muted-foreground">No credit card · Onboarded personally</p>
          </div>

          {/* Visual mock */}
          <div className="mx-auto mt-16 max-w-4xl">
            <div className="rounded-2xl border border-border bg-card p-2 shadow-2xl shadow-primary/5">
              <div className="rounded-xl bg-muted/50 p-6 sm:p-10">
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                      <Sparkles className="h-4 w-4" />
                    </div>
                    <div className="flex-1 rounded-lg border border-border bg-background p-4 text-left">
                      <p className="text-xs font-medium text-muted-foreground">You</p>
                      <p className="mt-1 text-sm">Research compliance requirements for launching a fintech in Singapore. Contact the relevant MAS officials and book an intro call.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
                      <Check className="h-4 w-4" />
                    </div>
                    <div className="flex-1 space-y-2 rounded-lg border border-border bg-background p-4 text-left">
                      <p className="text-xs font-medium text-muted-foreground">Aides</p>
                      <p className="text-sm">Compiled 12-page brief on MAS licensing tiers · Identified 3 relevant officials · Sent intro emails · Booked call with Senior Officer for Tue 10:00 SGT.</p>
                      <div className="flex flex-wrap gap-2 pt-1">
                        <span className="rounded-full bg-accent px-2 py-0.5 text-xs text-accent-foreground">Brief ready</span>
                        <span className="rounded-full bg-accent px-2 py-0.5 text-xs text-accent-foreground">3 contacts</span>
                        <span className="rounded-full bg-accent px-2 py-0.5 text-xs text-accent-foreground">1 meeting booked</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Benefits strip */}
        <section className="border-y border-border bg-muted/30">
          <div className="container grid gap-6 py-10 sm:grid-cols-3">
            {benefits.map((b) => (
              <div key={b.label} className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                  <b.icon className="h-4 w-4" />
                </div>
                <p className="text-sm text-foreground">{b.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section id="features" className="container py-20 sm:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-medium text-primary">What Aides does</p>
            <h2 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">
              An autonomous teammate for the boring, critical work
            </h2>
            <p className="mt-4 text-muted-foreground">
              Aides handles the research, outreach, and coordination founders normally lose weeks to —
              and gives you back clean, structured results.
            </p>
          </div>

          <div className="mt-14 grid gap-6 sm:grid-cols-2">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-border bg-card p-6 transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent text-accent-foreground transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 font-display text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="border-t border-border bg-muted/30">
          <div className="container py-20 sm:py-28">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-sm font-medium text-primary">How it works</p>
              <h2 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">
                From idea to booked meeting in three steps
              </h2>
            </div>

            <div className="mt-14 grid gap-6 md:grid-cols-3">
              {steps.map((s) => (
                <div key={s.n} className="rounded-2xl border border-border bg-card p-6">
                  <div className="font-display text-sm font-bold text-primary">{s.n}</div>
                  <h3 className="mt-3 font-display text-lg font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Waitlist CTA */}
        <section id="waitlist" className="container py-20 sm:py-28">
          <div className="mx-auto max-w-2xl rounded-3xl border border-border bg-card p-8 text-center sm:p-14">
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
              Get early access to Aides
            </h2>
            <p className="mt-4 text-muted-foreground">
              We’re onboarding a small group of founders. Drop your email and we’ll reach out personally.
            </p>

            {submitted ? (
              <div className="mx-auto mt-8 flex max-w-md items-center justify-center gap-2 rounded-lg border border-success/30 bg-success/10 p-4 text-success">
                <Check className="h-4 w-4" />
                <span className="text-sm font-medium">You’re on the list. We’ll be in touch soon.</span>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="mx-auto mt-8 flex max-w-md flex-col gap-2 sm:flex-row">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="founder@yourstartup.com"
                  className="flex-1 rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none ring-offset-background transition-shadow focus:ring-2 focus:ring-ring"
                />
                <Button type="submit" size="lg">Join waitlist</Button>
              </form>
            )}
            <p className="mt-3 text-xs text-muted-foreground">We’ll never share your email. Unsubscribe anytime.</p>
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className="container flex flex-col items-center justify-between gap-4 py-8 text-sm text-muted-foreground sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Sparkles className="h-3 w-3" />
            </div>
            <span className="font-display font-semibold text-foreground">Aides</span>
            <span>· © {new Date().getFullYear()}</span>
          </div>
          <p>An AI agent for founders.</p>
        </div>
      </footer>
    </div>
  );
}
