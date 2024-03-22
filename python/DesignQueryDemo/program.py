'''Example query for workspace info.'''
import os 

from nexarClient import NexarClient

gqlQuery = '''
query Workspaces {
    desWorkspaces {
      url
      name
      description
      location {
        apiServiceUrl
      }
    }
  }'''

gqlQuery2 = '''
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

if __name__ == '__main__':

    clientId = os.environ['NEXAR_CLIENT_ID']
    clientSecret = os.environ['NEXAR_CLIENT_SECRET']
    nexar = NexarClient(clientId, clientSecret, ['design.domain', 'user.access', 'offline_access'])

    workspaces = nexar.get_query(gqlQuery)['desWorkspaces']
    for workspace in workspaces:
        variables = {
            'url': workspace['url']
        }
        nexar.api_url = workspace['location']['apiServiceUrl']
        print(f'projects for workspace: {workspace["name"]} ({nexar.api_url})')

        for page in nexar.NodeIter(gqlQuery2, variables, lambda x: x['desProjects']):
            for project in page:
                print(f'Project Id: {project["id"]}')
                print(f'Name: {project["name"]}')
                print(f'Description: {project["description"]}')
                print()
