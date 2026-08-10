# platform-api-first-query — Python examples

Simple console apps which illustrate a number of queries in Altium 365:
- Hello Workspace basic example that gets metadata from your Altium 365 workspace
- a number of use cases (under `UseCases/`), such as looking up project revisions
  and parameters from your Altium 365 workspace.

See the [root README](../README.md) for prerequisites and how to register your
Altium 365 application. This README covers running the Python examples once you
have your credentials.

## Setup

From the `python/` directory, create and activate a virtual environment and
install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Hello Workspace

Using the application you registered:
- generate a Personal Access Token (PAT), by unticking the Refresh Token option
- paste that into the `PAT` variable in `hello_workspace.py`
- make sure you point `WORKSPACE_URL` to your workspace

Then run it:

```bash
python hello_workspace.py
```

## Project revisions and parameters use case

Depending on which authentication option you chose when registering your
application (see the [root README](../README.md)), make sure you have the right
environment variables set before you run the use case:
- either: `A365_PAT`
- or: `A365_CLIENT_ID`, `A365_CLIENT_SECRET` and `A365_REFRESH_TOKEN`

Then run it:

```bash
python UseCases/ProjectRevisionsAndReleases/project_revisions_and_parameters.py
```

### Overriding default endpoints
Default endpoints are provided for A365 GraphQL API and Refresh Token.
Those can be overridden if needed by setting the following environment variables:
- `A365_URL` for A365 GraphQL API endpoint override
- `TOKEN_URL` for Refresh Token endpoint override
