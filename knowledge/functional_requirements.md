# Functional Requirements Best Practices

Functional requirements define what the software system must do. They describe the system's behavior, features, inputs, outputs, and workflows under specific conditions.

## Writing Effective Functional Requirements

1. **Use Clear, Direct Language**: Traditionally, functional requirements use the phrase "The system shall..." or "The user must be able to...".
2. **Be Atomic and Traceable**: Each requirement should specify one and only one feature or behavior. It should be uniquely numbered or tagged.
3. **Avoid Implementation Details**: Say *what* the system should do, not *how* to do it. For instance, write "The system shall verify the user's password before granting access," rather than "The system shall run a bcrypt verification query against the MongoDB users collection."
4. **Make It Verifiable**: A tester must be able to verify whether the system successfully meets the requirement.

## Examples of Functional Requirements

- **User Authentication**:
  - `FR-1.1`: The system shall validate that a user's email address is from an approved university domain (.edu) during registration.
  - `FR-1.2`: The system shall send a 6-digit confirmation code via email to verify the user's identity.
- **Search & Filtering**:
  - `FR-2.1`: The system shall allow users to search for peer tutors by typing course codes or keywords.
  - `FR-2.2`: The system shall sort tutor search results by average user rating by default.
- **Scheduling & Booking**:
  - `FR-3.1`: The system shall prevent a student from booking a tutor slot that is already booked by another user.
  - `FR-3.2`: The system shall send real-time push notifications or email alerts to both parties upon successful session booking.
