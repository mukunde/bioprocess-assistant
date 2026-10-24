"""Current fixture revision of eleven frozen v03b safeguards, with no skipped cases."""
from pathlib import Path
import tempfile
from unittest.mock import patch

from tests.test_v03b_evaluation import V03bEvaluationTests
from experiments.cytiva import v03b_evaluation as subject


class CurrentV03bEvaluationTests(V03bEvaluationTests):
    def test_unreviewed_input_blocks_runtime_and_real_output(self):
        verification=subject.verify()
        for existing in (False,True):
            with self.subTest(existing_output=existing),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);package=root/subject.PACKAGE;package.mkdir(parents=True)
                for name in ('candidate.json','questions.json','references.json'):
                    (package/name).write_bytes((subject.ROOT/subject.PACKAGE/name).read_bytes())
                candidate=subject.read(package/'candidate.json')
                output=root/candidate['run_directory']
                if existing:
                    output.mkdir(parents=True)
                    (output/'completed.json').write_bytes(b'{"status":"completed","sentinel":"preserve"}\n')
                before={p.relative_to(output).as_posix():p.read_bytes() for p in output.rglob('*') if p.is_file()} if output.exists() else {}
                review=root/'review.json'
                subject.dump(review,{'manifest_sha256_lf':verification['preparation_manifest_sha256_lf'],
                                     'method_lock_sha256_lf':verification['method_lock_sha256_lf'],'decisions':[]})
                # The real freeze is verified above; only the temporary fixture's
                # absent full source tree is substituted. The actual review gate runs.
                with patch.object(subject,'verify',return_value=verification),patch.object(subject,'make_runtime') as factory:
                    with self.assertRaisesRegex(ValueError,'twelve questions'):
                        subject.run(review,root=root)
                    factory.assert_not_called()
                self.assertEqual(output.exists(),existing)
                after={p.relative_to(output).as_posix():p.read_bytes() for p in output.rglob('*') if p.is_file()} if output.exists() else {}
                self.assertEqual(after,before)
