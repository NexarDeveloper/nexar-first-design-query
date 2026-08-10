query_workspace_DesWorkspaceInfos = '''
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
