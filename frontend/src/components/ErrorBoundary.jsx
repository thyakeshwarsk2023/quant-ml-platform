import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("UI boundary caught an error", {
      message: error?.message,
      stack: error?.stack,
      componentStack: info?.componentStack,
    });
  }

  render() {
    if (this.state.error) {
      return (
        <div className="terminal-shell min-h-screen flex items-center justify-center px-4">
          <div className="terminal-panel max-w-lg w-full p-5">
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-terminal-negative">
              Application Error
            </p>
            <h1 className="mt-2 text-lg font-semibold text-terminal-text">
              The dashboard hit a rendering fault.
            </h1>
            <p className="mt-2 text-sm text-terminal-muted">
              Refresh the page. If this repeats, check the console for the
              captured component stack.
            </p>
            <button
              type="button"
              className="terminal-btn mt-4"
              onClick={() => window.location.reload()}
            >
              Reload
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
