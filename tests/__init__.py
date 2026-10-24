"""Current full suite; frozen historical test files remain unchanged."""
import importlib
import unittest
from pathlib import Path


class CurrentSuiteLoader(unittest.TestLoader):
    def loadTestsFromModule(self,module,pattern=None):
        if module.__name__ == 'tests.test_v03b_evaluation':
            from tests.v03b_review_gate_suite import CurrentV03bEvaluationTests
            return self.loadTestsFromTestCase(CurrentV03bEvaluationTests)
        return super().loadTestsFromModule(module,pattern=pattern)


def load_tests(loader,tests,pattern):
    # Standard `python -m unittest tests` and root discovery use this package hook.
    # Preserve every historical case name; replace only the obsolete fixture.
    root=Path(__file__).resolve().parents[1]
    current=CurrentSuiteLoader();suite=unittest.TestSuite()
    for path in sorted((root/'tests').rglob(pattern or 'test*.py')):
        module=importlib.import_module('.'.join(path.relative_to(root).with_suffix('').parts))
        suite.addTests(current.loadTestsFromModule(module,pattern=pattern))
    return suite
