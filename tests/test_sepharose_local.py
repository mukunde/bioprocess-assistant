"""Authority transitions use disposable data and never open the real candidate."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from serving.sepharose_candidate import Candidate, prepare
from serving.sepharose_local import Authority, LocalSepharose, VALIDATOR


class SepharoseAuthorityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.root = self.base / "candidate"
        prepare(self.root, "disposable-sepharose")
        self.database = self.base / "sepharose-authority.sqlite3"
        self.authority = Authority(self.database, self.root)
        self.release, _, self.snapshot = Candidate(self.root, preview=True)._snapshot()
        self.request = dict(product="protein_g", deposit_context="hydrophobic_deposits", guidance=True, pressure=True)

    def local(self):
        return LocalSepharose(Authority(self.database, self.root))

    def record(self, operation, **overrides):
        args = dict(expected_snapshot=self.snapshot, validator=VALIDATOR,
                    original_human_message="Synthetic decision for disposable test only")
        if operation != "disable":
            args.update(source_ids=[], review_ids=[])
        self.authority.record(operation, **(args | overrides))

    def source(self, source_id, generation):
        return self.local().source(self.release["release_id"], source_id, generation)

    def test_fail_closed_until_an_exact_approval_and_valid_inventory(self):
        self.assertEqual(self.local().evaluate(self.request)["status"], "unavailable")
        self.authority.initialize()
        for invalid in ({"validator": "other"}, {"expected_snapshot": "wrong"},
                        {"source_ids": ["unknown"]}, {"review_ids": None}, {"original_human_message": " "}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.record("enable", **invalid)
        self.assertEqual(self.local().evaluate(self.request)["citations"], [])
        self.record("enable")
        answer = self.local().evaluate(self.request)
        self.assertEqual({b["scope"] for b in answer["bundles"]}, {"Q01", "Q03", "Q04"})
        self.assertIn({"question": "pressure", "state": "abstained"}, answer["items"])
        self.assertEqual(self.source("E166-W", answer["generation"])["status"], "available")
        self.assertEqual(Candidate(self.root).evaluate(self.request)["status"], "unavailable")
        self.assertFalse((self.root / "active.json").exists())

    def test_withdrawals_and_disable_survive_restart(self):
        before = {file.name: file.read_bytes() for file in self.root.iterdir()}
        self.authority.initialize()
        self.record("enable")
        old = self.local().evaluate(self.request)["generation"]
        self.record("withdrawals", source_ids=["E166-W"])
        after = self.local().evaluate(self.request)
        self.assertEqual({b["scope"] for b in after["bundles"]}, {"Q01", "Q03"})
        self.assertEqual(self.source("E166-W", after["generation"])["status"], "unavailable")
        self.assertEqual(self.source("E166-D", old)["status"], "unavailable")
        self.assertEqual(self.source("E166-D", after["generation"])["status"], "available")
        self.record("withdrawals", source_ids=["E166-W"], review_ids=["Q01"])
        self.assertEqual(self.local().evaluate(self.request)["bundles"], [])
        unknown = self.local().evaluate(self.request | {"deposit_context": "unknown"})
        self.assertEqual([b["scope"] for b in unknown["bundles"]], ["Q09"])
        self.record("disable")
        self.assertEqual(self.local().evaluate(self.request)["status"], "unavailable")
        self.assertEqual(self.source("E166-D", after["generation"])["status"], "unavailable")
        with self.assertRaises(ValueError):
            self.record("enable")
        self.record("enable", source_ids=["E166-W"], review_ids=["Q01"])
        self.assertFalse(self.local().current(unknown["generation"]))
        self.assertEqual({file.name: file.read_bytes() for file in self.root.iterdir()}, before)

    def test_changed_authority_discards_an_in_flight_answer(self):
        self.authority.initialize()
        self.record("enable")
        from serving import sepharose_candidate as candidate
        original = candidate.journey.evaluate

        def withdraw_during_lookup(*args, **kwargs):
            self.record("withdrawals", source_ids=["E166-W"])
            return original(*args, **kwargs)

        with patch.object(candidate.journey, "evaluate", side_effect=withdraw_during_lookup):
            self.assertEqual(self.local().evaluate(self.request)["status"], "unavailable")

    def test_missing_history_and_damaged_candidate_fail_closed(self):
        self.authority.initialize()
        self.record("enable")
        release_file = self.root / "release.json"
        previous = release_file.read_bytes()
        release_file.write_text("invalid", encoding="utf-8")
        self.assertEqual(self.local().evaluate(self.request)["status"], "unavailable")
        self.record("disable")
        release_file.write_bytes(previous)
        self.assertEqual(self.local().evaluate(self.request)["status"], "unavailable")
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("DELETE FROM decisions WHERE seq=2")
        self.assertEqual(self.local().evaluate(self.request)["status"], "unavailable")

    def test_private_registry_path_is_rejected(self):
        with patch.dict("os.environ", {"MABSELECT_REGISTRY_ROOT": str(self.base / "private")}):
            with self.assertRaises(ValueError):
                Authority(self.base / "private" / self.database.name, self.root)

class SepharoseLocalChainlitTests(unittest.IsolatedAsyncioTestCase):
    async def test_old_source_button_is_refused_after_durable_withdrawal(self):
        from copy import deepcopy
        from importlib.util import module_from_spec, spec_from_file_location
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        from chainlit.config import config
        from chainlit.context import init_http_context

        init_http_context()
        path = Path(__file__).resolve().parents[1] / "demo" / "chainlit_sepharose_local.py"
        spec = spec_from_file_location("test_local_sepharose_entry", path)
        ui = module_from_spec(spec)
        with patch.object(config, "code", deepcopy(config.code)):
            spec.loader.exec_module(ui)

        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            candidate = base / "candidate"
            prepare(candidate, "ui-disposable")
            database = base / "sepharose-authority.sqlite3"
            authority = Authority(database, candidate)
            _, _, fingerprint = Candidate(candidate, preview=True)._snapshot()
            decision = dict(expected_snapshot=fingerprint, validator=VALIDATOR,
                            original_human_message="Synthetic UI test decision")
            authority.initialize()
            authority.record("enable", **decision, source_ids=[], review_ids=[])
            state, messages = {}, []

            def message(**kwargs):
                messages.append(kwargs)
                return SimpleNamespace(send=AsyncMock())

            with (patch.object(config.run, "host", "127.0.0.1"),
                  patch.dict("os.environ", {"SEPHAROSE_LOCAL_AUTHORITY": str(database),
                                            "SEPHAROSE_CANDIDATE_ROOT": str(candidate)}),
                  patch.object(ui.cl, "Message", side_effect=message),
                  patch.object(ui.cl, "ChatSettings", return_value=SimpleNamespace(send=AsyncMock())),
                  patch.object(ui.cl, "user_session", SimpleNamespace(get=state.get, set=state.__setitem__))):
                await ui.start()
                await ui.settings_update(dict(ui.DEFAULTS, product="Protein G Sepharose",
                                              context="Hydrophobic proteins, lipoproteins or lipids"))
                await ui.submit(messages[-1]["actions"][-1])
                action = next(x for x in messages[-1]["actions"] if x.label.startswith("E166-W"))
                await ui.source(action)
                self.assertIn("E166-W · PDF page 166", messages[-1]["content"])
                authority.record("withdrawals", **decision, source_ids=["E166-W"], review_ids=[])
                await ui.source(action)
                self.assertEqual(messages[-1]["content"], ui.UNAVAILABLE)
                await ui.submit(next(x for x in messages[-3]["actions"] if x.name == "sepharose_local_submit"))
                self.assertFalse(any(x.label.startswith("E166-W") for x in messages[-1]["actions"]))
                self.assertTrue(any(x.label.startswith("E166-D") for x in messages[-1]["actions"]))
                old_detergent = next(x for x in messages[-1]["actions"] if x.label.startswith("E166-D"))
                authority.record("disable", **decision)
                await ui.source(old_detergent)
                self.assertEqual(messages[-1]["content"], ui.UNAVAILABLE)
