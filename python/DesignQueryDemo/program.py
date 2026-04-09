'''Example query for workspace info.'''
import os, sys
#from ..AltiumClient.apiClient import AltiumClient
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, '..', 'AltiumClient'))
from apiClient import AltiumClient

gqlQuery = '''
query Workspaces {
    desWorkspaceInfos {
      workspaceId  
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

    pat = None
    clientId = None
    clientSecret = None
    refreshToken = None
    
    option = input("To use A365 API, select onf of the following token options\n"
          "(1) For Personal Access Token, enter 1 (requires A365_PAT env var)\n"
          "(2) For access token generation using Refresh Token, enter 2 (requires A365_CLIENT_ID, A365_CLIENT_SECRET and A365_REFRESH_TOKEN env vars)\n")
    
    if option == "1":
        pat = os.environ['A365_PAT']
    elif option == "2":
        clientId = os.environ['A365_CLIENT_ID']
        clientSecret = os.environ['A365_CLIENT_SECRET']
        refreshToken = os.environ['A365_REFRESH_TOKEN']
    else:
        sys.exit("Invalid option.")
    
    client = AltiumClient(clientId, clientSecret, refreshToken, pat, ['design.domain', 'user.access', 'offline_access'])

    workspaces = client.get_query(gqlQuery)['desWorkspaceInfos']
    grid_prefix = "grid:global::platform:workspace/"
    for workspace in workspaces:
        if not client.token_workspace_scope_match(workspace['workspaceId'].removeprefix(grid_prefix)):
            continue
            
        variables = {
            'url': workspace['url']
        }
        client.api_url = workspace['location']['apiServiceUrl']
        print(f'projects for workspace: {workspace["name"]} ({client.api_url})')

        for page in client.NodeIter(gqlQuery2, variables, lambda x: x['desProjects']):
            for project in page:
                print(f'Project Id: {project["id"]}')
                print(f'Name: {project["name"]}')
                print(f'Description: {project["description"]}')
                print()
