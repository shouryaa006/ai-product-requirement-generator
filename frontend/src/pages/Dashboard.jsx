import { useState } from "react";

import {
  ArrowUpRight,
  FileText,
  Plus,
  Sparkles,
  Clock3,
  CheckCircle2,
  LoaderCircle,
  AlertCircle,
} from "lucide-react";

import { generatePRD } from "../services/api";

/* =========================================================
   RECENT PRDs
   ========================================================= */

const recentPRDs = [
  {
    title: "Tutor Marketplace",
    description: "College students finding verified tutors",
    updated: "2 hours ago",
    progress: 92,

    product_overview:
      "A platform that connects university students with verified peer tutors from their campus. Students can search tutors by course, price, rating, and availability. Tutors can create academic profiles, manage availability, and offer flexible tutoring sessions.",

    problem_statement:
      "University students often struggle to find affordable and course-specific academic support, while high-achieving students lack an effective platform to offer tutoring services.",

    target_users: [
      "University students seeking affordable academic support",
      "High-achieving students interested in peer tutoring",
      "Students looking for course-specific tutoring",
    ],

    business_objectives: [
      "Connect students with verified peer tutors",
      "Make tutoring affordable and accessible",
      "Provide flexible earning opportunities for student tutors",
    ],

    personas: [
      {
        name: "Aisha Patel",
        role: "Second-Year Computer Science Undergraduate",
        goals: [
          "Find affordable academic support",
          "Improve performance in difficult courses",
          "Book sessions around her class schedule",
        ],
        pain_points: [
          "Professional tutors are expensive",
          "University tutoring centers have limited availability",
          "Finding tutors for specific courses is difficult",
        ],
      },
      {
        name: "Marcus Vance",
        role: "Senior Computer Science Major and Peer Tutor",
        goals: [
          "Earn flexible income",
          "Build teaching experience",
          "Manage tutoring availability easily",
        ],
        pain_points: [
          "Difficulty finding students",
          "Manual scheduling is inefficient",
          "Last-minute cancellations",
        ],
      },
    ],

    user_stories: [
      {
        id: "US-001",
        as_a: "student seeking academic help",
        i_want: "search for peer tutors by course and subject",
        so_that: "I can quickly find a suitable tutor",
      },
      {
        id: "US-002",
        as_a: "student looking for a tutor",
        i_want: "view tutor profiles and ratings",
        so_that: "I can compare tutors",
      },
      {
        id: "US-003",
        as_a: "student",
        i_want: "book one-time or recurring tutoring sessions",
        so_that: "I can receive consistent academic support",
      },
      {
        id: "US-004",
        as_a: "peer tutor",
        i_want: "create a verified tutor profile",
        so_that: "students can discover my services",
      },
    ],

    functional_requirements: [
      {
        id: "FR-001",
        description:
          "The system shall validate users using their university email address.",
        priority: "High",
      },
      {
        id: "FR-002",
        description:
          "The system shall allow students to search and filter tutors by course, subject, price, rating, and availability.",
        priority: "High",
      },
      {
        id: "FR-003",
        description:
          "The system shall display detailed tutor profiles including qualifications, courses, rates, ratings, and availability.",
        priority: "High",
      },
      {
        id: "FR-004",
        description:
          "The system shall allow students to book one-time or recurring tutoring sessions.",
        priority: "High",
      },
      {
        id: "FR-005",
        description:
          "The system shall lock booked time slots to prevent double-booking.",
        priority: "High",
      },
    ],

    non_functional_requirements: [
      {
        id: "NFR-001",
        description:
          "The application shall support mobile, tablet, and desktop screen sizes.",
        category: "Usability",
      },
      {
        id: "NFR-002",
        description:
          "The user interface shall comply with WCAG accessibility standards.",
        category: "Accessibility",
      },
      {
        id: "NFR-003",
        description:
          "Authentication credentials shall be securely stored and data transmitted using encryption.",
        category: "Security",
      },
      {
        id: "NFR-004",
        description:
          "Search results should render within two seconds under normal conditions.",
        category: "Performance",
      },
    ],

    risks: [
      "Low tutor adoption for specialized courses",
      "Students arranging tutoring outside the platform",
      "Scheduling disputes and cancellations",
    ],

    assumptions: [
      "Students have active university email accounts",
      "Tutoring sessions can happen on campus or online",
      "University course information remains consistent during the semester",
    ],

    future_enhancements: [
      "Integrated video conferencing",
      "Calendar integration",
      "Group tutoring sessions",
      "Integrated digital payments",
    ],
  },

  {
    title: "Campus Event Platform",
    description: "Discover and manage university events",
    updated: "Yesterday",
    progress: 78,

    product_overview:
      "A centralized platform that allows university students to discover, register for, and manage campus events from one place.",

    problem_statement:
      "Students often miss campus events because event information is spread across different communication channels.",

    target_users: [
      "University students",
      "Student clubs",
      "University event organizers",
    ],

    business_objectives: [
      "Increase campus event participation",
      "Centralize event information",
      "Help organizers manage registrations",
    ],

    personas: [
      {
        name: "Student",
        role: "University Student",
        goals: [
          "Discover interesting campus events",
          "Register easily",
          "Receive event reminders",
        ],
        pain_points: [
          "Event information is scattered",
          "Events are easy to miss",
        ],
      },
      {
        name: "Event Organizer",
        role: "Student Club Organizer",
        goals: [
          "Promote events",
          "Manage registrations",
          "Track attendance",
        ],
        pain_points: [
          "Manual registration management",
          "Limited event visibility",
        ],
      },
    ],

    user_stories: [
      {
        id: "US-001",
        as_a: "student",
        i_want: "discover upcoming campus events",
        so_that: "I can participate in activities I am interested in",
      },
      {
        id: "US-002",
        as_a: "student",
        i_want: "register for events",
        so_that: "I can reserve my place",
      },
      {
        id: "US-003",
        as_a: "event organizer",
        i_want: "create and manage events",
        so_that: "students can discover them",
      },
    ],

    functional_requirements: [
      {
        id: "FR-001",
        description:
          "The system shall allow users to browse upcoming campus events.",
        priority: "High",
      },
      {
        id: "FR-002",
        description:
          "The system shall allow students to register for events.",
        priority: "High",
      },
      {
        id: "FR-003",
        description:
          "The system shall allow organizers to create and manage events.",
        priority: "High",
      },
    ],

    non_functional_requirements: [
      {
        id: "NFR-001",
        description:
          "The platform shall provide responsive layouts across mobile and desktop devices.",
        category: "Usability",
      },
      {
        id: "NFR-002",
        description:
          "Event pages shall load quickly under normal campus traffic.",
        category: "Performance",
      },
    ],

    risks: [
      "Low adoption by student organizations",
      "Outdated event information",
      "Duplicate event listings",
    ],

    assumptions: [
      "Student organizations will actively publish events",
      "Students have access to university accounts",
    ],

    future_enhancements: [
      "Calendar integration",
      "Push notifications",
      "QR-based event check-in",
    ],
  },

  {
    title: "Student Finance Assistant",
    description: "Personal budgeting for college students",
    updated: "3 days ago",
    progress: 64,

    product_overview:
      "A personal finance assistant designed to help college students track spending, manage budgets, and understand their financial habits.",

    problem_statement:
      "College students often struggle to track daily spending and maintain a realistic budget while managing tuition, food, transportation, and entertainment expenses.",

    target_users: [
      "College students",
      "Students managing their first personal budget",
      "Students looking to improve financial habits",
    ],

    business_objectives: [
      "Help students understand their spending",
      "Encourage better budgeting habits",
      "Provide simple financial insights",
    ],

    personas: [
      {
        name: "College Student",
        role: "Undergraduate Student",
        goals: [
          "Control monthly spending",
          "Save money",
          "Understand spending patterns",
        ],
        pain_points: [
          "Difficulty tracking expenses",
          "Unexpected expenses",
          "Complex finance applications",
        ],
      },
    ],

    user_stories: [
      {
        id: "US-001",
        as_a: "student",
        i_want: "track my expenses",
        so_that: "I understand where my money goes",
      },
      {
        id: "US-002",
        as_a: "student",
        i_want: "create monthly budgets",
        so_that: "I can control my spending",
      },
      {
        id: "US-003",
        as_a: "student",
        i_want: "view spending insights",
        so_that: "I can improve my financial habits",
      },
    ],

    functional_requirements: [
      {
        id: "FR-001",
        description:
          "The system shall allow users to record and categorize expenses.",
        priority: "High",
      },
      {
        id: "FR-002",
        description:
          "The system shall allow users to create monthly budgets.",
        priority: "High",
      },
      {
        id: "FR-003",
        description:
          "The system shall provide spending summaries and insights.",
        priority: "Medium",
      },
    ],

    non_functional_requirements: [
      {
        id: "NFR-001",
        description:
          "The application shall provide a responsive mobile-first interface.",
        category: "Usability",
      },
      {
        id: "NFR-002",
        description:
          "Financial data shall be securely stored and transmitted.",
        category: "Security",
      },
    ],

    risks: [
      "Incorrect expense categorization",
      "Users abandoning manual expense tracking",
      "Security concerns around financial information",
    ],

    assumptions: [
      "Users manually enter or import expenses",
      "Users have access to smartphones or computers",
    ],

    future_enhancements: [
      "Bank account integration",
      "AI-powered spending recommendations",
      "Automatic expense categorization",
    ],
  },
];

