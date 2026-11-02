import unittest

from run_evals import findings_off_the_list, grade, render, review_text

TOKEN = {"id": "live-token", "grader": "string_match", "match": ["tk_live_", "Credential"]}
CLEAN = {"id": "clean-change", "grader": "no_findings"}
SUITE = {
    "runs": 3,
    "variants": [{"name": "defaults", "args": []}],
    "pull_requests": [
        {"branch": "demo", "cases": [TOKEN]},
        {"branch": "clean", "cases": [CLEAN]},
    ],
}


def review(*headers, tests="Yes", security=""):
    return {
        "review": {
            "key_issues_to_review": [{"issue_header": h, "issue_content": ""} for h in headers],
            "relevant_tests": tests,
            "security_concerns": security,
        },
        "usage": {"total_tokens": 100},
    }


class GradeTest(unittest.TestCase):
    def test_string_match_ignores_case(self):
        self.assertTrue(grade(TOKEN, review("An embedded credential")))
        self.assertFalse(grade(TOKEN, review("Stale results")))

    def test_security_paragraph_does_not_count(self):
        self.assertFalse(grade(TOKEN, review("Stale results", security="a credential")))

    def test_no_tests_verdict_is_searchable(self):
        self.assertIn("no relevant tests", review_text(review(tests="No")))

    def test_no_findings_passes_only_when_silent(self):
        self.assertTrue(grade(CLEAN, review()))
        self.assertFalse(grade(CLEAN, review("A nit")))

    def test_other_graders_are_not_graded(self):
        self.assertIsNone(grade({"id": "slow-query", "grader": "human"}, review()))


class OffTheListTest(unittest.TestCase):
    def test_counts_findings_no_case_covers(self):
        parsed = review("Embedded credential", "Stale results", "Inactive projects")
        self.assertEqual(findings_off_the_list([TOKEN, CLEAN], parsed), 2)


class ReportTest(unittest.TestCase):
    def report(self, demo, clean):
        return render(SUITE, {"defaults": {"demo": demo, "clean": clean}})

    def test_counts_runs_and_cases_that_passed_every_run(self):
        report = self.report(
            [review("tk_live_"), review("tk_live_"), review("other")],
            [review(), review(), review()],
        )
        self.assertIn("| live-token | 2/3 |", report)
        self.assertIn("| clean-change | 3/3 |", report)
        self.assertIn("**1 of 2**", report)

    def test_failed_runs_are_left_out_and_reported(self):
        report = self.report([review("tk_live_"), None, None], [review(), review(), review()])
        self.assertIn("| live-token | 1/1 |", report)
        self.assertIn("defaults 4/6", report)

    def test_reports_findings_and_tokens(self):
        report = self.report([review("tk_live_", "other"), None, None], [review("a nit"), None, None])
        self.assertIn("| Findings per review | 1.5 |", report)
        self.assertIn("| Findings no case covers | 1.0 |", report)
        self.assertIn("| Tokens per review | 100 |", report)


if __name__ == "__main__":
    unittest.main()
