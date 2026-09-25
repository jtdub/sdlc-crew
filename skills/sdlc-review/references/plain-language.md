# Plain language: how to explain a finding or a decision

The person who reads the plan, the questions, and the review is often not a software
developer. Write for them. The rules below apply to every message to the person, to
the plan, to the pull request body, and to every comment on a work item.

## Rules

1. Say what the person will notice first. Then say what the crew does about it. Put
   the technical name last, in parentheses, or leave it out.
2. Explain a term the first time it appears in a run. One sentence. Example:
   "A pull request is a page that shows the change and lets a person approve it."
3. Say why. A rule without a reason is a command. A reason lets the person decide.
4. Give the risk before the instruction. "This deletes the test database. Make a
   backup first."
5. One idea in each sentence. Twenty words or less.
6. Do not use these words with the person: leverage, utilize, robust, seamless,
   simply, just, obviously, trivial.
7. Do not blame. "The page shows an error when the list is empty" is better than
   "You did not handle the empty case".
8. When you ask a question, give options, say which one you recommend, and say why in
   the trade-off text.

## Terms that need one sentence for `person.experience: new`

| Term | One sentence |
|---|---|
| repository | The folder that holds the code and its full history. |
| branch | A separate line of work, so the main code stays safe until the change is ready. |
| commit | A saved step in the history, with a message that says what changed. |
| pull request | A page that shows a change and lets a person review and accept it. |
| merge | Accept a pull request, so its change becomes part of the main code. |
| test | A small program that checks that one part of the app works. |
| CI | A service that runs the tests on each change, so a broken change is caught early. |
| dependency | A library that the app uses, written by someone else. |
| environment variable | A setting that the app reads when it starts, used for secrets so they are not in the code. |
| migration | A script that changes the shape of the database to match new code. |
| API | The way one program talks to another. |
| deploy | Put a version of the app where people can use it. |
| rollback | Go back to the version before a change, when the change causes a problem. |
| least privilege | Give each account or service only the access that it needs. |

## Example

Not this:

> The endpoint lacks input validation and is vulnerable to injection.

This:

> A visitor can type something into the search box that runs commands on your
> database. The engineer will add a check that only accepts normal text. (Finding:
> the search endpoint has no input validation.)
