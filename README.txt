APPOINTMENTHUB — FINAL FRONTEND PROTOTYPE
=========================================

Purpose
-------
This is a professional frontend prototype for the appointment request workflow described in the current project brief.

IMPORTANT RESPONSIBILITY BOUNDARY
---------------------------------
The real external application form is NOT created in this package. It is owned/provided by another project team member.
This package only provides the integration point and a demo simulation so the complete trainer workflow can be demonstrated.

Candidate flow
--------------
index.html
  -> choose preferred date, duration and available time
  -> details.html
  -> submit appointment request (NOT confirmed)
  -> application.html
  -> open external form when its URL is supplied
  -> status.html
  -> trainer approval
  -> payment
  -> confirmed

Trainer flow
------------
trainer.html
  -> Appointment Requests
     - search candidate/email/request ID
     - filter exact date
     - filter month
     - filter preferred time
     - filter status
     - sort by priority/date/newest
     - view candidate + request + form information
     - accept/reject
  -> Availability
     - view weekly schedule
     - modify weekly timings
     - mark full dates or time ranges unavailable

Demo behavior
-------------
- Data is stored in localStorage only. This is NOT the production backend.
- Pending requests may share the same preferred slot so the trainer can compare them.
- Accepted/confirmed appointments block overlapping slots.
- Priority is a DEMO indicator based on score only. The real priority rule must be confirmed.
- Payment is simulated.
- Notification is represented in the UI only.
- Google Calendar is represented as a future integration point.

External form setup
-------------------
Open shared.js and set:

EXTERNAL_FORM_URL: 'YOUR_REAL_FORM_URL'

When configured, the application page passes the appointment ID as:

?appointment_id=REQUEST_ID

The exact response/webhook/integration mechanism depends on how the teammate's form is built and must be agreed before backend integration.

How to run
-----------
1. Open this folder in VS Code.
2. Use Live Server (recommended) on index.html.
3. Candidate flow: index.html -> details.html -> application.html.
4. For the trainer demonstration, open trainer.html directly. It is intentionally not linked from the candidate pages.
5. Click “Load demo requests” in the trainer portal to populate sample requests.
6. Use the trainer portal to review and accept/reject requests.
7. Use the Availability tab to change timings and observe slot changes on the candidate page.

Files
-----
index.html              Candidate slot selection
details.html/js         Candidate details and request creation
application.html        External-form integration placeholder + demo simulation
status.html/js          Candidate request status / payment demo
trainer.html/js         Trainer portal and availability management
trainer-requests.js     Trainer inbox, filters, priority indicator, accept/reject
shared.js               Shared demo data, status model, slot logic and integration configuration
style.css               UI styling
PROJECT_REQUIREMENTS.md Confirmed scope, responsibilities, assumptions and questions

NOT PRODUCTION YET
------------------
The following must be connected in the backend stage:
- database
- real API endpoints
- trainer authentication
- real external-form response integration
- actual priority rule
- notification service
- payment gateway
- Google Calendar API
- slot-hold/expiry rule

Do not present the demo localStorage behavior as the final backend implementation.
