import logging
import os

from NexarClient.nexarClient import NexarClient

def get_client(refresh_token = None):
    clientId = os.environ['NEXAR_CLIENT_ID']
    clientSecret = os.environ['NEXAR_CLIENT_SECRET']
    return NexarClient(clientId, clientSecret, ['design.domain', 'user.access', 'offline_access'], refresh_token=refresh_token)

workspacesQuery = '''
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

def library_query(workspaceUrl: str, pagination: str) -> str:
  return f'''
query library {{
  desLibrary(workspaceUrl: "{workspaceUrl}") {{
    components({pagination}){{
      pageInfo {{
        endCursor
        hasNextPage
      }}
      nodes {{
        id
        name
        details {{
          parameters {{
            type
            name
            value
          }}
        }}
      }}
    }}
  }}
}}
'''
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s - %(asctime)s - %(name)s - %(filename)s - %(lineno)d ]: %(message)s")

    nexar = get_client()

    workspaces = nexar.get_query(workspacesQuery)['desWorkspaces']
    workspace_name = os.environ['NEXAR_WORKSPACE_NAME']
    try:
      prod_workspace_url = [ workspace for workspace in workspaces if workspace['name'] == workspace_name ][0]['url']
    except IndexError as e:
      logging.error(f'Failed to find workspace with name {workspace_name}')
      logging.exception(e)
    else:
      result = nexar.get_query(library_query(prod_workspace_url, 'first: 100'))["desLibrary"]["components"]

      while (pageInfo:= result.get('pageInfo', {})):
        logging.debug('pageInfo', pageInfo)

        endCursor = pageInfo.get('endCursor')

        if pageInfo.get('hasNextPage', False) and endCursor is not None:
          break

        result = nexar.get_query(library_query(prod_workspace_url,f'after: "{endCursor}"'))["desLibrary"]["components"]
