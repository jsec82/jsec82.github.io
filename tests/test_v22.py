"""Regressions for the release checks; no network or external dependencies."""
import tempfile
import unittest
from pathlib import Path
from scripts.security_audit import CSP, audit_markup, scan_asset
from scripts.check_release import check


class SecurityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = (Path(__file__).resolve().parents[1]/'dist/index.html').read_text(encoding='utf-8')

    def check_injection(self, before, after, expected):
        self.assertIn(before, self.original)
        candidate = self.original.replace(before, after, 1)
        errors = audit_markup(candidate, Path('index.html'))
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_clean_homepage(self):
        self.assertEqual([], audit_markup(self.original, Path('index.html')))

    def test_external_script_rejected(self):
        self.check_injection('src="assets/dashboard.js"', 'src="https://cdn.example.com/evil.js"', 'unapproved')

    def test_inline_event_handler_rejected(self):
        self.check_injection('<body data-page="home">', '<body data-page="home" onload="alert(1)">', 'inline event')

    def test_csp_removal_rejected(self):
        self.check_injection('http-equiv="Content-Security-Policy"', 'name="not-csp"', 'Content Security Policy')

    def test_obsolete_domain_rejected(self):
        self.check_injection('https://weijdensecurity.nl/', 'https://jsec82.github.io/', 'obsolete')

    def test_blank_target_safety(self):
        candidate = self.original.replace('</main>', '<a target="_blank" rel="nofollow" href="https://www.linkedin.com/in/jeroenvanderweijden/">LinkedIn</a></main>')
        errors = audit_markup(candidate, Path('index.html'))
        self.assertTrue(any('noopener/noreferrer' in e for e in errors), errors)

    def test_exif_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/'example.webp'
            file.write_bytes(b'RIFFdummyWEBPEXIFdata')
            self.assertTrue(any('metadata' in e for e in scan_asset(file)))


class ReleaseIntegrityTests(unittest.TestCase):
    def test_missing_and_modified_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'dist').mkdir()
            (root/'dist/index.html').write_text('trusted',encoding='utf-8')
            self.assertTrue(any('missing' in e for e in check(root)))
            (root/'index.html').write_text('tampered',encoding='utf-8')
            self.assertTrue(any('differs' in e for e in check(root)))
            (root/'index.html').write_text('trusted',encoding='utf-8')
            self.assertEqual([],check(root))


if __name__ == '__main__':
    unittest.main()
