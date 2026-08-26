# User Stories and Acceptance Criteria

User stories are short, simple descriptions of a feature, told from the perspective of the person who desires the new capability. They are typically written in the standard format:

> **"As a [Type of User], I want [Some Feature/Goal], so that [Specific Value/Benefit]."**

## Principles of Good User Stories

- **Independent**: Each story can be developed, tested, and shipped independently of others.
- **Negotiable**: They are not rigid contracts; they leave room for discussion and technical flexibility.
- **Valuable**: They must deliver clear business or customer value.
- **Estimable**: The development team can understand and estimate the effort required.
- **Small**: They should fit within a single sprint (typically 1-2 weeks).
- **Testable**: They must have clear criteria to determine if they are done.

## Acceptance Criteria

Acceptance criteria define the boundaries of a user story and detail exactly what must be true for the story to be considered complete. A common framework is **Given-When-Then**:

- **Given**: The initial context or state of the system.
- **When**: The action or event performed by the user.
- **Then**: The expected outcome or reaction of the system.

### Example User Story and Criteria

- **User Story**: "As a struggling student, I want to filter tutors by course number and availability, so that I can quickly find someone who can help with my specific exam preparation."
- **Acceptance Criteria**:
  - Given a student is on the tutor search screen, when they select "CS 201" from the course dropdown, then only tutors who have certified expertise in CS 201 are shown.
  - Given the search results list, when a tutor is selected, then their schedule calendar highlights slots matching the student's available times.
