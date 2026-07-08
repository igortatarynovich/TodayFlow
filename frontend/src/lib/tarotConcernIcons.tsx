import type { LucideIcon } from "lucide-react";
import {
  Briefcase,
  Compass,
  Heart,
  Home,
  Leaf,
  Sparkles,
  Wallet,
  Zap,
  Bird,
} from "lucide-react";
import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";

const CONCERN_ICONS: Record<TarotConcernDomain, LucideIcon> = {
  relationships: Heart,
  work: Briefcase,
  money: Wallet,
  family: Home,
  growth: Leaf,
  decision: Compass,
  conflict: Zap,
  inner_state: Bird,
  other: Sparkles,
};

export function TarotConcernIcon({
  domain,
  size = 20,
  strokeWidth = 1.5,
  className,
}: {
  domain: TarotConcernDomain;
  size?: number;
  strokeWidth?: number;
  className?: string;
}) {
  const Icon = CONCERN_ICONS[domain];
  return <Icon size={size} strokeWidth={strokeWidth} className={className} aria-hidden />;
}
