VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Sub runDesignExample()

    ' Declare necessary objects and variables
    Dim url As String
    Dim workSpaceQuery As String
    Dim xmlhttp As Object
    Dim json As Object
    Dim i As Integer
    Dim filePath As String
    Dim apikey As String
    Dim jsonResponse As Object
    Dim httpRequest As Object
    Dim id As String, name As String, apiUrl As String
    
    ' CHANGE FILEPATH TO YOUR FILEPATH OF YOUR API KEY
    filePath = "filePath\apikey.txt"
    
    ' Open the text file and read the API key
    apikey = ReadApiKeyFromFile(filePath)
    
    ' Set up the URL (replace with your API endpoint)
    url = "https://api.nexar.com/graphql"
    
    ' Set up the GraphQL query as a JSON string
    workSpaceQuery = "{ ""query"": ""query Workspaces { desWorkspaceInfos { url name description location { apiServiceUrl } } }"" }"
    
    Set httpRequest = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    ' Initialize and send the HTTP POST request
    With httpRequest
        .Open "POST", url, False  ' Set the HTTP method to POST and the URL
        .setRequestHeader "Content-Type", "application/json"  ' GraphQL requires JSON payload
        
        .setRequestHeader "Authorization", "Bearer " & apikey

        ' Send the request with the query in the body
        .Send workSpaceQuery
    End With
    
    responseText = httpRequest.responseText
    
    ' Parse the JSON response
    Set jsonResponse = JsonConverter.ParseJson(responseText)
    
    Dim workspaceResponseData As Object
    Set workspaceResponseData = jsonResponse("data")("desWorkspaceInfos")
    
    ' Start writing data to Excel (starting from cell A1)
    i = 1  ' Start at row 1
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Sheet1") ' Use the desired sheet
    
    ' Write headers
    ws.Cells(1, 1).Value = "Workspace Name"
    ws.Cells(1, 2).Value = "Description"
    ws.Cells(1, 3).Value = "URL"
    
    ' Iterate over the items array
    i = 2 ' Start writing to row 2
    For Each workspace In workspaceResponseData

        name = workspace("name")
        description = workspace("description")
        apiUrl = workspace("url")
        
        ' Write id, name, and url to Excel
        ThisWorkbook.Sheets("Sheet1").Cells(i, 1).Value = name
        ThisWorkbook.Sheets("Sheet1").Cells(i, 2).Value = description
        ThisWorkbook.Sheets("Sheet1").Cells(i, 3).Value = apiUrl
        
        i = i + 1 ' Increment row
    Next workspace
    
    MsgBox "Data written to cells successfully!"
    
    ' Clean up
    Set httpRequest = Nothing
    Set jsonResponse = Nothing
    Set workspaceResponseData = Nothing
End Sub

Function ReadApiKeyFromFile(filePath As String) As String
    Dim fileNum As Integer
    Dim apikey As String
    fileNum = FreeFile ' Get the next available file number

    ' Open the file for input (reading)
    Open filePath For Input As fileNum
    
    ' Read the API key (assuming it's on the first line)
    Line Input #fileNum, apikey
    
    ' Close the file
    Close fileNum
    
    ' Return the API key
    ReadApiKeyFromFile = apikey
End Function

