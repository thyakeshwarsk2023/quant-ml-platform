import { useEffect, useRef, useState } from "react";
import { ResponsiveContainer } from "recharts";

export default function SafeResponsiveContainer({
  children,
  height = "100%",
  minHeight = 120,
  className = "",
}) {
  const ref = useRef(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const element = ref.current;
    if (!element) {
      return undefined;
    }

    const updateSize = () => {
      const rect = element.getBoundingClientRect();
      setSize({
        width: Math.floor(rect.width),
        height: Math.floor(rect.height),
      });
    };

    updateSize();

    if (typeof ResizeObserver === "undefined") {
      window.addEventListener("resize", updateSize);
      return () => window.removeEventListener("resize", updateSize);
    }

    const observer = new ResizeObserver(updateSize);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const hasLayout = size.width > 0 && size.height > 0;
  const safeWidth = Math.max(1, size.width);
  const safeHeight = Math.max(minHeight, size.height);

  return (
    <div
      ref={ref}
      className={`w-full min-w-0 ${className}`}
      style={{ height, minHeight }}
    >
      {hasLayout ? (
        <ResponsiveContainer
          width={safeWidth}
          height={safeHeight}
          minWidth={1}
          minHeight={minHeight}
          debounce={50}
        >
          {children}
        </ResponsiveContainer>
      ) : (
        <div className="h-full min-h-[inherit] flex items-center justify-center text-[10px] font-mono text-terminal-muted">
          Preparing chart...
        </div>
      )}
    </div>
  );
}
