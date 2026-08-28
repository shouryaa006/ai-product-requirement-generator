import {
  CheckCircle2,
  Users,
  Target,
  AlertTriangle,
  Lightbulb,
  ListChecks,
  ShieldCheck,
  UserRound,
  ArrowLeft,
} from "lucide-react";

/*
 * Safely convert any API value into text React can render.
 */
function safeText(value, fallback = "") {
  if (value === null || value === undefined) {
    return fallback;
  }

  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.map((item) => safeText(item)).join(", ");
  }

  if (typeof value === "object") {
    if (value.text !== undefined) {
      return safeText(value.text);
    }

    if (value.description !== undefined) {
      return safeText(value.description);
    }

    if (value.name !== undefined) {
      return safeText(value.name);
    }

    try {
      return JSON.stringify(value);
    } catch {
      return "";
    }
  }

  return String(value);
}

/*
 * Safely convert API values into arrays.
 */
function safeArray(value) {
  if (!value) {
    return [];
  }

  if (Array.isArray(value)) {
    return value;
  }

  if (typeof value === "string") {
    return value
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return [value];
}

/*
 * Remove accidental SVG/XML artifacts from LLM output.
 */
function cleanText(value) {
  const text = safeText(value);

  if (!text) {
    return "";
  }

  return text
    .replace(/<svg[\s\S]*?<\/svg>/gi, "")
    .replace(/<svg[^>]*>/gi, "")
    .replace(/<\/svg>/gi, "")
    .replace(/\bsvgReady\b/gi, "")
    .replace(/\bsvg\b/gi, "")
    .trim();
}

/*
 * Handles section layout.
 */
function Section({ icon: Icon, label, children }) {
  return (
    <section className="result-section">
      <div className="result-section-header">
        <div className="result-section-icon">
          <Icon size={17} />
        </div>

        <span>{label}</span>
      </div>

      <div className="result-section-content">
        {children}
      </div>
    </section>
  );
}

/*
 * Bullet list.
 */
function BulletList({ items }) {
  const list = safeArray(items);

  if (!list.length) {
    return null;
  }

  return (
    <ul className="result-list">
      {list.map((item, index) => {
        const text = cleanText(item);

        if (!text) {
          return null;
        }

        return <li key={index}>{text}</li>;
      })}
    </ul>
  );
}

/*
 * Persona card.
 */
function PersonaCard({ persona, index }) {
  if (!persona) {
    return null;
  }

  const name =
    cleanText(persona.name) ||
    cleanText(persona.title) ||
    `Persona ${index + 1}`;

  const role =
    cleanText(persona.role) ||
    cleanText(persona.title) ||
    cleanText(persona.description);

  const goals = safeArray(persona.goals);

  const painPoints = safeArray(
    persona.pain_points ??
      persona.painPoints ??
      persona.pains
  );

  return (
    <article className="persona-card">
      <div className="persona-header">
        <div className="persona-avatar">
          {name.charAt(0).toUpperCase()}
        </div>

        <div>
          <h3>{name}</h3>

          {role && <span>{role}</span>}
        </div>
      </div>

      {goals.length > 0 && (
        <div className="persona-group">
          <strong>Goals</strong>
          <BulletList items={goals} />
        </div>
      )}

      {painPoints.length > 0 && (
        <div className="persona-group">
          <strong>Pain points</strong>
          <BulletList items={painPoints} />
        </div>
      )}
    </article>
  );
}

/*
 * User story card.
 */
function UserStoryCard({ story, index }) {
  if (!story) {
    return null;
  }

  const id =
    cleanText(story.id) ||
    `US-${String(index + 1).padStart(3, "0")}`;

  const asA =
    cleanText(story.as_a) ||
    cleanText(story.asA) ||
    cleanText(story.actor);

  const iWant =
    cleanText(story.i_want) ||
    cleanText(story.iWant) ||
    cleanText(story.action);

  const soThat =
    cleanText(story.so_that) ||
    cleanText(story.soThat) ||
    cleanText(story.benefit);

  return (
    <article className="story-card">
      <span className="story-id">{id}</span>

      <div className="story-content">
        {asA && (
          <p>
            <strong>As a</strong>{" "}
            {asA}
          </p>
        )}

        {iWant && (
          <p>
            <strong>I want</strong>{" "}
            {iWant}
          </p>
        )}

        {soThat && (
          <p>
            <strong>So that</strong>{" "}
            {soThat}
          </p>
        )}
      </div>
    </article>
  );
}

/*
 * Functional requirement card.
 */
function FunctionalRequirementCard({
  requirement,
  index,
}) {
  if (!requirement) {
    return null;
  }

  const id =
    cleanText(requirement.id) ||
    `FR-${String(index + 1).padStart(3, "0")}`;

  const description =
    cleanText(requirement.description) ||
    cleanText(requirement.requirement) ||
    cleanText(requirement.text);

  const priority =
    cleanText(requirement.priority) ||
    cleanText(requirement.level);

  return (
    <article className="requirement-card">
      <span className="requirement-id">
        {id}
      </span>

      <p>{description}</p>

      {priority && (
        <span className="priority-badge">
          {priority}
        </span>
      )}
    </article>
  );
}

/*
 * Non-functional requirement card.
 */
function NonFunctionalRequirementCard({
  requirement,
  index,
}) {
  if (!requirement) {
    return null;
  }

  const id =
    cleanText(requirement.id) ||
    `NFR-${String(index + 1).padStart(3, "0")}`;

  const description =
    cleanText(requirement.description) ||
    cleanText(requirement.requirement) ||
    cleanText(requirement.text);

  const category =
    cleanText(requirement.category) ||
    cleanText(requirement.type);

  return (
    <article className="requirement-card">
      <span className="requirement-id">
        {id}
      </span>

      <p>{description}</p>

      {category && (
        <span className="category-badge">
          {category}
        </span>
      )}
    </article>
  );
}

/*
 * Main PRD result component.
 *
 * IMPORTANT:
 * Accepts BOTH:
 *
 * <PRDResult result={data} />
 *
 * and
 *
 * <PRDResult prd={data} />
 *
 * so App.jsx and older Dashboard code both work.
 */
export default function PRDResult({
  prd,
  result,
  onBack,
}) {
  /*
   * Prefer result because App.jsx currently sends:
   *
   * <PRDResult result={prdResult} />
   *
   * Fall back to prd for compatibility.
   */
  let data = result ?? prd;

  /*
   * Handle API wrappers.
   */
  if (
    data &&
    typeof data === "object" &&
    !Array.isArray(data)
  ) {
    if (
      data.prd &&
      typeof data.prd === "object"
    ) {
      data = data.prd;
    } else if (
      data.data &&
      typeof data.data === "object"
    ) {
      data = data.data;
    } else if (
      data.result &&
      typeof data.result === "object"
    ) {
      data = data.result;
    }
  }

  /*
   * Handle JSON returned as a string.
   */
  if (typeof data === "string") {
    try {
      data = JSON.parse(data);
    } catch {
      data = {
        product_overview: data,
      };
    }
  }

  /*
   * Sometimes the API returns JSON inside a text/content field.
   */
  if (
    data &&
    typeof data === "object" &&
    !Array.isArray(data)
  ) {
    const possibleText =
      data.content ??
      data.text ??
      data.output;

    if (
      typeof possibleText === "string" &&
      possibleText.trim().startsWith("{")
    ) {
      try {
        const parsed = JSON.parse(possibleText);

        if (
          parsed &&
          typeof parsed === "object"
        ) {
          data = parsed;
        }
      } catch {
        // Keep original data if parsing fails.
      }
    }
  }

  /*
   * Final safety check.
   */
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data)
  ) {
    return (
      <div className="prd-result">
        <div className="prd-error">
          <AlertTriangle size={16} />

          <span>
            The generated PRD could not be displayed.
          </span>
        </div>
      </div>
    );
  }

  /*
   * Extract sections.
   */
  const productOverview =
    cleanText(data.product_overview) ||
    cleanText(data.productOverview);

  const problemStatement =
    cleanText(data.problem_statement) ||
    cleanText(data.problemStatement);

  const targetUsers = safeArray(
    data.target_users ??
      data.targetUsers
  );

  const businessObjectives = safeArray(
    data.business_objectives ??
      data.businessObjectives
  );

  const personas = safeArray(
    data.personas
  );

  const userStories = safeArray(
    data.user_stories ??
      data.userStories
  );

  const functionalRequirements =
    safeArray(
      data.functional_requirements ??
        data.functionalRequirements
    );

  const nonFunctionalRequirements =
    safeArray(
      data.non_functional_requirements ??
        data.nonFunctionalRequirements
    );

  const risks = safeArray(
    data.risks
  );

  const assumptions = safeArray(
    data.assumptions
  );

  const futureEnhancements =
    safeArray(
      data.future_enhancements ??
        data.futureEnhancements
    );

  return (
    <div className="prd-result">

      {/* HEADER */}
      <div className="prd-result-header">

        <div>
          {onBack && (
            <button
              type="button"
              className="prd-back-button"
              onClick={onBack}
            >
              <ArrowLeft size={16} />
              Back
            </button>
          )}

          <span className="result-eyebrow">
            <span className="eyebrow-line" />
            GENERATED PRD
          </span>

          <h2>
            Product Requirements
          </h2>

          <p>
            Structured requirements generated
            from your product idea.
          </p>
        </div>

        <div className="result-ready">
          <CheckCircle2 size={15} />
          Ready
        </div>

      </div>

      {/* PRODUCT OVERVIEW */}
      {productOverview && (
        <Section
          icon={Target}
          label="PRODUCT OVERVIEW"
        >
          <p>{productOverview}</p>
        </Section>
      )}

      {/* PROBLEM STATEMENT */}
      {problemStatement && (
        <Section
          icon={AlertTriangle}
          label="PROBLEM STATEMENT"
        >
          <p>{problemStatement}</p>
        </Section>
      )}

      {/* TARGET USERS */}
      {targetUsers.length > 0 && (
        <Section
          icon={Users}
          label="TARGET USERS"
        >
          <BulletList items={targetUsers} />
        </Section>
      )}

      {/* BUSINESS OBJECTIVES */}
      {businessObjectives.length > 0 && (
        <Section
          icon={Target}
          label="BUSINESS OBJECTIVES"
        >
          <BulletList
            items={businessObjectives}
          />
        </Section>
      )}

      {/* PERSONAS */}
      {personas.length > 0 && (
        <Section
          icon={UserRound}
          label="PERSONAS"
        >
          <div className="persona-grid">
            {personas.map(
              (persona, index) => (
                <PersonaCard
                  key={index}
                  persona={persona}
                  index={index}
                />
              )
            )}
          </div>
        </Section>
      )}

      {/* USER STORIES */}
      {userStories.length > 0 && (
        <Section
          icon={ListChecks}
          label="USER STORIES"
        >
          <div className="story-list">
            {userStories.map(
              (story, index) => (
                <UserStoryCard
                  key={index}
                  story={story}
                  index={index}
                />
              )
            )}
          </div>
        </Section>
      )}

      {/* FUNCTIONAL REQUIREMENTS */}
      {functionalRequirements.length > 0 && (
        <Section
          icon={CheckCircle2}
          label="FUNCTIONAL REQUIREMENTS"
        >
          <div className="requirement-list">
            {functionalRequirements.map(
              (requirement, index) => (
                <FunctionalRequirementCard
                  key={index}
                  requirement={requirement}
                  index={index}
                />
              )
            )}
          </div>
        </Section>
      )}

      {/* NON-FUNCTIONAL REQUIREMENTS */}
      {nonFunctionalRequirements.length > 0 && (
        <Section
          icon={ShieldCheck}
          label="NON-FUNCTIONAL REQUIREMENTS"
        >
          <div className="requirement-list">
            {nonFunctionalRequirements.map(
              (requirement, index) => (
                <NonFunctionalRequirementCard
                  key={index}
                  requirement={requirement}
                  index={index}
                />
              )
            )}
          </div>
        </Section>
      )}

      {/* RISKS */}
      {risks.length > 0 && (
        <Section
          icon={AlertTriangle}
          label="RISKS"
        >
          <BulletList items={risks} />
        </Section>
      )}

      {/* ASSUMPTIONS */}
      {assumptions.length > 0 && (
        <Section
          icon={Lightbulb}
          label="ASSUMPTIONS"
        >
          <BulletList items={assumptions} />
        </Section>
      )}

      {/* FUTURE ENHANCEMENTS */}
      {futureEnhancements.length > 0 && (
        <Section
          icon={Lightbulb}
          label="FUTURE ENHANCEMENTS"
        >
          <BulletList
            items={futureEnhancements}
          />
        </Section>
      )}

    </div>
  );
}