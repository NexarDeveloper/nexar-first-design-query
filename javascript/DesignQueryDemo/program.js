const nx = require('../NexarClient/nexarClient')
const clientId = process.env.NEXAR_CLIENT_ID ??
    (() => {throw new Error("Please set environment variable 'NEXAR_CLIENT_ID'")})()
const clientSecret = process.env.NEXAR_CLIENT_SECRET ??
    (() => {throw new Error("Please set environment variable 'NEXAR_CLIENT_SECRET'")})()
const nexar = new nx.NexarClient(clientId, clientSecret, nx.NexarClient.scopes.design)

const gqlQuery = `query Workspaces {
    desWorkspaces {
      url
      name
      description
      location {
        apiServiceUrl
      }
    }
  }`

let workspaces = nexar.query(gqlQuery)
    .then(response => response.data.desWorkspaces)

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
            nexar.host = workspace.location.apiServiceUrl
            console.log(`projects for workspace: ${workspace.name} (${nexar.hostName})`)

            let gqlVariables = {'url': workspace    .url}
            let projects = nexar.pageGen(gqlQuery2, gqlVariables, 'end', (data) => data.desProjects)

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