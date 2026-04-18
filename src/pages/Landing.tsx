import { useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { AideasLogo } from "@/components/AideasLogo";
import {
  Globe2,
  Users,
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
    icon: Globe2,
    title: "Market & Landscape Research",
    desc: "AIdeas scans the web, regulatory filings, news, and public records to build a complete intel brief on your startup's landscape.",
    cta: "Run research",
  },
  {
    icon: Users,
    title: "Contacts",
    desc: "Identifies the relevant officials, agencies, and decision-makers — then reaches out on your behalf with the right context.",
    cta: "Find contacts",
  },
  {
    icon: CalendarCheck,
    title: "Bookings",
    desc: "When a meeting is needed, AIdeas handles the back-and-forth and puts it on your calendar. You just show up.",
    cta: "Book meetings",
  },
];

const steps = [
  {
    n: "01",
    title: "Tell AIdeas about your startup",
    desc: "Drop in your company name, what you're building, and where you operate. That's it.",
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
  { icon: ShieldCheck, label: "Sources cited on every fact — never guess what's real" },
  { icon: Building2, label: "Built for founders dealing with regulators, partners, and officials" },
];

const testimonials = [
  {
    quote: "AIdeas mapped every regulator we needed and booked three intro calls in 48 hours. It would've taken us a month.",
    name: "Priya Shah",
    role: "Founder, Lendline",
  },
  {
    quote: "The compliance brief alone saved us a $25K legal bill. The fact that it actually picks up the phone is wild.",
    name: "Marcus Lee",
    role: "CEO, Northwind Health",
  },
  {
    quote: "Felt like hiring a full-time chief of staff on day one. Cleanest research workflow I've used.",
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
      <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="container flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <AideasLogo size={30} />
            <span className="font-display text-lg font-bold tracking-tight">AIdeas</span>
          </Link>
          <nav className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How it works</a>
            <a href="#testimonials" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
          </nav>
          <Button asChild size="sm" className="shadow-soft">
            <Link to="/get-started">Get started</Link>
          </Button>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          {/* Light effects background */}
          <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute inset-0 bg-spotlight" />
            <div className="absolute inset-0 bg-grid opacity-60" />
            {/* Soft floating light orbs */}
            <div className="absolute -top-24 left-1/2 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-primary/15 blur-3xl animate-float-slow" />
            <div className="absolute top-40 -left-24 h-72 w-72 rounded-full bg-primary/10 blur-3xl animate-pulse-glow" />
            <div className="absolute top-32 -right-24 h-80 w-80 rounded-full bg-primary/10 blur-3xl animate-float-slow" style={{ animationDelay: "-6s" }} />
            {/* Vertical light beam */}
            <div className="absolute top-0 left-1/2 h-96 w-px -translate-x-1/2 bg-gradient-to-b from-primary/40 to-transparent" />
            <div className="absolute top-0 left-1/2 h-96 w-32 -translate-x-1/2 light-beam opacity-60" />
            {/* Bottom fade */}
            <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-background to-transparent" />
          </div>

          <div className="container relative py-20 sm:py-28 lg:py-32">
            <div className="mx-auto max-w-3xl text-center">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-3 py-1 text-xs text-muted-foreground backdrop-blur shadow-soft">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                Now in private beta — invite-only
              </div>
              <h1 className="font-display text-4xl font-bold leading-[1.05] tracking-tight text-foreground sm:text-6xl lg:text-7xl">
                Your AI agent for{" "}
                <span className="relative inline-block text-primary">
                  research & outreach
                  <span aria-hidden className="absolute -inset-x-2 -inset-y-1 -z-10 rounded-lg bg-primary/10 blur-xl" />
                </span>
              </h1>
              <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
                Tell AIdeas about your startup. It researches the web, contacts the right officials,
                collects critical information, and books your meetings — automatically.
              </p>
              <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Button asChild size="lg" className="gap-2 w-full sm:w-auto shadow-light text-base h-12 px-7">
                  <Link to="/get-started">Get started <ArrowRight className="h-4 w-4" /></Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="w-full sm:w-auto h-12 px-7 text-base bg-card/60 backdrop-blur">
                  <a href="#how">See how it works</a>
                </Button>
              </div>
              <p className="mt-5 text-xs text-muted-foreground">No credit card · Free to try · 2-minute setup</p>
            </div>

            {/* Visual mock */}
            <div className="mx-auto mt-20 max-w-4xl">
              <div className="relative">
                <div aria-hidden className="absolute -inset-6 -z-10 rounded-[2rem] bg-primary/10 blur-3xl" />
                <div className="rounded-2xl border border-border bg-card/95 p-2 shadow-spotlight backdrop-blur">
                  <div className="rounded-xl bg-background p-6 sm:p-10 border border-border/60">
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-foreground text-background">
                          <span className="text-xs font-semibold">You</span>
                        </div>
                        <div className="flex-1 rounded-2xl rounded-tl-sm border border-border bg-secondary/60 p-4 text-left">
                          <p className="text-sm leading-relaxed">
                            Research compliance requirements for launching a fintech in Singapore. Contact the relevant MAS officials and book an intro call.
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-light">
                          <Sparkles className="h-4 w-4" />
                          <span aria-hidden className="absolute inset-0 rounded-xl bg-primary/40 blur-md -z-10 animate-pulse-glow" />
                        </div>
                        <div className="flex-1 space-y-3 rounded-2xl rounded-tl-sm border border-border bg-card p-4 text-left shadow-soft">
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
        <section className="border-y border-border bg-secondary/40">
          <div className="container grid gap-6 py-12 sm:grid-cols-3">
            {benefits.map((b) => (
              <div key={b.label} className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-background text-primary shadow-soft border border-border">
                  <b.icon className="h-4 w-4" />
                </div>
                <p className="pt-1.5 text-sm font-medium text-foreground">{b.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section id="features" className="relative container py-24 sm:py-32">
          {/* Subtle light effect */}
          <div aria-hidden className="pointer-events-none absolute top-1/2 left-1/2 -z-10 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-3xl" />

          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
              <Zap className="h-3 w-3" /> What AIdeas does
            </div>
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-5xl">
              An autonomous teammate for the{" "}
              <span className="relative inline-block text-primary">
                critical work
                <span aria-hidden className="absolute -inset-x-2 -inset-y-1 -z-10 rounded-lg bg-primary/10 blur-xl" />
              </span>
            </h2>
            <p className="mt-5 text-lg text-muted-foreground">
              AIdeas handles the research, outreach, and coordination founders normally lose weeks to —
              and gives you back clean, structured results.
            </p>
          </div>

          <div className="mt-16 grid gap-6 md:grid-cols-3">
            {features.map((f) => (
              <div
                key={f.title}
                className="group relative overflow-hidden rounded-2xl border border-border bg-card p-7 shadow-card transition-all duration-300 hover:-translate-y-1 hover:shadow-light hover:border-primary/40"
              >
                <div aria-hidden className="absolute -top-16 -right-16 h-40 w-40 rounded-full bg-primary/10 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />
                <div className="relative flex h-full flex-col">
                  <div className="relative inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary border border-primary/20">
                    <f.icon className="h-5 w-5" />
                    <span aria-hidden className="absolute inset-0 rounded-xl bg-primary/20 blur-md opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                  <h3 className="mt-6 font-display text-xl font-semibold">{f.title}</h3>
                  <p className="mt-2 flex-1 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                  <Button asChild variant="outline" size="sm" className="mt-6 w-full group-hover:border-primary/40 group-hover:bg-primary/5">
                    <Link to="/get-started" className="gap-2">
                      {f.cta} <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="relative border-t border-border bg-secondary/30 overflow-hidden">
          <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute top-0 left-1/4 h-64 w-64 rounded-full bg-primary/8 blur-3xl animate-pulse-glow" />
            <div className="absolute bottom-0 right-1/4 h-64 w-64 rounded-full bg-primary/8 blur-3xl animate-pulse-glow" style={{ animationDelay: "-2s" }} />
          </div>
          <div className="container py-24 sm:py-32">
            <div className="mx-auto max-w-2xl text-center">
              <div className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-background px-3 py-1 text-xs font-medium text-primary shadow-soft border border-border">
                How it works
              </div>
              <h2 className="font-display text-3xl font-bold tracking-tight sm:text-5xl">
                From idea to{" "}
                <span className="relative inline-block text-primary">
                  booked meeting
                  <span aria-hidden className="absolute -inset-x-2 -inset-y-1 -z-10 rounded-lg bg-primary/10 blur-xl" />
                </span>
                <br className="hidden sm:block" /> in three steps
              </h2>
            </div>

            <div className="mx-auto mt-16 grid max-w-5xl gap-6 md:grid-cols-3">
              {steps.map((s, i) => (
                <div key={s.n} className="relative rounded-2xl border border-border bg-card p-7 shadow-card">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary border border-primary/20 font-display text-base font-bold">
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
              Real founders, real{" "}
              <span className="relative inline-block text-primary">
                time saved
                <span aria-hidden className="absolute -inset-x-2 -inset-y-1 -z-10 rounded-lg bg-primary/10 blur-xl" />
              </span>
            </h2>
          </div>

          <div className="mt-16 grid gap-6 md:grid-cols-3">
            {testimonials.map((t) => (
              <figure key={t.name} className="relative rounded-2xl border border-border bg-card p-7 shadow-card transition-all hover:shadow-light hover:border-primary/30">
                <div className="mb-4 flex gap-0.5 text-warning">
                  {[0, 1, 2, 3, 4].map((i) => <Star key={i} className="h-4 w-4 fill-current" />)}
                </div>
                <blockquote className="text-sm leading-relaxed text-foreground">"{t.quote}"</blockquote>
                <figcaption className="mt-5 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary border border-primary/20 font-display text-sm font-semibold">
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
          <div className="relative overflow-hidden rounded-3xl border border-border bg-card p-10 text-center shadow-spotlight sm:p-16">
            {/* Light effects */}
            <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
              <div className="absolute inset-0 bg-dots opacity-50" />
              <div className="absolute -top-20 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-primary/20 blur-3xl animate-pulse-glow" />
              <div className="absolute top-0 left-1/2 h-64 w-px -translate-x-1/2 bg-gradient-to-b from-primary/50 to-transparent" />
            </div>
            <div className="relative">
              <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20 shadow-light">
                <AideasLogo size={28} />
              </div>
              <h2 className="font-display text-3xl font-bold tracking-tight text-foreground sm:text-5xl">
                Ready to put AIdeas to work?
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-base text-muted-foreground sm:text-lg">
                Tell us about your startup and get a complete research & outreach brief in minutes.
              </p>
              <div className="mt-8 flex justify-center">
                <Button asChild size="lg" className="gap-2 h-12 px-8 text-base shadow-light">
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
            <AideasLogo size={24} />
            <span className="font-display font-semibold text-foreground">AIdeas</span>
            <span>· © {new Date().getFullYear()}</span>
          </div>
          <p>An AI agent for founders.</p>
        </div>
      </footer>
    </div>
  );
}
