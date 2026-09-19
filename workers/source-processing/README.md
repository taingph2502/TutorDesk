# Source-processing worker

This directory is the image and deployment boundary for the disposable Source Processing worker.
The worker's Python entrypoint remains part of the single `tutordesk` distribution under
`apps/server`; this directory must not become an independently owned domain service.
