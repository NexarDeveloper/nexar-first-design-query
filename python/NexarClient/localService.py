"""Handler for local HTTP server to support OAuth2 Authorization Code Flow."""
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


def NexarPage(title, message):
  return f"""
<html>
<head>
  <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel="stylesheet" type="text/css">
  <title>{title}</title>
  <style>
    html {{
      height: 100%;
      background-image: linear-gradient(to right, #000b24, #001440);
    }}
    body {{
      color: #ffffff;
    }}
    .center {{
      width: 100%;
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
    }}
    .title {{
      font-family: Montserrat, sans-serif;
      font-weight: 400;
    }}
    .normal {{
      font-family: Montserrat, sans-serif;
      font-weight: 300;
    }}
  </style>
</head>
<body>
  <div class="center">
    <h1 class="title">{title}</h1>
    <p class="normal">{message}.</p>
  </div>
  <script>
    function autoClose(){{
        window.close();
    }}
    setTimeout(autoClose, 3000);
  </script>
</body>
</html>
"""

def handlerFactory(code, state):
    class MyHandler(BaseHTTPRequestHandler):
        def log_request(code='-', size='-'):
            pass

        def do_HEAD(s):
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            
        def do_GET(s):
            """Respond to a GET request."""
            o = urlparse(s.path)
            if (o.path != "/login"):
                return

            response = parse_qs(o.query)
            error = None
            if ("code" not in response):
                error = "Code not returned"
            elif ("state" not in response or response["state"][0] != state):
                error = "Unverified state"

            if (error is not None):
                s.send_response(400)
                s.send_header("Content-type", "text/html")
                s.end_headers()
                s.wfile.write(NexarPage("Authorization Failed!",error).encode())
                code.extend([None, error])
                return

            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write(NexarPage("Welcome to Nexar","You can now return to the application. This window will close soon.").encode())
            code.append(response["code"][0])

    return MyHandler
