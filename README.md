# platform-api-first-query

[365.altium.com]: https://365.altium.com/

A collection of example applications that illustrate an API-first approach to
querying the [Altium 365][365.altium.com] platform through its GraphQL API.

The examples are provided per language. In each language, a "Hello Workspace"
example gets you started, along with a number of use cases that query the
platform in different ways — see the language-specific README for the current list.

## Prerequisites

These apply regardless of the language you use:

- Altium Live credentials, and membership of at least one Altium 365 workspace.
- An application registered at [365.altium.com].

When you create your application, you choose how to authenticate:

- generate a Personal Access Token (PAT), by unticking the Refresh Token option, or
- generate a triplet — Client ID, Client Secret and Refresh Token — by ticking the
  Refresh Token option.

The language-specific README explains how to supply the token(s) you generated.

## Examples by language

### Python

See [python/README.md](python/README.md).

- **Hello Workspace** — a basic example that reads metadata from your Altium 365 workspace.
