#!/usr/bin/env python3
"""Re-run the reviewer on test pull requests and grade what it says.

Every run is a fresh, independent review and nothing is posted to the pull
requests. The result is a table of cases by variant, where 2/3 means the
reviewer passed that case in two of its three runs. It measures catches and
noise, because a setting that finds more usually also says more.

Usage: python evals/run_evals.py evals/review_cases.yaml
Needs: PR-Agent importable, OPENAI_KEY, GITHUB_TOKEN, GITHUB_REPOSITORY.
"""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MAX_PARALLEL_REVIEWS = 9
REVIEW_TIMEOUT_SECONDS = 300
# No posting, and no memory of earlier reviews, so the runs stay independent.
HEADLESS = ["--config.publish_output=false", "--pr_reviewer.persistent_finding_state=false"]


def findings_of(parsed):
    """Return the findings of a parsed review. Each one has a file and a line."""
    return parsed.get("review", {}).get("key_issues_to_review") or []


def finding_text(finding):
    return f"{finding.get('issue_header', '')}\n{finding.get('issue_content', '')}".lower()


def review_text(parsed):
    """Return the text the string grader searches: the findings and the tests verdict.

    A mention in the review's security paragraph does not count.
    """
    parts = [finding_text(finding) for finding in findings_of(parsed)]
    if str(parsed.get("review", {}).get("relevant_tests", "")).strip().lower() in ("no", "false"):
        parts.append("no relevant tests")
    return "\n".join(parts)


def matches(case, text):
    return any(str(needle).lower() in text for needle in case["match"])


def grade(case, parsed):
    """Return True or False, or None when no code grader applies to this case."""
    if case.get("grader") == "string_match":
        return matches(case, review_text(parsed))
    if case.get("grader") == "no_findings":
        return not findings_of(parsed)
    return None


def findings_off_the_list(cases, parsed):
    """Count findings no case covers. They may be real or noise, so a person has to look."""
    listed = [case for case in cases if case.get("grader") == "string_match"]
    return sum(
        1 for finding in findings_of(parsed)
        if not any(matches(case, finding_text(finding)) for case in listed)
    )


def find_pull_request(repo, branch, token):
    """Return the URL of the pull request for a branch: the open one, else the newest."""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pulls"
        f"?head={repo.split('/')[0]}:{branch}&state=all&per_page=100",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request) as response:
        pulls = json.load(response)
    if not pulls:
        raise SystemExit(f"No pull request found for branch {branch}")
    return max(pulls, key=lambda pull: (pull["state"] == "open", pull["number"]))["html_url"]


def run_review(pr_url, args, env):
    """Run one headless review. Return the parsed review, or None if the run failed."""
    with tempfile.TemporaryDirectory() as folder:
        output = Path(folder) / "review.json"
        command = [
            sys.executable, "-m", "pr_agent.cli", f"--pr_url={pr_url}",
            f"--json-output={output}", "review", *HEADLESS, *args,
        ]
        try:
            done = subprocess.run(
                command, env=env, capture_output=True, text=True, timeout=REVIEW_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired:
            print(f"A review of {pr_url} timed out", file=sys.stderr)
            return None
        if not output.exists():
            print(f"A review of {pr_url} failed (exit {done.returncode}):\n{done.stderr[-1500:]}", file=sys.stderr)
            return None
        return json.loads(output.read_text())


def render(suite, reviews):
    """Render {variant: {branch: [parsed reviews]}} as a Markdown report."""
    names = [variant["name"] for variant in suite["variants"]]
    groups = suite["pull_requests"]

    def completed(name, group):
        return [run for run in reviews[name][group["branch"]] if run is not None]

    lines = ["| Case | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    every_run = dict.fromkeys(names, 0)
    graded_cases = dict.fromkeys(names, 0)
    for group in groups:
        for case in group["cases"]:
            cells = []
            for name in names:
                results = [grade(case, run) for run in completed(name, group)]
                graded = [result for result in results if result is not None]
                if not graded:
                    cells.append("not graded")
                    continue
                cells.append(f"{sum(graded)}/{len(graded)}")
                graded_cases[name] += 1
                every_run[name] += all(graded)
            lines.append(f"| {case['id']} | " + " | ".join(cells) + " |")

    def row(label, cell):
        lines.append(f"| {label} | " + " | ".join(cell(name) for name in names) + " |")

    def per_review(name, value):
        values = [value(group, run) for group in groups for run in completed(name, group)]
        return sum(values) / len(values) if values else 0

    row("**Passed every run**", lambda name: f"**{every_run[name]} of {graded_cases[name]}**")
    row("Findings per review", lambda name: f"{per_review(name, lambda group, run: len(findings_of(run))):.1f}")
    row("Findings no case covers", lambda name: f"{per_review(name, lambda group, run: findings_off_the_list(group['cases'], run)):.1f}")
    row("Tokens per review", lambda name: f"{per_review(name, lambda group, run: run.get('usage', {}).get('total_tokens', 0)):,.0f}")

    expected = suite["runs"] * len(groups)
    runs = ", ".join(f"{name} {sum(len(completed(name, group)) for group in groups)}/{expected}" for name in names)
    lines += [
        "",
        f"Completed runs: {runs}. Pull requests: " + ", ".join(group["branch"] for group in groups) + ".",
        "",
        "A finding no case covers may be real or noise. Check the raw reviews in the run's artifact.",
    ]
    return "\n".join(lines)


def main(path):
    import yaml  # ships with PR-Agent; imported here so the grader tests need nothing

    suite = yaml.safe_load(Path(path).read_text())
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    env = {
        **os.environ,
        "OPENAI.KEY": os.environ["OPENAI_KEY"],
        "GITHUB.USER_TOKEN": token,
        "GITHUB.DEPLOYMENT_TYPE": "user",
    }

    urls = {group["branch"]: find_pull_request(repo, group["branch"], token) for group in suite["pull_requests"]}
    jobs = [
        (variant["name"], branch, [*suite.get("settings", []), *variant["args"]])
        for variant in suite["variants"]
        for branch in urls
        for _ in range(suite["runs"])
    ]
    with ThreadPoolExecutor(MAX_PARALLEL_REVIEWS) as pool:
        results = list(pool.map(lambda job: run_review(urls[job[1]], job[2], env), jobs))

    reviews = {variant["name"]: {branch: [] for branch in urls} for variant in suite["variants"]}
    for (name, branch, _), review in zip(jobs, results):
        reviews[name][branch].append(review)

    # Keep the raw reviews, so a surprising score can be checked against what was said.
    output = Path(os.environ.get("EVALS_OUTPUT", "evals-output"))
    output.mkdir(exist_ok=True)
    (output / "reviews.json").write_text(json.dumps(reviews, indent=2))

    report = render(suite, reviews)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("## Review evals\n\n" + report + "\n")

    # A low score is a measurement, not a broken build. Fail only if nothing ran.
    return 0 if any(review is not None for review in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "evals/review_cases.yaml"))
