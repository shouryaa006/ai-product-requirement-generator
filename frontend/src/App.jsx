import { useEffect, useState } from "react";

import AppShell from "./components/layout/AppShell";
import Dashboard from "./pages/Dashboard";
import PRDResult from "./components/prd/PRDResult";

function App() {
  const [prdResult, setPrdResult] = useState(null);
  const [page, setPage] = useState("overview");

  const handlePRDGenerated = (result) => {
    setPrdResult(result);
    setPage("prd");
  };

  const handleBackToDashboard = () => {
    setPrdResult(null);
    setPage("overview");
  };

  useEffect(() => {
    function handleNavigation(event) {
      const destination = event.detail;

      if (destination === "overview") {
        setPrdResult(null);
        setPage("overview");
        return;
      }

      if (destination === "new-prd") {
        setPrdResult(null);
        setPage("overview");

        // Give Dashboard time to render, then focus textarea
        setTimeout(() => {
          const textarea = document.querySelector(".idea-box textarea");

          if (textarea) {
            textarea.focus();
            textarea.scrollIntoView({
              behavior: "smooth",
              block: "center",
            });
          }
        }, 100);

        return;
      }

      // These currently show a simple placeholder.
      // We can build proper pages later if needed.
      setPage(destination);
      setPrdResult(null);
    }

    window.addEventListener("prd:navigate", handleNavigation);

    return () => {
      window.removeEventListener("prd:navigate", handleNavigation);
    };
  }, []);

  function renderContent() {
    if (page === "overview") {
      return (
        <Dashboard
          onPRDGenerated={handlePRDGenerated}
        />
      );
    }

    if (page === "prd" && prdResult) {
      return (
        <PRDResult
          result={prdResult}
          onBack={handleBackToDashboard}
        />
      );
    }

    if (page === "documents") {
      return (
        <div className="dashboard">
          <section className="welcome-section">
            <div>
              <div className="section-eyebrow">
                <span className="eyebrow-line" />
                DOCUMENTS
              </div>

              <h1>Documents</h1>

              <p>
                Your generated product requirement documents will appear here.
              </p>
            </div>
          </section>
        </div>
      );
    }

    if (page === "recent") {
      return (
        <div className="dashboard">
          <section className="welcome-section">
            <div>
              <div className="section-eyebrow">
                <span className="eyebrow-line" />
                LIBRARY
              </div>

              <h1>Recent PRDs</h1>

              <p>
                Recently generated product requirement documents.
              </p>
            </div>
          </section>
        </div>
      );
    }

    if (page === "templates") {
      return (
        <div className="dashboard">
          <section className="welcome-section">
            <div>
              <div className="section-eyebrow">
                <span className="eyebrow-line" />
                LIBRARY
              </div>

              <h1>Templates</h1>

              <p>
                PRD templates will be available here.
              </p>
            </div>
          </section>
        </div>
      );
    }

    if (page === "settings") {
      return (
        <div className="dashboard">
          <section className="welcome-section">
            <div>
              <div className="section-eyebrow">
                <span className="eyebrow-line" />
                SETTINGS
              </div>

              <h1>Settings</h1>

              <p>
                Workspace and AI engine settings will appear here.
              </p>
            </div>
          </section>
        </div>
      );
    }

    if (page === "help") {
      return (
        <div className="dashboard">
          <section className="welcome-section">
            <div>
              <div className="section-eyebrow">
                <span className="eyebrow-line" />
                SUPPORT
              </div>

              <h1>Help & feedback</h1>

              <p>
                Need help with PRD AI? This section is ready for support
                information.
              </p>
            </div>
          </section>
        </div>
      );
    }

    if (page === "profile") {
      return (
        <div className="dashboard">
          <section className="welcome-section">
            <div>
              <div className="section-eyebrow">
                <span className="eyebrow-line" />
                ACCOUNT
              </div>

              <h1>Shourya</h1>

              <p>
                Workspace owner
              </p>
            </div>
          </section>
        </div>
      );
    }

    return (
      <Dashboard
        onPRDGenerated={handlePRDGenerated}
      />
    );
  }

  return (
    <AppShell>
      {renderContent()}
    </AppShell>
  );
}

export default App;