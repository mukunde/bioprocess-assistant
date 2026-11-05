# Repository collaboration instructions

## Git operations

The user must explicitly validate each commit and each push before it is made.
The user normally performs these operations themselves unless they explicitly
instruct the assistant otherwise. Do not commit, amend, push or publish changes
automatically. Preparing local edits, tests and reviewable diffs is authorized
within the task scope.

Keep commit/push authorization rules in this file only; other documentation may
refer here instead of repeating them. Do not include credentials, source PDFs,
model weights or private raw experiment artifacts in Git. Stage explicit file
lists rather than the entire workspace.

## Documentation

Write project documentation in English. Preserve original source quotations and
human decision quotations verbatim, including their original language. Keep frozen
review records, claims, evidence and provenance fields unchanged. If translated
documentation is covered by a manifest, update only its documentation digest;
preserve all source, claim and human-decision hashes. Keep historical results and
their dates distinct from current implementation status.

## Markdown checks

Install [prek](https://prek.j178.dev/installation/) and run `prek install` from
the repository root. The hook uses Python 3 from PATH. Run `prek run --all-files`
to check the tracked Markdown files manually. Keep delivery and approval notes
in pull requests or local work logs.

The Markdown delivery baseline records existing occurrences by file, exact
trimmed line and count. Remove entries as the corresponding text is cleaned up.
Treat additions to the baseline as policy changes requiring review.

## Editorial style

Use the root README to explain the problem and audience, show the demo, and
link to setup, architecture, sources, evaluation, limitations, and credits.
Keep evidence easy to inspect. Move full procedures and dated results to
linked documents.
[README structure](https://www.agentroomai.com/insights/github-readme-template-ai-projects) ·
[Portfolio evidence](https://www.agentroomai.com/insights/build-ai-project-portfolio)

Use direct verbs, short paragraphs, and sentence case for new prose. Lead with
the reader's next action. Use the serial comma and omit periods and colons at
the ends of headings. Keep original quotations and source text intact.
[Microsoft writing guidance](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice)

The root README hook checks the section order, heading punctuation, and a
project budget of 160 lines. Review clarity, sentence case, and the relevance
of evidence when reviewing a change.
