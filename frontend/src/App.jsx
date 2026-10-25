import { useEffect, useRef, useState } from "react";
import {
  Activity, ArrowDownRight, ArrowUpRight, Bot, Check, ChevronDown,
  CircleHelp, Clock3, Command, Droplets, ExternalLink, FlaskConical,
  Gauge, Globe2, Leaf, LoaderCircle, Menu, MessageSquareText, Plus,
  RefreshCw, Send, ShieldCheck, Sparkles, Waves, X, Zap
} from "lucide-react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const suggestions = [
  { icon: Droplets, title: "Groundwater overview", prompt: "Give me a groundwater overview for Uttar Pradesh." },
  { icon: Activity, title: "Extraction analysis", prompt: "Explain groundwater extraction and recharge for a district." },
  { icon: ArrowUpRight, title: "Compare resources", prompt: "How should I compare groundwater recharge and extraction?" },
  { icon: FlaskConical, title: "Understand categories", prompt: "Explain groundwater assessment categories in simple terms." }
];

function BrandMark() {
  return <div className="brand-mark"><Waves size={22} strokeWidth={2.2} /></div>;
}

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const inputRef = useRef(null);
  const responseRef = useRef(null);

  async function checkApi() {
    try {
      const res = await fetch(`${API_BASE}/`, { method: "GET" });
      if (!res.ok) throw new Error("API unavailable");
      setApiStatus("online");
    } catch {
      setApiStatus("offline");
    }
  }

  useEffect(() => {
    checkApi();
  }, []);

  useEffect(() => {
    if (response && responseRef.current) {
      responseRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [response]);

  async function askQuestion(question = query) {
    const clean = question.trim();
    if (!clean || loading) return;

    setLoading(true);
    setError("");
    setResponse("");
    setSubmittedQuery(clean);
    setQuery(clean);

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: clean })
      });

      const payload = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(payload.detail || `Request failed (${res.status})`);
      }

      const answer = payload.response || "The API returned an empty response.";
      setResponse(answer);
      setHistory(prev => [
        { query: clean, response: answer, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) },
        ...prev.filter(item => item.query !== clean)
      ].slice(0, 8));
      setApiStatus("online");
    } catch (err) {
      setError(
        `${err.message || "Unable to connect to the backend."} Check that FastAPI is running at ${API_BASE} and that CORS allows this frontend origin.`
      );
      setApiStatus("offline");
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    setQuery("");
    setResponse("");
    setSubmittedQuery("");
    setError("");
    inputRef.current?.focus();
    setSidebarOpen(false);
  }

  function loadHistory(item) {
    setQuery(item.query);
    setSubmittedQuery(item.query);
    setResponse(item.response);
    setError("");
    setSidebarOpen(false);
  }

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <BrandMark />
          <div className="brand-copy">
            <span className="brand-name">Aqua<span>Intel</span></span>
            <span className="brand-caption">GROUNDWATER AI ANALYST</span>
          </div>
          <button className="icon-button mobile-close" onClick={() => setSidebarOpen(false)} aria-label="Close menu"><X size={18}/></button>
        </div>

        <button className="new-chat-button" onClick={startNewChat}>
          <Plus size={17} />
          <span>New analysis</span>
          <span className="shortcut"><Command size={11}/> K</span>
        </button>

        <div className="nav-label">WORKSPACE</div>
        <button className="nav-item active" onClick={startNewChat}>
          <MessageSquareText size={17} />
          <span>AI analyst</span>
          <span className="nav-dot" />
        </button>
        <button className="nav-item" onClick={() => setShowAbout(true)}>
          <Gauge size={17} />
          <span>How it works</span>
        </button>
        <button className="nav-item" onClick={() => inputRef.current?.focus()}>
          <CircleHelp size={17} />
          <span>Ask a question</span>
        </button>

        <div className="history-heading">
          <span className="nav-label">RECENT ANALYSIS</span>
          {history.length > 0 && <span className="history-count">{history.length}</span>}
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <div className="history-empty">
              <Clock3 size={15} />
              <span>Your recent questions will appear here.</span>
            </div>
          ) : history.map((item, index) => (
            <button className="history-item" key={`${item.query}-${index}`} onClick={() => loadHistory(item)}>
              <MessageSquareText size={15} />
              <span>{item.query}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="data-card">
            <div className="data-card-icon"><ShieldCheck size={17}/></div>
            <div>
              <strong>Data-conscious AI</strong>
              <p>Verify important figures against official sources.</p>
            </div>
          </div>
          <div className="profile-row">
            <div className="profile-avatar">GA</div>
            <div className="profile-copy"><strong>Groundwater Analyst</strong><span>Workspace</span></div>
            <button className="icon-button" onClick={() => setShowAbout(true)} aria-label="About"><ChevronDown size={16}/></button>
          </div>
        </div>
      </aside>

      {sidebarOpen && <button className="mobile-scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-button menu-trigger" onClick={() => setSidebarOpen(true)} aria-label="Open menu"><Menu size={19}/></button>
            <div className="breadcrumb">Workspace <span>/</span> <strong>AI Analyst</strong></div>
          </div>
          <div className="topbar-right">
            <div className={`connection-pill ${apiStatus}`}>
              <span className="status-dot" />
              {apiStatus === "checking" ? "Checking API" : apiStatus === "online" ? "API connected" : "API offline"}
            </div>
            <button className="icon-button refresh-button" onClick={checkApi} title="Check API connection" aria-label="Check API connection"><RefreshCw size={16}/></button>
            <div className="topbar-divider" />
            <div className="top-avatar">AI</div>
          </div>
        </header>

        <div className="content-wrap">
          <section className="hero-section">
            <div className="hero-eyebrow"><span className="eyebrow-icon"><Sparkles size={13}/></span> GROUNDWATER INTELLIGENCE, SIMPLIFIED</div>
            <h1>Ask better questions.<br/><span>Understand our water.</span></h1>
            <p className="hero-description">
              Explore groundwater data through natural conversation. Ask about recharge, extraction, water levels, or regional resource status.
            </p>
            <div className="hero-meta">
              <span><ShieldCheck size={14}/> Source-aware analysis</span>
              <span className="meta-separator">·</span>
              <span><Zap size={14}/> Powered by your AI workflow</span>
            </div>
          </section>

          <section className="query-panel">
            <div className="query-panel-top">
              <div className="query-label"><span className="query-pulse" /> YOUR QUESTION</div>
              <span className="input-hint">Natural language works best</span>
            </div>
            <form className="query-form" onSubmit={e => { e.preventDefault(); askQuestion(); }}>
              <textarea
                ref={inputRef}
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    askQuestion();
                  }
                }}
                placeholder="e.g. Explain groundwater extraction in Rajasthan..."
                rows={2}
                aria-label="Ask a groundwater question"
              />
              <div className="query-form-bottom">
                <span className="keyboard-hint"><kbd>↵</kbd> to ask <span>·</span> <kbd>Shift</kbd> + <kbd>↵</kbd> for new line</span>
                <button type="submit" className="send-button" disabled={!query.trim() || loading}>
                  {loading ? <LoaderCircle className="spin" size={16}/> : <Send size={16}/>}
                  <span>{loading ? "Analyzing" : "Analyze question"}</span>
                </button>
              </div>
            </form>
            <div className="privacy-note"><ShieldCheck size={13}/> Answers depend on the data sources configured in the backend. Verify critical decisions against official records.</div>
          </section>

          {!submittedQuery && !loading && (
            <section className="suggestions-section">
              <div className="section-heading">
                <div><span className="section-kicker">GET STARTED</span><h2>What would you like to explore?</h2></div>
                <span className="suggestion-count">04 PROMPTS</span>
              </div>
              <div className="suggestion-grid">
                {suggestions.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <button className={`suggestion-card card-delay-${i}`} key={item.title} onClick={() => { setQuery(item.prompt); askQuestion(item.prompt); }}>
                      <span className="suggestion-icon"><Icon size={18}/></span>
                      <span className="suggestion-title">{item.title}</span>
                      <span className="suggestion-prompt">{item.prompt}</span>
                      <span className="suggestion-arrow"><ArrowDownRight size={16}/></span>
                    </button>
                  );
                })}
              </div>
            </section>
          )}

          {(loading || submittedQuery || error) && (
            <section className="answer-section" ref={responseRef}>
              <div className="answer-section-heading">
                <div className="answer-heading-icon"><Bot size={18}/></div>
                <div><span className="section-kicker">ANALYSIS RESULT</span><h2>Groundwater assistant</h2></div>
                {response && <span className="answer-ready"><span/> RESPONSE READY</span>}
              </div>
              {submittedQuery && (
                <div className="submitted-question">
                  <div className="question-marker"><MessageSquareText size={15}/></div>
                  <div><span className="mini-label">YOUR QUESTION</span><p>{submittedQuery}</p></div>
                </div>
              )}
              {loading && (
                <div className="loading-card">
                  <div className="loading-orb"><Droplets size={22}/></div>
                  <div className="loading-copy"><strong>Analyzing groundwater information</strong><span>Interpreting your question and waiting for the backend response…</span></div>
                  <div className="loading-bars"><i/><i/><i/><i/></div>
                </div>
              )}
              {error && !loading && (
                <div className="error-card">
                  <div className="error-icon"><Activity size={19}/></div>
                  <div><strong>We couldn't complete this request</strong><p>{error}</p><button className="text-action" onClick={() => askQuestion(submittedQuery)}><RefreshCw size={14}/> Try again</button></div>
                </div>
              )}
              {response && !loading && (
                <div className="response-card">
                  <div className="response-card-top"><div className="response-avatar"><Bot size={17}/></div><div><strong>AI-generated response</strong><span>Review the source and context for important decisions.</span></div><button className="copy-button" onClick={() => navigator.clipboard?.writeText(response)} title="Copy response"><span>Copy answer</span><ExternalLink size={13}/></button></div>
                  <div className="response-body">{response}</div>
                  <div className="response-footer"><span><ShieldCheck size={14}/> Check figures against official records</span><button onClick={startNewChat}><Plus size={14}/> New analysis</button></div>
                </div>
              )}
            </section>
          )}

          <footer className="page-footer">
            <div className="footer-brand"><BrandMark/><span>AquaIntel <i>·</i> Groundwater AI Analyst</span></div>
            <span className="footer-note">Built for clearer groundwater insights</span>
          </footer>
        </div>
      </main>

      {showAbout && (
        <div className="modal-backdrop" onClick={() => setShowAbout(false)}>
          <section className="about-modal" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="about-title">
            <button className="modal-close icon-button" onClick={() => setShowAbout(false)} aria-label="Close dialog"><X size={18}/></button>
            <div className="modal-icon"><Waves size={23}/></div>
            <span className="section-kicker">ABOUT THIS WORKSPACE</span>
            <h2 id="about-title">Groundwater insights, in plain language.</h2>
            <p>This interface sends your question to the FastAPI <code>/analyze</code> endpoint. Your LangGraph workflow is responsible for processing the query and returning the response.</p>
            <div className="modal-info-row"><ShieldCheck size={17}/><span>The UI does not independently verify groundwater figures or sources.</span></div>
            <div className="modal-info-row"><Globe2 size={17}/><span>Configure the backend URL with <code>VITE_API_BASE_URL</code> when deploying.</span></div>
            <button className="modal-primary" onClick={() => setShowAbout(false)}>Got it <Check size={16}/></button>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
