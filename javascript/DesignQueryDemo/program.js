const nx = require('../AltiumClient/apiClient')
const pat = process.env.A365_PAT ??
    (() => {throw new Error("Please set environment variable 'A365_PAT'")})()
const client = new nx.AltiumClient(pat, nx.AltiumClient.scopes.design)

const gqlQuery = `query Workspaces {
    desWorkspaceInfos {
      url
      name
      description
      location {
        apiServiceUrl
      }
    }
  }`

let workspaces = client.query(gqlQuery, "/napi/gateway/graphql")
    .then(response => response.data.desWorkspaceInfos)

// This second query uses the node (paged) interface.
// To iterate through the pages we need a variable to set the cursor (after: $var)
const gqlQuery2 = `query Projects($url: String!, $end: String) {
    desProjects(workspaceUrl: $url, first: 10, after: $end) {
      nodes {
        id
        name
        description
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }`

workspaces
    .then(async workspaces => {
        for (workspace of workspaces) {
            client.host = workspace.location.apiServiceUrl
            console.log(`projects for workspace: ${workspace.name} (${client.hostName})`)

            let gqlVariables = {'url': workspace.url}
            let projects = client.pageGen(gqlQuery2, "/svc/napi/gateway/graphql", gqlVariables, 'end', (data) => data.desProjects)

            for await (const page of projects) {
                for (const project of page) {
                    console.log(`Project Id: ${project?.id}`)
                    console.log(`Name: ${project?.name}`)
                    console.log(`Description: ${project?.description}`)
                    console.log()
                }
            }
        }
    })