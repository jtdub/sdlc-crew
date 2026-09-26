# Security checklist

QA and the `sdlc-review` skill run this list on every pull request. It is a subset of
the OWASP Application Security Verification Standard (ASVS) level 1, plus the checks
that matter most for a small project. Each item gives a priority for the finding.

## Secrets

| Check | Priority |
|---|---|
| The diff adds a password, an API key, a token, or a private key in a file | MUST FIX |
| The diff adds a `.env` file, a credentials file, or a key file that `.gitignore` does not exclude | MUST FIX |
| A secret is read from a config file in the repository instead of an environment variable | SHOULD FIX |

Run a secret scan when a tool is installed: `gitleaks detect --no-git -s .` or
`trufflehog filesystem .`. Otherwise grep the diff for `password`, `secret`, `token`,
`api_key`, `BEGIN PRIVATE KEY`, and long random strings.

## Input and output

| Check | Priority |
|---|---|
| A database query, a shell command, or a file path is built from user input by string concatenation | MUST FIX |
| User input is put into an HTML page without escaping | MUST FIX |
| A request that changes data has no check of who sent it | MUST FIX |
| A file upload has no limit on type or size | SHOULD FIX |
| An error message shows a stack trace, a file path, or a query to the user | SHOULD FIX |

## Access

| Check | Priority |
|---|---|
| A page or an API that shows private data has no login check | MUST FIX |
| A user can read or change another user's data by changing an ID in the URL | MUST FIX |
| A new admin function has no role check | MUST FIX |
| Passwords are stored without a slow hash such as bcrypt, scrypt, or Argon2 | MUST FIX |
| A session cookie has no `HttpOnly`, `Secure`, or `SameSite` flag | SHOULD FIX |

## Dependencies

| Check | Priority |
|---|---|
| The diff adds a dependency with a known critical or high vulnerability | MUST FIX |
| The diff adds a dependency without a version pin or a lock file | SHOULD FIX |
| The diff adds a dependency that does one small thing the standard library already does | CONSIDER FIXING |

Run the ecosystem audit when the tool is available: `npm audit`, `pip-audit`,
`uv pip audit`, `bundle audit`, `cargo audit`, `govulncheck ./...`, `composer audit`.

## Transport and configuration

| Check | Priority |
|---|---|
| The app talks to a service over `http://` where `https://` is available | SHOULD FIX |
| Debug mode is on in a production configuration | MUST FIX |
| CORS allows every origin on an API that needs login | SHOULD FIX |
| A default password or a default admin account is created | MUST FIX |

## Data

| Check | Priority |
|---|---|
| Personal data is written to a log | SHOULD FIX |
| Personal data is stored that the feature does not need | CONSIDER FIXING |
| A delete has no confirmation and no way back, and the data matters | SHOULD FIX |

## How to report

Write each finding with `references/plain-language.md`. Say what a visitor or an
attacker can do, what the fix is, and the technical name in parentheses.
