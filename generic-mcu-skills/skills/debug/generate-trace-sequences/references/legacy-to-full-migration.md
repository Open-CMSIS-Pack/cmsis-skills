# Legacy-to-full migration

Use `assets/scaffolds/full-trace.xml` when an existing PDSC uses or omits `traceSetup="legacy"`, or when a `cbuild-run` file uses or omits `debug-sequences-conf.trace-setup: legacy`.

1. Preserve verified device-specific pin, clock, reset, and access-enable behavior as device-extension calls.
2. Replace debugger-assumed CoreSight setup with selected component-asset calls.
3. Set PDSC `traceSetup="full"` or `cbuild-run` `debug-sequences-conf.trace-setup: full` only after every required sink and trace-path component is configured by the emitted sequences.
4. Retain the required extension/CoreSight ordering markers and validate the selected destination format.
