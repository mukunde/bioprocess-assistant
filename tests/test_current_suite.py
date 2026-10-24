"""Discovery must replace a historical fixture without dropping any safeguards."""
import unittest
from tests import CurrentSuiteLoader
from tests import test_v03b_evaluation as historical
from tests import v03b_review_gate_suite as current


class CurrentSuiteTests(unittest.TestCase):
    def test_all_eleven_historical_case_names_are_preserved(self):
        loader=CurrentSuiteLoader()
        expected=loader.getTestCaseNames(historical.V03bEvaluationTests)
        self.assertEqual(len(expected),11)
        self.assertEqual(loader.getTestCaseNames(current.CurrentV03bEvaluationTests),expected)
        suite=loader.loadTestsFromModule(historical)
        self.assertEqual(suite.countTestCases(),11)
        self.assertTrue(all(type(case) is current.CurrentV03bEvaluationTests for case in suite))

    def test_only_obsolete_fixture_is_overridden(self):
        name='test_unreviewed_input_blocks_runtime_and_real_output'
        old=historical.V03bEvaluationTests;new=current.CurrentV03bEvaluationTests
        self.assertIsNot(getattr(old,name),getattr(new,name))
        for case in unittest.TestLoader().getTestCaseNames(old):
            if case!=name:self.assertIs(getattr(old,case),getattr(new,case))
