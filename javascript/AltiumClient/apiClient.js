const { URLSearchParams } = require("url");
const http = require("http");
const https = require("https");
const crypto = require("crypto");
const { spawn } = require("child_process");
const os = require("os");

a365Page = (title, message) => `
    <html>
    <head>
      <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel="stylesheet" type="text/css">
      <title>${title}</title>
      <style>
        html {
          height: 100%;
          background-image: linear-gradient(to right, #000b24, #001440);
        }
        body {
          color: #ffffff;
        }
        .center {
          width: 100%;
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
        }
        .title {
          font-family: Montserrat, sans-serif;
          font-weight: 400;
        }
        .normal {
          font-family: Montserrat, sans-serif;
          font-weight: 300;
        }
      </style>
    </head>
    <body>
      <div class="center">
        <h1 class="title">${title}</h1>
        <p class="normal">${message}.</p>
      </div>
    </body>
    </html>
    `;
const TOKEN_OPTIONS = {
  hostname: "auth.altium.com",
  path: "/connect/token",
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
};

function launchBrowser(auth_request) {
  switch (os.platform()) {
    case "win32":
      return spawn("start", ['""', `"${auth_request}"`], { shell: true });
    case "darwin":
      return spawn("open", [`"${auth_request}"`], { shell: true });
    default:
      return spawn("xdg-open", [`"${auth_request}"`], { shell: true });
  }
}

function decodeJWT(jwt) {
  let json = JSON.parse(
    Buffer.from(
      jwt.split(".")[1].replace("-", "+").replace("_", "/"),
      "base64"
    ).toString("binary")
  );
  return json;
}

function getRequest(options, data) {
  return new Promise((resolve, reject) => {
    let req = https.request(options, (res) => {
      const contentType = res.headers["content-type"];

      let error;
      if (res.statusCode !== 200) {
        error = new Error(
          "Request Failed.\n" +
            `Status Code: ${res.statusCode} ${res.statusMessage}`
        );
      } else if (!/^application\/graphql-response|json/.test(contentType)) {
        error = new Error(
          "Invalid content-type.\n" +
            `Expected application/json but received ${contentType}`
        );
      }
      if (error) {
        console.error(error.message);
        // Consume response data to free up memory
        res.resume();
        return;
      }

      let rawData = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => (rawData += chunk));
      res.on("end", () => resolve(JSON.parse(rawData)));
    });
    req.on("error", (err) => reject(err));
    req.write(data);
    req.end();
  });
}

class AltiumClient {
  #exp;
  #accessToken;
  #pat;
  #scope;
  hostName = "usw2.dev-365.altium.com"; //"dev-365.altium.com/"; // "eur.365.altium.com";
  static scopes = {
    supply: "supply.domain",
    design: "openid profile email design.domain user.access offline_access",
  };

  /**
   * Client for the Altium 365 API to manage authorization and requests.
   * @param {string} pat - personal access token.
   * @param {string} [scope] - the resources required for authorization
   */

  constructor(pat, scope = AltiumClient.scopes.supply) {
    this.#pat = pat;
    this.#scope = scope;
  }

  set host(name) {
    this.hostName = name.replace(/^https:\/\//, "")
                        .replace(/\/graphql$/, "")
                        .replace(/\/gateway$/, "")
                        .replace(/\/napi$/, "")
                        .replace(/\/svc$/, "");
  }

  #refreshToken(token) {
    if ("refresh_token" in token) {
      const data = new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: token.refresh_token,
        client_id: this.#pat,
        scope: this.#scope,
      });

      return getRequest(TOKEN_OPTIONS, data.toString());
    }

    return new Promise(() => ""); // this.#getAccessToken(this.#id, this.#secret, this.#scope);
  }

  #checkTokenExp() {
    this.#exp =
      this.#exp ||
      this.#accessToken.then(
        (token) => decodeJWT(token)?.exp * 1000
      );

    return this.#exp.then((exp) => {
      if (exp < Date.now() + 300000) {
        //token is expired ... or will be in less than 5 minutes (300000 msec)
        this.#exp = undefined;
        this.#accessToken = this.#accessToken.then((token) =>
          this.#refreshToken(token)
        );
      }
      return this.#accessToken;
    });
  }

  /**
   * Make a request to the Altium 365 API
   * @param {string} gqlQuery - graphQL string containing the query/mutation.
   * @param {object} variables - key/value pairs for variables used in the gqlQuery.
   * @returns {object} - The Altium 365 API response
   */

  query(gqlQuery, path, variables) {
      this.#accessToken =
          this.#accessToken ||
          Promise.resolve(this.#pat);
      
    return this.#checkTokenExp().then((token) => {
      const options = {
        hostname: this.hostName,
        path: path,
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
      };
      const data = {
        query: gqlQuery,
        variables: variables,
      };

      return getRequest(options, JSON.stringify(data));
    });
  }

  /**
   * Iterable for a graphQL Type implementing a node interface.
   * NB: the query must include a variable to set the the cursor and the pageInfo field on the Type.
   * @async
   * @generator
   * @param {string} pageKey - graphQL variable name for setting the cursor: desProjects(after: $pageKey).
   * @param {function} pageSelect - return from response the type with node interface: (data) => data.desProjects
   * @yields {object} - a page of the graphQL Type implementing a node interface
   */

  async *pageGen(gqlQuery, path, gqlVariables, pageKey, pageSelect) {
    let pageInfo = { hasNextPage: true };
    while (pageInfo.hasNextPage) {
      const response = await this.query(gqlQuery, path, gqlVariables);

      pageInfo = pageSelect(response.data).pageInfo;
      gqlVariables[pageKey] = pageInfo.endCursor;

      yield pageSelect(response.data).nodes;
    }
  }
}

module.exports = { AltiumClient };
