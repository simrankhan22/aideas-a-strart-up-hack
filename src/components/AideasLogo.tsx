import { cn } from "@/lib/utils";

interface AideasLogoProps {
  className?: string;
  size?: number;
}

export function AideasLogo({ className, size = 32 }: AideasLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("text-primary", className)}
      aria-hidden
    >
      {/* Outer ring */}
      <circle cx="20" cy="20" r="18" stroke="currentColor" strokeWidth="1.5" opacity="0.25" />
      {/* Inner orbital arc */}
      <path
        d="M6 20 A14 14 0 0 1 34 20"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.5"
      />
      {/* Spark / idea bulb */}
      <path
        d="M20 10 L22.5 17.5 L30 20 L22.5 22.5 L20 30 L17.5 22.5 L10 20 L17.5 17.5 Z"
        fill="currentColor"
      />
      {/* Center dot */}
      <circle cx="20" cy="20" r="2" fill="hsl(var(--background))" />
    </svg>
  );
}