/* =========================================================
   DASHBOARD
   ========================================================= */

export default function Dashboard({ onPRDGenerated }) {
  const [productIdea, setProductIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* =======================================================
     GENERATE PRD
     ======================================================= */

  async function handleGeneratePRD() {
    const idea = productIdea.trim();

    if (!idea) {
      setError("Please describe your product idea first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      console.log("Generating PRD...");

      const result = await generatePRD(idea);

      console.log("PRD API result:", result);

      if (!result) {
        throw new Error("Empty response received from the API.");
      }

      onPRDGenerated(result);
    } catch (err) {
      console.error("PRD generation failed:", err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to generate the PRD. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  /* =======================================================
     NEW PRD
     ======================================================= */

  function handleNewPRD() {
    setProductIdea("");
    setError("");

    // Clear currently opened PRD in App.jsx
    if (onPRDGenerated) {
      onPRDGenerated(null);
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  /* =======================================================
     OPEN RECENT PRD
     ======================================================= */

  function handleOpenRecentPRD(prd) {
    setError("");

    if (onPRDGenerated) {
      onPRDGenerated(prd);
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  /* =======================================================
     VIEW ALL
     ======================================================= */

  function handleViewAll() {
    document.querySelector(".recent-section")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <div className="dashboard">
      {/* =====================================================
          TOP BAR
      ===================================================== */}

      <header className="topbar">
        <div className="breadcrumb">
          Workspace <span>/</span> Overview
        </div>

        <div className="topbar-actions">
          <button
            className="icon-button"
            type="button"
            title="Recent activity"
          >
            <Clock3 size={17} />
          </button>

          <div className="topbar-avatar">SJ</div>
        </div>
      </header>

      {/* =====================================================
          WELCOME
      ===================================================== */}

      <section className="welcome-section">
        <div>
          <div className="section-eyebrow">
            <span className="eyebrow-line" />
            PRODUCT WORKSPACE
          </div>

          <h1>
            Good afternoon, <strong>Shourya.</strong>
          </h1>

          <p>
            Turn product ideas into structured requirements your engineering
            team can actually build.
          </p>
        </div>

        <button
          className="new-prd-button"
          type="button"
          onClick={handleNewPRD}
        >
          <Plus size={17} />
          New PRD
        </button>
      </section>

      {/* =====================================================
          CREATE PRD
      ===================================================== */}

      <section className="create-section">
        <div className="create-header">
          <div>
            <span className="create-label">
              <Sparkles size={14} />
              CREATE
            </span>

            <h2>Start with an idea</h2>

            <p>
              Describe your product and let the PRD engine structure the
              requirements.
            </p>
          </div>

          <div className="create-step">01</div>
        </div>

        <div className="idea-box">
          <textarea
            value={productIdea}
            onChange={(event) => {
              setProductIdea(event.target.value);

              if (error) {
                setError("");
              }
            }}
            placeholder="Example: I want to build a platform where college students can find and book verified tutors..."
            disabled={loading}
          />

          <div className="idea-footer">
            <span>
              {productIdea.length > 0
                ? `${productIdea.length} characters`
                : "Be as detailed or as simple as you like."}
            </span>

            <button
              className="generate-button"
              type="button"
              onClick={handleGeneratePRD}
              disabled={loading}
            >
              {loading ? (
                <>
                  <LoaderCircle size={17} className="spin" />
                  Generating...
                </>
              ) : (
                <>
                  Generate PRD
                  <ArrowUpRight size={17} />
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="prd-error">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}
        </div>
      </section>

      {/* =====================================================
          RECENT PRDs
      ===================================================== */}

      <section className="recent-section">
        <div className="section-header">
          <div>
            <span className="section-eyebrow">
              <span className="eyebrow-line" />
              YOUR WORK
            </span>

            <h2>Recent PRDs</h2>
          </div>

          <button
            className="view-all"
            type="button"
            onClick={handleViewAll}
          >
            View all
            <ArrowUpRight size={15} />
          </button>
        </div>

        <div className="prd-list">
          {recentPRDs.map((prd) => (
            <article
              className="prd-row"
              key={prd.title}
              onClick={() => handleOpenRecentPRD(prd)}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  handleOpenRecentPRD(prd);
                }
              }}
            >
              {/* ICON */}

              <div className="prd-icon">
                <FileText size={19} />
              </div>

              {/* MAIN CONTENT */}

              <div className="prd-main">
                <div className="prd-title-row">
                  <h3>{prd.title}</h3>

                  <span className="prd-status">
                    <CheckCircle2 size={13} />
                    Complete
                  </span>
                </div>

                <p>{prd.description}</p>

                <div className="progress-track">
                  <div
                    className="progress-bar"
                    style={{
                      width: `${prd.progress}%`,
                    }}
                  />
                </div>
              </div>

              {/* META */}

              <div className="prd-meta">
                <span>{prd.progress}%</span>
                <small>{prd.updated}</small>
              </div>

              {/* ARROW */}

              <ArrowUpRight className="row-arrow" size={18} />
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}