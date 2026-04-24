import requests

class StandaloneAltiumClient:
    pass

    def execute_query(pat, workspace_url, query):
        """Runs the A365 API query using the given PAT for the specificed workspace."""
        s = requests.session()
        s.keep_alive = False
        workspace_url_stripped = workspace_url.rstrip('/')
        api_url = f'{workspace_url_stripped}/svc/napi/gateway/graphql'

        try:
            r = s.post(
                api_url,
                json={'query': query},
                headers={'Authorization': f'Bearer {pat}'}
            )
            response = r.json()

        except Exception as e:
            print(e)
            raise Exception('Error while getting API response. Make sure you provide a valid Personal Access Token (PAT)')

        if 'errors' in response:
            for error in response['errors']: print(error["message"])
            raise SystemExit

        return response