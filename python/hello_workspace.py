import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AltiumClient'))

from standaloneApiClient import StandaloneAltiumClient

if __name__ == '__main__':
    # *** Paste your Personal Access Token and Workspace URL here. No token? Visit https://developer.altium.com ***
    PAT = '...'
    WORKSPACE_URL = '...'
    query = '''
        query Projects {
            desProjects {
                nodes {
                    name
                    description
                    id
                    updatedAt
                    variantCount
                    url
                }
            }
          }'''

    response = StandaloneAltiumClient.execute_query(PAT, WORKSPACE_URL, query)

    print('Altium 365 API - Hello Workspace! - First project...\n======================================================================\n')
    if response['data']['desProjects']['nodes']:
        first_project = response['data']['desProjects']['nodes'][0]
        print(f'        name: {first_project["name"]}\n'
              f' description: {first_project["description"]}\n'
              f'          id: {first_project["id"]}\n'
              f'last updated: {first_project["updatedAt"]}\n'
              f'  # variants: {first_project["variantCount"]}\n'
              f' project URL: {first_project["url"]}\n======================================================================')
    else:
        print(f'No projects found in your workspace: {workspaceUrl}')