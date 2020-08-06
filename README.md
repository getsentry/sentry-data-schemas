# Sentry Data Schemas

This is a collection of shared data schema definitions across Sentry's services.

If there is a definitive service that owns/produces the schema, it should be
used as folder name. Otherwise put the schema into `sentry/`.

## `relay/event.schema.json`

Contains a draft-07 JSON Schema of the Event payload as accepted, validated and
understood by Relay. The schema is automatically updated when `master` in
`getsentry/relay` is committed to.

Following caveats apply:

- Security reports and transaction events are not part of that schema.
- The top-level keys `metadata` and `title` are missing because Relay does not
  produce them (Sentry does).
- The key `project_id` and `received` is missing as Relay does not accept those from SDK.
- The keys `culprit`, `template` and other deprecated fields are missing such
  that no producers or consumers can either send or rely on them.

In short, only the canonical form of an error event as SDKs should send them is
reflected by that schema.
