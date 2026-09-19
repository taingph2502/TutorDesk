# TutorDesk server

The Python distribution contains TutorDesk's domain modules and runtime entrypoints. Adapters call
domain modules through typed public interfaces; modules do not read one another's storage directly.

It exposes separate API, scheduler, Source Processing supervisor, source worker, migration, and
maintenance commands. Pending process implementations fail explicitly instead of simulating health.
