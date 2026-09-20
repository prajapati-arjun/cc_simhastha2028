"""
Prototype disclosure strings.

Standing constraint (SPRINT1_DECISIONS.md): no screen, endpoint, seed row or
document may imply a live connection to police, medical, CCTV or any government
dispatch system. Every safety-critical response embeds one of these verbatim,
so the disclosure travels with the payload rather than depending on the client
remembering to render a banner.

These strings are frozen by Docs/API_CONTRACT.md, em dash included. Do not
reword them without updating the contract and telling Frontend.
"""

EMERGENCY_NOTICE = "Demo prototype — not connected to live emergency dispatch."

SOS_NOTICE = (
    "Demo prototype — this SOS was recorded in a test database only. Nothing "
    "was dispatched and no responder was notified. In a real emergency contact "
    "local emergency services directly."
)

LOST_FOUND_NOTICE = (
    "Demo prototype — this report is stored in a test database and is not "
    "shared with police or any lost-property authority."
)

MISSING_PERSON_NOTICE = (
    "Demo prototype — this report is stored in a test database for this pilot "
    "and is NOT automatically sent to police. If a person is genuinely missing, "
    "contact local police directly."
)

GHAT_STATUS_NOTICE = (
    "Status is seeded placeholder data — no live sensor or CCTV feed is connected."
)

PARKING_AVAILABILITY_NOTICE = (
    "Occupancy count is operator-entered placeholder data — no live sensor, "
    "camera or gate-counter feed is connected in this prototype."
)

CROWD_NOTICE = (
    "Demo prototype — crowd density bands are operator-entered "
    "observations stored in a test database, not a live sensor, CCTV or "
    "headcount feed. Every figure is an aggregate zone-level band; no "
    "individual is tracked, identified or counted."
)

INCIDENT_NOTICE = (
    "Demo prototype — this incident record lives in this project's own test "
    "database and moves through its lifecycle only by human admin action "
    "here. Nothing is dispatched and no police, medical, fire or government "
    "system is notified. In a real emergency contact local emergency "
    "services directly."
)

COMMAND_CENTER_NOTICE = (
    "Demo prototype — this command centre view aggregates this "
    "project's own seeded and operator-entered data only. It is not "
    "connected to live CCTV, sensor or dispatch systems, and the "
    "\"recommendations\" section is intentionally empty because no "
    "model-generated recommendation engine exists in this prototype."
)

PLANNER_NOTICE = (
    "Demo prototype — this itinerary is generated from this project's own "
    "seed data using simple, deterministic scheduling rules. It is not an AI "
    "assistant, and not a live planning, booking or reservation system — it "
    "does not reflect real-time crowd, transport or accommodation "
    "availability. Nothing is saved; generate again if your plans change."
)
