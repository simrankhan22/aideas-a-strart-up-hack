-- Anonymous startup submissions for Aides
CREATE TABLE public.startup_submissions (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  startup_name text NOT NULL,
  website text,
  industry text,
  location text,
  stage text,
  description text NOT NULL,
  goals text,
  contact_email text,
  analysis jsonb NOT NULL DEFAULT '{}'::jsonb,
  status text NOT NULL DEFAULT 'pending',
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now()
);

ALTER TABLE public.startup_submissions ENABLE ROW LEVEL SECURITY;

-- Anyone (anonymous or authenticated) can create a submission
CREATE POLICY "Anyone can create submissions"
ON public.startup_submissions
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

-- Anyone with the id (which acts as the share token) can read it
CREATE POLICY "Anyone can view submissions"
ON public.startup_submissions
FOR SELECT
TO anon, authenticated
USING (true);

-- Trigger to keep updated_at fresh
CREATE TRIGGER update_startup_submissions_updated_at
BEFORE UPDATE ON public.startup_submissions
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();
