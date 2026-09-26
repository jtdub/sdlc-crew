# Infrastructure rules

These rules apply when a work item creates or changes infrastructure: a server, a
database, a container, a cloud service, a DNS record, a domain, a deploy pipeline, or
a hosting plan. The architect puts the applicable rules in the plan. The engineer
follows them. QA checks them.

## Before the plan

1. Ask what the app must survive: how much data loss is acceptable, and how long the
   app can be down. Two questions in plain words. The answers set the backup and the
   hosting choice.
2. Estimate the monthly cost of each option. Put the estimate next to the option.
   State the free tier and what happens when the free tier ends.
3. Prefer a managed service over a server that the person must maintain, unless the
   person asks for a server.
4. Prefer the platform that the person already pays for or knows.

## In the design

1. Infrastructure is code. Write it in a file in the repository: a Dockerfile, a
   `compose.yaml`, a Terraform or OpenTofu module, a Pulumi program, a platform config
   such as `fly.toml`, `render.yaml`, `vercel.json`, or a GitHub Actions workflow. A
   change made only in a web console is not done.
2. Least privilege. Each token, role, or service account gets only the access that
   the app needs. No admin token in an app.
3. Secrets come from the platform's secret store or from environment variables. Never
   from a file in the repository.
4. HTTPS by default. A custom domain gets a certificate from the platform.
5. One command starts the app locally, and it is in `project.run_command`.
6. Backups: a database has an automatic backup, and the plan says how to restore it.
7. A rollback path: the plan says how to return to the previous version in one step.
8. Logs and one health check: the app writes errors to a log the person can read, and
   the platform checks one URL to know the app is up.

## WARNING gates

Before each of these actions, state the risk in one sentence, then ask, then wait:

- An action that deletes a database, a volume, a bucket, or a server.
- An action that creates a resource with a monthly cost, or changes a plan.
- An action that changes DNS or a domain.
- The first deploy to a URL that other people use.

Write the gate in this form: "WARNING: <what can be lost or what it costs>. <the
question>."

## What QA checks

| Check | Priority |
|---|---|
| A resource is created without a file in the repository that defines it | SHOULD FIX |
| A token or a role has more access than the app uses | MUST FIX |
| A database has no automatic backup | SHOULD FIX |
| The plan has no rollback step | SHOULD FIX |
| A public URL serves over plain HTTP | SHOULD FIX |
| The deploy step has no health check | CONSIDER FIXING |
| The cost of a new resource is not in the plan | SHOULD FIX |
