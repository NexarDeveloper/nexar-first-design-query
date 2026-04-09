# platform-api-first-design-query
[365.altium.com]: https://365.altium.com/

Simple console app which looks up projects in an Altium 365 workspace.

## Prerequisites

You need your Altium Live credentials and have to be a member of at least one Altium 365 workspace.

In addition, you need an application at [365.altium.com].
When you create your application, you have two options regarding the token to use in `platform-api-first-design-query`:
- either generate a Personal Access Token (PAT), by unticking the Refresh Token option
- or generate a triplet: Client ID, Client Secret and Refresh Token, by ticking the Refresh Token option 

Depending on which option chosen above, make sure you have the right environment variables set before you run `platform-api-first-design-query`:
- either: `A365_PAT`
- or: `A365_CLIENT_ID`, `A365_CLIENT_SECRET` and `A365_REFRESH_TOKEN`
