# Simhastha 2028 - Prototype Limitations

This Sprint 1 application is a local-development prototype. It is not an
official Simhastha service and must not be used to seek emergency help or make
travel decisions without consulting an authoritative source.

## Safety-critical limitations

- The SOS form only stores a simulated incident in this application's database.
  It sends no alert and dispatches no police, ambulance, fire, medical, or
  government responder.
- Emergency-directory phone numbers are deliberately non-routable placeholders.
  They are not live services and must not be dialled in an emergency.
- Lost & Found and Missing Person reports are stored only for prototype
  demonstration. They are not sent to police or any missing-person authority.
- There is no integration with CCTV, facial recognition, biometrics, live crowd
  sensors, traffic systems, government records, or command-centre systems.

## Information limitations

- Temple timings, aarti schedules, accessibility information, transport notes,
  events, and announcements are seed data for UI development. They are marked
  placeholder or indicative and are not authority-verified.
- Map locations are approximate visual markers, not navigation, surveying, or
  safety information. Crowd and traffic layers are static placeholders, not
  live conditions.
- The application supports English and Hindi scaffolding only. Translations
  remain subject to review by qualified local-language and domain experts.

## Technical and scope limitations

- The only supported deployment path is local `docker compose`; there is no
  cloud deployment, production hardening, uptime commitment, or operational
  support.
- This sprint does not include the pilgrimage planner, parking availability,
  transport integrations, PWA/offline support, AI/RAG assistant, Kafka,
  OpenSearch, computer vision, volunteer/vendor platforms, command centre, or
  digital twin.
- Admin credentials seeded for development are not production credentials and
  must be replaced before any non-local use.

See [ROADMAP.md](ROADMAP.md) for the deferred product backlog.
