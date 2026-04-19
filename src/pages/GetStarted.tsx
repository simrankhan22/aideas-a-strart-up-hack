import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Sparkles, ArrowLeft, ArrowRight, Loader2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

const schema = z.object({
  startup_name: z.string().trim().min(1, "Required").max(120),
  website: z.string().trim().max(200).optional().or(z.literal("")),
  industry: z.string().trim().max(80).optional().or(z.literal("")),
  location: z.string().trim().min(1, "Current location is required").max(120),
  marketplace: z.string().trim().min(1, "Marketplace is required").max(120),
  stage: z.string().trim().max(60).optional().or(z.literal("")),
  description: z.string().trim().min(20, "Please describe your startup in at least 20 characters").max(2000),
  goals: z.string().trim().max(1000).optional().or(z.literal("")),
  contact_email: z.string().trim().email("Invalid email").max(200).optional().or(z.literal("")),
});

type FormState = z.infer<typeof schema>;

const stages = ["Idea", "Pre-seed", "Seed", "Series A", "Series B+", "Other"];

export default function GetStarted() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<FormState>({
    startup_name: "",
    website: "",
    industry: "",
    location: "",
    marketplace: "",
    stage: "",
    description: "",
    goals: "",
    contact_email: "",
  });
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});

  useEffect(() => {
    document.title = "Get started · AIdeas";
  }, []);

  const update = <K extends keyof FormState>(k: K, v: FormState[K]) => {
    setForm((f) => ({ ...f, [k]: v }));
    if (errors[k]) setErrors((e) => ({ ...e, [k]: undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = schema.safeParse(form);
    if (!parsed.success) {
      const fieldErrors: Partial<Record<keyof FormState, string>> = {};
      parsed.error.issues.forEach((i) => {
        const k = i.path[0] as keyof FormState;
        if (!fieldErrors[k]) fieldErrors[k] = i.message;
      });
      setErrors(fieldErrors);
      return;
    }

    setSubmitting(true);
    const { data, error } = await supabase
      .from("startup_submissions")
      .insert({
        startup_name: parsed.data.startup_name,
        website: parsed.data.website || null,
        industry: parsed.data.industry || null,
        location: parsed.data.location || null,
        marketplace: parsed.data.marketplace || null,
        stage: parsed.data.stage || null,
        description: parsed.data.description,
        goals: parsed.data.goals || null,
        contact_email: parsed.data.contact_email || null,
      })
      .select("id")
      .single();
    setSubmitting(false);

    if (error || !data) {
      toast.error("Could not submit. Please try again.");
      return;
    }
    navigate(`/analysis/${data.id}`);
  };

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
          <Button asChild variant="ghost" size="sm" className="gap-2">
            <Link to="/"><ArrowLeft className="h-4 w-4" /> Back</Link>
          </Button>
        </div>
      </header>

      <main className="container max-w-2xl py-12 sm:py-16">
        <div className="mb-8">
          <p className="text-sm font-medium text-primary">Step 1 of 2</p>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">
            Tell us about your startup
          </h1>
          <p className="mt-3 text-muted-foreground">
            The more context you give AIdeas, the better the research and outreach. This takes about 2 minutes.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl border border-border bg-card p-6 sm:p-8">
          <div className="grid gap-2">
            <Label htmlFor="startup_name">Startup name *</Label>
            <Input
              id="startup_name"
              value={form.startup_name}
              onChange={(e) => update("startup_name", e.target.value)}
              placeholder="Acme AI"
              maxLength={120}
            />
            {errors.startup_name && <p className="text-xs text-destructive">{errors.startup_name}</p>}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                value={form.website}
                onChange={(e) => update("website", e.target.value)}
                placeholder="acme.ai"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="industry">Industry</Label>
              <Input
                id="industry"
                value={form.industry}
                onChange={(e) => update("industry", e.target.value)}
                placeholder="Fintech, Healthtech…"
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="location">Current location</Label>
              <Input
                id="location"
                value={form.location}
                onChange={(e) => update("location", e.target.value)}
                placeholder="Where you're based — e.g. San Francisco, USA"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="marketplace">Marketplace</Label>
              <Input
                id="marketplace"
                value={form.marketplace}
                onChange={(e) => update("marketplace", e.target.value)}
                placeholder="Target market — e.g. Southeast Asia, EU"
              />
            </div>
          </div>

          <div className="grid gap-2 sm:max-w-xs">
            <Label htmlFor="stage">Stage</Label>
            <select
              id="stage"
              value={form.stage}
              onChange={(e) => update("stage", e.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-ring"
            >
              <option value="">Select…</option>
              {stages.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="description">What is your startup building? *</Label>
            <Textarea
              id="description"
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
              placeholder="We're building an AI agent that automates compliance research for fintechs entering new markets…"
              rows={5}
              maxLength={2000}
            />
            {errors.description && <p className="text-xs text-destructive">{errors.description}</p>}
          </div>

          <div className="grid gap-2">
            <Label htmlFor="goals">What do you want AIdeas to research / accomplish?</Label>
            <Textarea
              id="goals"
              value={form.goals}
              onChange={(e) => update("goals", e.target.value)}
              placeholder="Find the right regulators in Singapore for fintech licensing, and book intro calls with the relevant officials."
              rows={4}
              maxLength={1000}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="contact_email">Your email (so we can send you the brief)</Label>
            <Input
              id="contact_email"
              type="email"
              value={form.contact_email}
              onChange={(e) => update("contact_email", e.target.value)}
              placeholder="founder@acme.ai"
            />
            {errors.contact_email && <p className="text-xs text-destructive">{errors.contact_email}</p>}
          </div>

          <Button type="submit" size="lg" className="w-full gap-2" disabled={submitting}>
            {submitting ? <><Loader2 className="h-4 w-4 animate-spin" /> Submitting…</> : <>Generate analysis <ArrowRight className="h-4 w-4" /></>}
          </Button>
        </form>
      </main>
    </div>
  );
}
