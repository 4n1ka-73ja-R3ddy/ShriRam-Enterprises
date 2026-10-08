# AppointmentHub — Backend API Handoff Contract

This is an implementation contract for the future backend. It intentionally avoids choosing a backend framework/database until ma'am confirms the stack.

## Candidate APIs

### GET /slots?date=YYYY-MM-DD&duration=15|30
Returns slots derived from trainer availability, unavailable periods, and accepted/confirmed appointments.

Suggested response:
```json
{
  "date": "2026-10-10",
  "duration": 30,
  "slots": [
    {"time":"10:00","status":"available"},
    {"time":"10:30","status":"requested"},
    {"time":"11:00","status":"booked"}
  ]
}
```

### POST /appointments
Creates an appointment request.

Minimum data:
- preferred date
- preferred time
- duration
- candidate name
- email
- phone

The backend returns a unique `appointment_id` and status `PENDING_FORM`.

### GET /appointments/:id
Returns the candidate-facing request status and appointment details.

### POST /appointments/:id/form-complete
Integration endpoint for the external form response, if the final form mechanism supports backend callbacks.

The exact payload depends on the teammate's form implementation.

### POST /payments/create
Creates a payment request after trainer acceptance.

### POST /payments/verify
Verifies the payment. Only after successful verification should the appointment become `CONFIRMED`.

## Trainer APIs

### POST /trainer/login
Authentication method is TBD.

### GET /trainer/requests
Suggested filters:
- candidate/user search
- exact date
- month
- preferred time
- status
- priority sorting

### GET /trainer/requests/:id
Returns candidate details, preferred appointment, status and available form-response data.

### POST /trainer/requests/:id/accept
Changes an eligible request to `ACCEPTED` / payment pending.

### POST /trainer/requests/:id/reject
Changes the request to `REJECTED`.

### GET /trainer/availability
Returns weekly availability and date/time blocks.

### PUT /trainer/availability
Updates weekly availability.

### POST /trainer/unavailable-periods
Creates a busy/leave/holiday block.

### DELETE /trainer/unavailable-periods/:id
Removes a future block.

## External integrations

### Form
The exact endpoint depends on the form teammate's implementation. Do not assume Google Forms, Apps Script or a webhook until confirmed.

### Notification
The channel is TBD. The backend should expose one internal notification service so the channel can change without changing appointment logic.

### Payment
The gateway is TBD. Use a provider adapter so the provider can be changed if required.

### Google Calendar
The backend should own all Google Calendar credentials and API calls. The exact account/calendar and event-creation point must be confirmed.

## Status model

Recommended:

`PENDING_FORM -> PENDING_APPROVAL -> ACCEPTED -> CONFIRMED`

Other possible outcomes:

`REJECTED`, `CANCELLED`, `EXPIRED`

These names are implementation proposals, not verbatim requirements from ma'am.
