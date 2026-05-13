import React from "react";
import slashLogo from "@/assets/vermeg-slash.png";
import { cn } from "@/lib/utils";

interface VermegAnimatedLogoProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: { slash: "h-8", fontPx: 24, gapPx: 8 },
  md: { slash: "h-12", fontPx: 38, gapPx: 12 },
  lg: { slash: "h-20", fontPx: 60, gapPx: 16 },
};

const VISION_RED = "oklch(0.58 0.22 27)";

export function VermegAnimatedLogo({ size = "md", className = "" }: VermegAnimatedLogoProps) {
  const s = sizeMap[size];
  return (
    <div className={cn("vermeg-logo flex items-center", className)}>
      <img src={slashLogo} alt="logVision" className={`${s.slash} w-auto vermeg-logo-slash`} />
      <div className="vermeg-logo-text-wrap relative" style={{ marginLeft: s.gapPx }}>
        <span
          className="vermeg-logo-text font-bold tracking-tight inline-block whitespace-nowrap"
          style={{ fontSize: s.fontPx, lineHeight: 1 }}
        >
          <span className="text-foreground">log</span>
          <span style={{ color: VISION_RED }}>Vision</span>
        </span>
      </div>
    </div>
  );
}

export default VermegAnimatedLogo;
import { cn } from "@/lib/utils";

type VermegAnimatedLogoProps = {
  size?: "sm" | "md" | "lg";
  className?: string;
};

const sizeMap = {
  sm: { slash: "h-8", fontPx: 24, gapPx: 8 },
  md: { slash: "h-12", fontPx: 38, gapPx: 12 },
  lg: { slash: "h-20", fontPx: 60, gapPx: 16 },
};

const VISION_RED = "oklch(0.58 0.22 27)";

export function VermegAnimatedLogo({ size = "md", className = "" }: VermegAnimatedLogoProps) {
  const s = sizeMap[size];
  return (
    <div className={cn("vermeg-logo flex items-center", className)}>
      <img src="/assets/vermeg-slash-clean.png" alt="logVision" className={`${s.slash} w-auto vermeg-logo-slash`} />
      <div className="vermeg-logo-text-wrap relative" style={{ marginLeft: `${s.gapPx}px` }}>
        <span
          className="vermeg-logo-text font-bold tracking-tight inline-block whitespace-nowrap"
          style={{ fontSize: `${s.fontPx}px`, lineHeight: 1 }}
        >
          <span className="text-foreground">log</span>
          <span style={{ color: VISION_RED }}>Vision</span>
        </span>
      </div>
    </div>
  );
}
