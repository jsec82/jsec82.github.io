"""Regression checks for bilingual evidence methodology and dark/light theme UI."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
PAGES=[
    'index.html','focus/index.html','projects/index.html','roadmap/index.html',
    'contact/index.html','methodology/index.html',
    'projects/engineering/index.html','projects/engineering/endpoint.html',
    'projects/engineering/identity.html','projects/engineering/capstone.html',
    'projects/ohsint-investigation.html','projects/fakebank-attack-defend.html',
    'projects/md102-autopilot-esp.html','projects/identity-detection-roadmap.html'
]
class WebsiteReleaseTests(unittest.TestCase):
    def test_theme_switch_and_methodology_links_on_current_routes(self):
        for prefix in ('','en/'):
            for path in PAGES:
                with self.subTest(page=prefix+path):
                    page=(DIST/prefix/path).read_text(encoding='utf-8')
                    self.assertIn('data-theme="dark"',page)
                    self.assertIn('data-theme-select="dark"',page)
                    self.assertIn('data-theme-select="light"',page)
                    self.assertIn('aria-pressed="false"',page)
                    self.assertIn('methodology/index.html',page)
                    self.assertIn('data-language-switch="nl"',page)
                    self.assertIn('data-language-switch="en"',page)
                    self.assertIn('Content-Security-Policy',page)
    def test_home_no_counters_and_original_core_sections(self):
        for prefix in ('','en/'):
            homepage=(DIST/prefix/'index.html').read_text(encoding='utf-8')
            self.assertNotIn('class="stats"',homepage)
            self.assertNotIn('class="two-col"',homepage)
            self.assertNotIn('class="group-count"',homepage)
            self.assertNotIn('Laatste gedocumenteerde voortgang',homepage)
            self.assertNotIn('Latest documented progress',homepage)
            self.assertEqual(homepage.count('class="group-card"'),3)
            self.assertEqual(homepage.count('class="focus-card'),4)
            self.assertIn('Security+ V8',homepage)
            self.assertIn('AZ-900',homepage)
            self.assertIn('SC-300',homepage)
            self.assertIn('method-inline-link',homepage)
    def test_methodology_scope_and_correct_evidence_limitations(self):
        for prefix in ('','en/'):
            doc=(DIST/prefix/'methodology/index.html').read_text(encoding='utf-8')
            for name in ('NIST NICE','NIST CSF 2.0','Microsoft Zero Trust','MITRE ATT&amp;CK','HSE-01'):
                self.assertIn(name,doc)
            self.assertEqual(doc.count('class="method-step"'),5)
            self.assertEqual(doc.count('class="method-framework"'),4)
            self.assertEqual(doc.count('class="method-status"'),4)
            self.assertEqual(doc.count('class="method-card"'),4)
            self.assertEqual(doc.count('target="_blank" rel="noopener noreferrer"'),5)
            self.assertIn('https://weijdensecurity.nl/'+prefix+'methodology/',doc)
    def test_local_theme_script_without_network_or_eval(self):
        js=(DIST/'assets/dashboard.js').read_text(encoding='utf-8')
        css=(DIST/'assets/dashboard.css').read_text(encoding='utf-8')
        self.assertIn('weijden-security-theme',js)
        self.assertIn('localStorage',js)
        self.assertIn('data-theme="light"',css)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('eval(',js)
if __name__=='__main__':unittest.main()
