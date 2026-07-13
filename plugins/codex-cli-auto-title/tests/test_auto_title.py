"""Behavior tests for the auto-title Stop hook."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "auto_title.py"


def _load_module():
    if not SCRIPT.exists():
        raise AssertionError(f"missing implementation: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("auto_title", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load implementation: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FirstPromptTests(unittest.TestCase):
    """Protect the one-prompt thread eligibility rule."""

    def test_returns_text_from_one_user_message_in_unnamed_thread(self):
        module = _load_module()
        thread = {
            "name": None,
            "turns": [
                {
                    "items": [
                        {
                            "type": "userMessage",
                            "content": [
                                {"type": "text", "text": "Name this thread"},
                                {"type": "image", "url": "data:image/png;base64,AA=="},
                                {"type": "text", "text": "from this prompt"},
                            ],
                        }
                    ]
                }
            ],
        }

        self.assertEqual(
            module._first_prompt(thread),
            "Name this thread\nfrom this prompt",
        )

    def test_skips_named_thread(self):
        module = _load_module()
        thread = {
            "name": "Existing title",
            "turns": [
                {
                    "items": [
                        {
                            "type": "userMessage",
                            "content": [{"type": "text", "text": "Prompt"}],
                        }
                    ]
                }
            ],
        }

        self.assertIsNone(module._first_prompt(thread))

    def test_skips_zero_or_multiple_user_messages(self):
        module = _load_module()
        no_messages = {"name": None, "turns": [{"items": []}]}
        two_messages = {
            "name": None,
            "turns": [
                {
                    "items": [
                        {
                            "type": "userMessage",
                            "content": [{"type": "text", "text": "First"}],
                        },
                        {"type": "agentMessage", "text": "Response"},
                    ]
                },
                {
                    "items": [
                        {
                            "type": "userMessage",
                            "content": [{"type": "text", "text": "Second"}],
                        }
                    ]
                },
            ],
        }

        self.assertIsNone(module._first_prompt(no_messages))
        self.assertIsNone(module._first_prompt(two_messages))

    def test_skips_empty_or_image_only_prompt(self):
        module = _load_module()
        for content in (
            [{"type": "text", "text": " \n "}],
            [{"type": "image", "url": "data:image/png;base64,AA=="}],
        ):
            with self.subTest(content=content):
                thread = {
                    "name": None,
                    "turns": [{"items": [{"type": "userMessage", "content": content}]}],
                }
                self.assertIsNone(module._first_prompt(thread))


class SanitizeTitleTests(unittest.TestCase):
    """Protect the bounded title format stored by the hook."""

    def test_normalizes_first_nonempty_line_and_removes_wrapping_punctuation(self):
        module = _load_module()

        self.assertEqual(
            module._sanitize_title('\n  "  Concise   thread title.  "\nignored'),
            "Concise thread title",
        )
        self.assertEqual(
            module._sanitize_title('"Concise thread title".'), "Concise thread title"
        )

    def test_caps_title_at_seven_words_and_eighty_characters(self):
        module = _load_module()
        many_words = "one two three four five six seven eight nine"
        long_word = "x" * 100

        self.assertEqual(
            module._sanitize_title(many_words),
            "one two three four five six seven",
        )
        self.assertEqual(module._sanitize_title(long_word), "x" * 80)


class MainTests(unittest.TestCase):
    """Protect the recursion guard at the process boundary."""

    def test_child_guard_exits_without_invoking_codex(self):
        if not SCRIPT.exists():
            self.fail(f"missing implementation: {SCRIPT}")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "codex-was-called"
            fake_codex = root / "codex"
            fake_codex.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 99\n")
            fake_codex.chmod(0o755)
            env = os.environ.copy()
            env["CODEX_AUTO_TITLE_CHILD"] = "1"
            env["PATH"] = f"{root}{os.pathsep}{env.get('PATH', '')}"

            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                input="not valid JSON",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"continue": True})
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
