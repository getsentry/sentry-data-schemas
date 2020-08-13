# Sentry Data Schemas

This is a collection of shared data schema definitions across Sentry's services.

## Adding new schemas

- If there is a definitive service that owns/produces the schema, it should be
  used as folder name. Otherwise put the schema into `sentry/`.
- Bot commits for auto-generated schema updates should reference the commit in
  the service repo that they were triggered by (e.g. reference commit of Relay
  master for schema change originating in Relay)

## Consuming schemas

Right now the best way to use this repo is to include it as a submodule in your
project and set up [Dependabot to periodically update
`HEAD`](https://dependabot.com/submodules/), then use the following tools:

- For consuming JSON Schema in Python,
  [jsonschema-typed](https://github.com/inspera/jsonschema-typed)
  (`jsonschema-typed-v2` on PyPI) is recommended. It has been found by Snuba
  devs to produce decent type definitions.
- For consuming JSON Schema in TypeScript,
  [json-schema-to-typescript](https://github.com/bcherny/json-schema-to-typescript)
  is recommended.
- In other situations, setting up something based on
  [quicktype](https://github.com/quicktype/quicktype) might help. Quicktype
  produces output for a very large variety of languages, but its output for
  TypeScript in particular has been found to be weakly typed. We use [a fork of
  quicktype](https://github.com/getsentry/quicktype) to generate schema
  documentation.

## List of schemas

### `relay/event.schema.json`

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
