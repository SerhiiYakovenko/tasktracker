# Review evals

Is the reviewer catching what we care about, and what does a setting change cost in noise?

`run_evals.py` re-runs the reviewer on known test pull requests, several times, and grades each review against the cases in `review_cases.yaml`. Nothing is posted to the pull requests, and the runs do not see each other's findings, so each one is an independent sample.

The result is a table in the job summary:

- `2/3` means the reviewer passed that case in two of its three runs.
- **Passed every run** counts the cases it passed every time, which is the number your team will feel.
- **Findings per review** and **Findings no case covers** are the cost side. A setting that finds more usually also says more.

The raw reviews are kept as a run artifact, so you can check a surprising score against what was actually said.

## The test pull requests

They are found by branch name and only read, so they can be closed.

- `demo/add-search`: a search feature with ten known issues.
- `eval/cross-tenant-lookup`: a real production finding, an unscoped lookup that could reach another tenant's data, rebuilt in this app.
- `eval/clean-change`: a correct small change with a test, where silence is the right answer.

## Add a case

When a real review misses something, add a pull request that reproduces it, then a case:

```yaml
- id: live-token
  incident: a live-looking token merged to production
  expect: flag the hardcoded token constant
  grader: string_match
  match: [tk_live_, ADMIN_BYPASS, credential]
```

`string_match` passes if any of those strings appears in a finding. Only findings count, because each one has a file and a line someone can act on. `no_findings` passes if the review has none.

## Measure a setting

Add a `variants` entry with the flags you want to compare, then read the columns side by side. Each flag is the same one you could type after `/review` in a comment.

## Limits

- `string_match` is the cheapest grader and the bluntest. A finding worded differently fails it. When output and eval disagree, check the eval first. The first version of this suite searched the whole review, and it showed no difference between settings. The eval was wrong, not the reviewer.
- A finding no case covers may be real or noise. Counting it is not judging it; a person, or a model grader, has to look.
- Three pull requests is a demonstration. A real suite takes 20 to 50 cases from your own incidents.
- A low score does not fail the build. Evals measure the reviewer; your CI enforces the merge.
- Every run calls the model: 3 pull requests x 2 variants x 3 runs is 18 reviews.
