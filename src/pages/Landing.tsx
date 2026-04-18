import { useEffect } from "react";
import { Link } from "react-router-dom";
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
  Star,
  Zap,
} from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Deep web research",
    desc: "AIdeas scans the web, regulatory sites, news, and public records to build a complete intel brief on your startup’s landscape.",
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
    desc: "When a meeting is needed, AIdeas handles the back-and-forth and puts it on your calendar. You just show up.",
  },
];

const steps = [
  {
    n: "01",
    title: "Tell AIdeas about your startup",
    desc: "Drop in your company name, what you’re building, and where you operate. That’s it.",
  },
  {
    n: "02",
    title: "AIdeas goes to work",
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
  { icon: Building2, label: "Built for founders dealing with regulators, partners, and officials" },
];

const testimonials = [
  {
    quote: "AIdeas mapped every regulator we needed and booked three intro calls in 48 hours. It would’ve taken us a month.",
    name: "Priya Shah",
    role: "Founder, Lendline",
  },
  {
    quote: "The compliance brief alone saved us a $25K legal bill. The fact that it actually picks up the phone is wild.",
    name: "Marcus Lee",
    role: "CEO, Northwind Health",
  },
  {
    quote: "Felt like hiring a full-time chief of staff on day one. Cleanest research workflow I’ve used.",
    name: "Ana Ribeiro",
    role: "Co-founder, Trellis AI",
  },
];

export default function Landing() {
  useEffect(() => {
    document.title = "AIdeas — AI Research & Outreach Agent for Startups";
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Nav */}
      <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/70 backdrop-blur-xl">
        <div className="container flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary text-primary-foreground shadow-glow">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-display text-lg font-bold tracking-tight">AIdeas</span>
          </Link>
          <nav className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How it works</a>
            <a href="#testimonials" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
          </nav>
          <Button asChild size="sm" className="bg-gradient-primary border-0 text-primary-foreground hover:opacity-90 shadow-soft">
            <Link to="/get-started">Get started</Link>
          </Button>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          {/* Background blobs */}
          <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute -top-24 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-gradient-primary opacity-20 blur-3xl animate-float-slow" />
            <div className="absolute top-40 -left-32 h-80 w-80 rounded-full bg-primary/20 blur-3xl animate-float-slow" style={{ animationDelay: "-4s" }} />
            <div className="absolute top-20 -right-32 h-80 w-80 rounded-full bg-[hsl(280_85%_65%/0.18)] blur-3xl animate-float-slow" style={{ animationDelay: "-8s" }} />
          </div>

          <div className="container relative py-20 sm:py-28 lg:py-32">
            <div className="mx-auto max-w-3xl text-center">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-3 py-1 text-xs text-muted-foreground backdrop-blur shadow-soft">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                Now in private beta — invite-only
              </div>
              <h1 className="font-display text-4xl font-bold leading-[1.05] tracking-tight text-foreground sm:text-6xl lg:text-7xl">
                Your AI agent for{" "}
                <span className="text-gradient">research & outreach</span>
              </h1>
              <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
                Tell AIdeas about your startup. It researches the web, contacts the right officials,
                collects critical information, and books your meetings — automatically.
              </p>
              <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Button asChild size="lg" className="gap-2 w-full sm:w-auto bg-gradient-primary border-0 text-primary-foreground hover:opacity-95 shadow-glow text-base h-12 px-7">
                  <Link to="/get-started">Get started <ArrowRight className="h-4 w-4" /></Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="w-full sm:w-auto h-12 px-7 text-base">
                  <a href="#how">See how it works</a>
                </Button>
              </div>
              <p className="mt-5 text-xs text-muted-foreground">No credit card · Free to try · 2-minute setup</p>
            </div>

            {/* Visual mock */}
            <div className="mx-auto mt-20 max-w-4xl">
              <div className="relative">
                <div aria-hidden className="absolute -inset-4 -z-10 rounded-[2rem] bg-gradient-primary opacity-20 blur-2xl" />
                <div className="rounded-2xl border border-border bg-card/90 p-2 shadow-glow backdrop-blur">
                  <div className="rounded-xl bg-gradient-soft p-6 sm:p-10">
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-foreground text-background">
                          <span className="text-xs font-semibold">You</span>
                        </div>
                        <div className="flex-1 rounded-2xl rounded-tl-sm border border-border bg-background p-4 text-left shadow-soft">
                          <p className="text-sm leading-relaxed">
                            Research compliance requirements for launching a fintech in Singapore. Contact the relevant MAS officials and book an intro call.
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                          <Sparkles className="h-4 w-4" />
                        </div>
                        <div className="flex-1 space-y-3 rounded-2xl rounded-tl-sm border border-border bg-background p-4 text-left shadow-soft">
                          <p className="text-sm leading-relaxed">
                            Compiled a 12-page brief on MAS licensing tiers. Identified 3 relevant officials. Sent intro emails. Booked a call with the Senior Officer for Tue 10:00 SGT.
                          </p>
                          <div className="flex flex-wrap gap-2 pt-1">
                            <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2.5 py-1 text-xs font-medium text-success">
                              <Check className="h-3 w-3" /> Brief ready
                            </span>
                            <span className="inline-flex items-center gap-1 rounded-full bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground">
                              3 contacts found
                            </span>
                            <span className="inline-flex items-center gap-1 rounded-full bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground">
                              <CalendarCheck className="h-3 w-3" /> 1 meeting booked
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Benefits strip */}
        <section className="border-y border-border bg-gradient-soft">
          <div className="container grid gap-6 py-12 sm:grid-cols-3">
            {benefits.map((b) => (
              <div key={b.label} className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-background text-primary shadow-soft">
                  <b.icon className="h-4 w-4" />
                </div>
                <p className="pt-1.5 text-sm font-medium text-foreground">{b.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section id="features" className="container py-24 sm:py-32">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
              <Zap className="h-3 w-3" /> What AIdeas does
            </div>
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-5xl">
              An autonomous teammate for the <span className="text-gradient">critical work</span>
            </h2>
            <p className="mt-5 text-lg text-muted-foreground">
              AIdeas handles the research, outreach, and coordination founders normally lose weeks to —
              and gives you back clean, structured results.
            </p>
          </div>

          <div className="mt-16 grid gap-6 sm:grid-cols-2">
            {features.map((f) => (
              <div
                key={f.title}
                className="group relative overflow-hidden rounded-2xl border border-border bg-card p-7 shadow-card transition-all duration-300 hover:-translate-y-1 hover:shadow-glow hover:border-primary/30"
              >
                <div aria-hidden className="absolute -top-12 -right-12 h-32 w-32 rounded-full bg-gradient-primary opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-30" />
                <div className="relative">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
                    <f.icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-6 font-display text-xl font-semibold">{f.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="relative border-t border-border bg-gradient-soft">
          <div className="container py-24 sm:py-32">
            <div className="mx-auto max-w-2xl text-center">
              <div className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-background px-3 py-1 text-xs font-medium text-primary shadow-soft">
                How it works
              </div>
              <h2 className="font-display text-3xl font-bold tracking-tight sm:text-5xl">
                From idea to <span className="text-gradient">booked meeting</span><br className="hidden sm:block" /> in three steps
              </h2>
            </div>

            <div className="mx-auto mt-16 grid max-w-5xl gap-6 md:grid-cols-3">
              {steps.map((s, i) => (
                <div key={s.n} className="relative rounded-2xl border border-border bg-card p-7 shadow-card">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground font-display text-base font-bold shadow-glow">
                    {s.n}
                  </div>
                  <h3 className="mt-6 font-display text-lg font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
                  {i < steps.length - 1 && (
                    <ArrowRight className="absolute -right-3 top-1/2 hidden h-5 w-5 -translate-y-1/2 text-primary md:block" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="container py-24 sm:py-32">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
              <Star className="h-3 w-3 fill-current" /> Loved by founders
            </div>
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-5xl">
              Real founders, real <span className="text-gradient">time saved</span>
            </h2>
          </div>

          <div className="mt-16 grid gap-6 md:grid-cols-3">
            {testimonials.map((t) => (
              <figure key={t.name} className="relative rounded-2xl border border-border bg-card p-7 shadow-card">
                <div className="mb-4 flex gap-0.5 text-warning">
                  {[0, 1, 2, 3, 4].map((i) => <Star key={i} className="h-4 w-4 fill-current" />)}
                </div>
                <blockquote className="text-sm leading-relaxed text-foreground">“{t.quote}”</blockquote>
                <figcaption className="mt-5 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-primary font-display text-sm font-semibold text-primary-foreground">
                    {t.name.split(" ").map((n) => n[0]).join("")}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.role}</p>
                  </div>
                </figcaption>
              </figure>
            ))}
          </div>
        </section>

        {/* Final CTA */}
        <section className="container pb-24 sm:pb-32">
          <div className="relative overflow-hidden rounded-3xl border border-border bg-gradient-primary p-10 text-center shadow-glow sm:p-16">
            <div aria-hidden className="absolute inset-0 bg-dots opacity-20" />
            <div className="relative">
              <h2 className="font-display text-3xl font-bold tracking-tight text-primary-foreground sm:text-5xl">
                Ready to put AIdeas to work?
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-base text-primary-foreground/85 sm:text-lg">
                Tell us about your startup and get a complete research & outreach brief in minutes.
              </p>
              <div className="mt-8 flex justify-center">
                <Button asChild size="lg" className="gap-2 h-12 px-8 bg-background text-foreground hover:bg-background/90 text-base">
                  <Link to="/get-started">Get started for free <ArrowRight className="h-4 w-4" /></Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className="container flex flex-col items-center justify-between gap-4 py-10 text-sm text-muted-foreground sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-primary text-primary-foreground">
              <Sparkles className="h-3.5 w-3.5" />
            </div>
            <span className="font-display font-semibold text-foreground">AIdeas</span>
            <span>· © {new Date().getFullYear()}</span>
          </div>
          <p>An AI agent for founders.</p>
        </div>
      </footer>
    </div>
  );
}
