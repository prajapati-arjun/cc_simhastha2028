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
