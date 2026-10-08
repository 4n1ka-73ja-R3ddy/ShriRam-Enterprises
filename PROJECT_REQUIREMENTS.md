# AppointmentHub — Project Requirement & Responsibility Notes

## Confirmed workflow from the current project brief

1. Candidate selects a preferred date, duration and time slot.
2. Candidate enters contact details and submits an appointment **request**.
3. The request is not immediately confirmed.
4. Candidate is directed to an external application form containing additional information such as marks/score and other questions.
5. The external form is created/maintained by another project team member. This prototype only provides the integration point.
6. After the form is submitted, the request and form information are available to the trainer.
7. Trainer can view, filter/search and prioritize requests and review candidate details.
8. Trainer accepts or rejects a request.
9. After acceptance, the candidate is notified and payment is required.
10. After successful payment, the appointment becomes confirmed.
11. Google/Google Calendar API integration is expected, but the exact calendar, timing and API details must be confirmed.
12. Trainer availability can be modified, including busy/leave/unavailable periods.

## Prototype decisions made deliberately

- Candidate pages do not expose a prominent Trainer Panel link.
- The trainer portal is a separate internal prototype page (`trainer.html`). Authentication is not implemented because the required authentication method was not specified.
- Pending requests may share a preferred slot during the trainer-review stage. This allows the trainer to compare requests by priority. The prototype does **not** automatically reject competing candidates.
- Only an accepted or confirmed appointment blocks a slot in the prototype.
- Priority is shown using the submitted score as a **demo indicator only**. The real priority rule is not invented.
- Payment is a demo action. No real gateway is connected.
- Notification is represented in the status flow. No specific channel is invented.
- Google Calendar is represented as a future integration point. No credentials or calendar account are invented.
- LocalStorage is only a frontend demonstration substitute for the future backend/database.

## Responsibilities

### Appointment/booking implementation
- Candidate booking UI
- Request creation and request status
- Trainer request inbox
- Filters/search/sorting
- Trainer accept/reject
- Availability management
- Integration points for external form, payment, notification and Google Calendar

### External form teammate
- Build/maintain the real external form
- Define the actual form questions
- Provide the form URL
- Provide/confirm the method by which submitted responses can be associated with the appointment request

The booking implementation must not claim ownership of the external form itself.

## Items to confirm with ma'am before production integration

1. Is the Google API specifically Google Calendar API?
2. Which calendar/account should be checked and used for event creation?
3. What is the exact priority rule?
4. What is the external form platform and response mechanism?
5. What payment gateway and fee should be used?
6. What notification channel is required?
7. Is there one trainer or multiple trainers, and how are requests assigned?
8. How long should an accepted/unpaid request hold a slot?
9. What backend/database/authentication stack should the internship use?
10. Are 15 and 30 minutes the final allowed durations?
11. What exactly does the earlier “every day” availability requirement mean?

## Suggested production architecture

Candidate Frontend → Backend API → Database

Trainer Frontend → Backend API → Database

Backend → External Form integration
Backend → Payment gateway
Backend → Notification service
Backend → Google Calendar API

The frontend should not connect directly to the database or Google Calendar credentials.
