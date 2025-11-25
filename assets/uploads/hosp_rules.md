# CarePulse Hospital - Operational Protocols

## 1. Admission Protocols
- **Mandatory Fields:**
  - Patient Name and Age are required for all admissions.
  - If the patient is under 18 (Minor), a "Guardian Name" field must serve as a mandatory input (logic handled by backend).
- **Triage Rules:**
  - **Emergency (Red):**
    - Does not require Insurance information immediately.
    - Must automatically trigger a page to the on-call specialist.
  - **Routine (Green):**
    - Cannot be processed without valid Insurance ID.

## 2. Doctor Availability
- **Paging System:**
  - You cannot page a doctor who has the status "In Surgery".
  - Paging an "Available" doctor sends an SMS alert.

## 3. Data Privacy (HIPAA)
- Patient names must never be displayed in full on public waiting room screens (e.g., use "John D.").
- The "Emergency Contact" phone number must be masked after entry (e.g., `******1234`).