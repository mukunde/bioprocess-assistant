"""Static publication checks; no network or application inference."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pages_builder', ROOT / 'scripts/prepare_cytiva_video_site.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class FlowshotPagesTests(unittest.TestCase):
    def test_allowlist_navigation_and_original_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'site'
            result = builder.prepare(output)
            actual = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
            self.assertEqual(actual, set(result['files']))
            self.assertEqual(len(actual), 18)
            self.assertIn('href="flowshot/"', (output / 'index.html').read_text(encoding='utf-8'))
            html = (output / 'flowshot/index.html').read_text(encoding='utf-8')
            self.assertIn('href="../"', html)
            self.assertNotIn('not published', html)
            self.assertNotIn('LOCAL PILOT', html)
            for name in builder.FLOW_FILES:
                if name != 'index.html':
                    self.assertEqual((output / 'flowshot' / name).read_bytes(),
                                     (ROOT / 'media/cytiva-flowshot-pilot-v02' / name).read_bytes())
            for name in ('onboarding.mp4', 'onboarding.jpg'):
                self.assertEqual((output / 'assets' / name).read_bytes(),
                                 (ROOT / 'media/cytiva-onboarding-v05/exports' / name).read_bytes())

    def test_sepharose_player_uses_the_approved_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            builder.prepare(output)
            player = output / 'sepharose'
            html = (player / 'index.html').read_text(encoding='utf-8')
            self.assertIn('<video controls playsinline', html)
            self.assertIn('poster="sepharose-chainlit-poster.jpg"', html)
            self.assertIn('src="sepharose-chainlit-continuous.mp4"', html)
            self.assertIn('staged candidate', html)
            for name in builder.SEPHAROSE_EXPORTS:
                original = ROOT / 'media/chainlit-sepharose-continuous/exports' / name
                self.assertEqual((player / name).read_bytes(), original.read_bytes())

    def test_graph_chat_player_and_readme_use_the_1080p_recording(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            builder.prepare(output)
            player = output / 'graph-chat'
            html = (player / 'index.html').read_text(encoding='utf-8')
            self.assertIn('<video controls playsinline', html)
            self.assertIn('poster="poster.png"', html)
            self.assertIn('src="demo.mp4"', html)
            for name in ('demo.mp4', 'poster.png'):
                self.assertEqual((player / name).read_bytes(),
                                 (ROOT / 'media/chainlit-graph-1080p' / name).read_bytes())
            readme = (ROOT / 'README.md').read_text(encoding='utf-8')
            showcase = readme.split('## Watch the demo', 1)[1].split('## Run locally', 1)[0]
            self.assertIn('media/chainlit-graph-1080p/poster.png', showcase)
            self.assertIn('/bioprocess-assistant/graph-chat/', showcase)
            self.assertNotIn('flowshot/', showcase)
            self.assertNotIn('sepharose/', showcase)
            self.assertNotIn('onboarding.jpg', showcase)

    def test_changed_capture_rejected_before_output_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            shutil.copytree(ROOT / 'media/cytiva-flowshot-pilot-v02', fixture / 'media/cytiva-flowshot-pilot-v02')
            video = fixture / 'media/cytiva-onboarding-v05'
            for name in ('decisions/human-decision-005.json', 'exports/onboarding.mp4', 'exports/onboarding.jpg'):
                destination = video / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'media/cytiva-onboarding-v05' / name, destination)
            output = fixture / 'output'
            image = fixture / 'media/cytiva-flowshot-pilot-v02/shots/03-citation.jpg'
            image.write_bytes(image.read_bytes() + b'changed')
            with patch.object(builder, 'ROOT', fixture):
                with self.assertRaisesRegex(ValueError, 'Flowshot asset hash mismatch'):
                    builder.prepare(output)
            self.assertFalse(output.exists())

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            marker = output / 'existing.txt'
            marker.write_text('preserve', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'existing files are preserved'):
                builder.prepare(output)
            self.assertEqual(marker.read_text(encoding='utf-8'), 'preserve')


if __name__ == '__main__':
    unittest.main()
