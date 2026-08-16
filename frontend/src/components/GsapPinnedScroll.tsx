"use client";

import React, { useEffect, useRef } from "react";
import gsap from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface Props {
  children: React.ReactNode[];
}

export default function GsapPinnedScroll({ children }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // In React 18 strict mode, useEffect runs twice. gsap.context helps clean up.
    const ctx = gsap.context(() => {
      const panels = gsap.utils.toArray(".gsap-panel") as HTMLElement[];
      
      panels.forEach((panel, i) => {
        ScrollTrigger.create({
          trigger: panel,
          start: "top top",
          pin: true,
          pinSpacing: false
        });
      });

      let maxScroll = 0;
      
      const pageScrollTrigger = ScrollTrigger.create({
        snap(value) {
          const snappedValue = gsap.utils.snap(1 / panels.length, value);
          if (snappedValue <= 0) {
            return 1.05 / maxScroll;
          } else if (snappedValue >= 1) {
            return maxScroll / (maxScroll + 1.05);
          }
          return snappedValue;
        }
      });

      function onResize() {
        maxScroll = ScrollTrigger.maxScroll(window) - 1;
      }
      onResize();
      window.addEventListener("resize", onResize);

      const onScroll = (e: Event) => {
        const scroll = pageScrollTrigger.scroll();
        if (maxScroll > 0) {
          if (scroll > maxScroll) {
            pageScrollTrigger.scroll(1);
            e.preventDefault();
          } else if (scroll < 1) {
            pageScrollTrigger.scroll(maxScroll - 1);
            e.preventDefault();
          }
        }
      };

      window.addEventListener("scroll", onScroll, { passive: false });

      return () => {
        window.removeEventListener("resize", onResize);
        window.removeEventListener("scroll", onScroll);
      };
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const childrenArray = React.Children.toArray(children);
  const firstChild = childrenArray[0];

  return (
    <div ref={containerRef} className="gsap-container">
      {childrenArray.map((child, i) => (
        <section 
          className="gsap-panel" 
          key={`panel-${i}`} 
          style={{ 
            minHeight: "100vh", 
            width: "100%", 
            position: "relative", 
            backgroundColor: "#000",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden" // ensures content doesn't bleed out of the pinned panel
          }}
        >
          <div style={{ width: "100%", height: "100%", padding: "6rem 2rem", boxSizing: "border-box", overflowY: "auto", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
            {child}
          </div>
        </section>
      ))}
      {/* Clone the first panel for infinite looping */}
      <section 
        className="gsap-panel" 
        key="panel-copy" 
        style={{ 
          minHeight: "100vh", 
          width: "100%", 
          position: "relative", 
          backgroundColor: "#000",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden"
        }}
      >
        <div style={{ width: "100%", height: "100%", padding: "6rem 2rem", boxSizing: "border-box", overflowY: "auto", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          {firstChild}
        </div>
      </section>
    </div>
  );
}
