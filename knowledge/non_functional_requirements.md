# Non-Functional Requirements (NFRs)

Non-functional requirements (NFRs) define the quality attributes, operational constraints, and performance parameters of a software system. Unlike functional requirements which specify *what* the system does, NFRs specify *how well* the system does it.

## Key Categories of NFRs

### 1. Performance and Scalability
- **Response Time**: The system shall load the dashboard page in under 1.5 seconds under normal load conditions.
- **Concurrent Users**: The backend API shall support at least 500 concurrent active connections without degradation in response time.
- **Throughput**: The database connection pool shall handle at least 100 read operations per second.

### 2. Security and Privacy
- **Encryption**: All user passwords shall be hashed using a cryptographically secure algorithm (e.g., bcrypt or Argon2) before database insertion.
- **Data in Transit**: All API requests and responses shall be encrypted using TLS 1.3.
- **Privacy Compliance**: The system shall support user request for deletion of all personal data (GDPR/CCPA compliance).

### 3. Availability and Reliability
- **Uptime**: The system shall maintain a 99.9% monthly availability (excluding scheduled maintenance).
- **Graceful Degradation**: In the event of a payment gateway outage, users should still be able to browse tutors and schedules without crashing the application.

### 4. Usability and Accessibility
- **Screen Reader Support**: The front-end user interface must comply with WCAG 2.1 Level AA accessibility guidelines.
- **Mobile responsiveness**: The web application must adapt dynamically to screens ranging from 320px (mobile) to 1920px (desktop).
