query_project_desProjects = '''
query Projects($url: String!, $end: String) {
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
  }'''

query_project_desProjectById = '''
query ProjectDataAndParameters($id: ID!) {
    desProjectById (id: $id) {
      description
      id
      name
      projectType
      updatedAt
      url
      createdAt
      design {
        releases {
          totalCount
        }
        variants {
          name
        }
      }
      latestRevision {
        author
        createdAt
        message
        revisionId
      }
      revisions {
        totalCount
      }
      parameters {
        name
        value
      }
    }
  }'''
