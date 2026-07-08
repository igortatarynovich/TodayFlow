"use client";

interface AccountOvalSectionProps {
  title: string;
  showContent: boolean;
  transitionDelay?: string;
}

export function AccountOvalSection({ title, showContent, transitionDelay = "0.2s" }: AccountOvalSectionProps) {
  return (
    <section 
      className="orbit-account-section orbit-account-oval"
      style={{
        opacity: showContent ? 1 : 0,
        transform: showContent ? "translateY(0)" : "translateY(30px)",
        transition: `opacity 0.8s ease ${transitionDelay}, transform 0.8s ease ${transitionDelay}`
      }}
    >
      <div className="orbit-account-oval-content">
        <h2 className="orbit-display-sm">{title}</h2>
      </div>
    </section>
  );
}

