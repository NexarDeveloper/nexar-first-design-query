import os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, '..', '..', 'AltiumClient'))
from apiClient import AltiumClient

from workspace import query_workspace_DesWorkspaceInfos
from project import query_project_desProjects
from project import query_project_desProjectById

sys.path.append(os.path.join(SCRIPT_DIR, '..', '..', 'Helpers'))
from utils import print_delimiter_1
from utils import print_delimiter_2
from utils import print_nested

if __name__ == '__main__':

    print("Altium 365 platform-api-first-query")
    print_delimiter_1()
    
    clientId = None
    clientSecret = None
    refreshToken = None

    pat = os.environ.get('A365_PAT')
    
    if pat is None:
        clientId = os.environ.get('A365_CLIENT_ID')
        clientSecret = os.environ.get('A365_CLIENT_SECRET')
        refreshToken = os.environ.get('A365_REFRESH_TOKEN')
        if any(v is None for v in (clientId, clientSecret, refreshToken)):
            sys.exit("Missing environment variable(s). Please set A365_PAT or the triplet A365_CLIENT_ID / A365_CLIENT_SECRET / A365_REFRESH_TOKEN then retry.")
    
    client = AltiumClient(clientId, clientSecret, refreshToken, pat, ["design.domain", "user.access", "offline_access"])

    workspaces = client.get_query(query_workspace_DesWorkspaceInfos)["desWorkspaceInfos"]
    grid_prefix = "grid:global::platform:workspace/"
    for workspace in workspaces:
        if not client.token_workspace_scope_match(workspace["workspaceId"].removeprefix(grid_prefix)):
            continue
            
        variables = {
            'url': workspace["url"]
        }
        client.api_url = workspace["location"]["apiServiceUrl"]
        print(f'projects for workspace: {workspace["name"]} ({client.api_url})')
        print_delimiter_1()

        first_project = None
        for page in client.NodeIter(query_project_desProjects, variables, lambda x: x["desProjects"]):
            for project in page:
                if first_project is None:
                    first_project = project
                    
                print(f'Project Id: {project["id"]}')
                print(f'Name: {project["name"]}')
                print(f'Description: {project["description"]}')
                print()
                print_delimiter_2()

        if first_project is not None:
            print(f'Fetching details of the first project: {first_project["name"]}\n')
            print_delimiter_1()
            
            variables = {
                'id': first_project["id"]
            }
            
            project_details = client.get_query(query_project_desProjectById, variables)["desProjectById"]
            if project_details is not None:
                print_nested(project_details)
        