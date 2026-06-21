import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "benchmarks" / "prompt-quality-benchmarks.json"
EVALUATOR_PATH = ROOT / "tools" / "evaluate_quality_benchmarks.py"
EXPECTED_DOMAINS = {"backend", "frontend", "ai", "devops", "architecture"}
EXPECTED_METRICS = {
    "requirement_omission_reduction",
    "output_quality_improvement",
    "revision_request_reduction",
    "productivity_improvement",
}


def load_benchmarks():
    return json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_quality_benchmarks", EVALUATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QualityBenchmarkTest(unittest.TestCase):
    def test_benchmark_set_covers_required_domains_and_metrics(self):
        payload = load_benchmarks()

        self.assertEqual("1.0.0", payload["schemaVersion"])
        self.assertEqual(EXPECTED_DOMAINS, {case["domain"] for case in payload["cases"]})
        self.assertEqual(EXPECTED_METRICS, {metric["id"] for metric in payload["successMetrics"]})
        self.assertEqual("neutral", payload["evaluation"]["target"])
        self.assertEqual("python tools/evaluate_quality_benchmarks.py", payload["evaluation"]["localCommand"])

    def test_each_benchmark_defines_sections_and_quality_expectations(self):
        payload = load_benchmarks()

        for case in payload["cases"]:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["sourceText"])
                self.assertTrue(case["expectedIntent"])
                self.assertTrue(case["expectedCategory"])
                self.assertGreaterEqual(len(case["minimumSections"]), 3)
                expectations = case["qualityExpectations"]
                self.assertLessEqual(expectations["sourceMax"], 40)
                self.assertGreaterEqual(expectations["optimizedMin"], 90)
                self.assertGreaterEqual(expectations["improvementMin"], 50)

    def test_current_optimizer_passes_quality_benchmark_gate(self):
        evaluator = load_evaluator()
        summary = evaluator.evaluate_benchmarks(load_benchmarks())

        self.assertTrue(summary["passed"], summary["results"])
        self.assertEqual(len(load_benchmarks()["cases"]), summary["benchmarkCount"])


if __name__ == "__main__":
    unittest.main()
