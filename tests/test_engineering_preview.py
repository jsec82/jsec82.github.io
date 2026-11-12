"""Bilingual security engineering preview regression checks."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
class EngineeringPreview(unittest.TestCase):
 def test_pages_and_status(self):
  for prefix in ('','en/'):
   for slug in ('index.html','endpoint.html','identity.html','capstone.html'):
    html=(DIST/prefix/'projects/engineering'/slug).read_text(encoding='utf-8')
    self.assertEqual(html.count('<h1'),1)
    self.assertIn('class="pill planned"',html)
    self.assertIn('Content-Security-Policy',html)
    self.assertIn('hreflang="nl"',html)
    self.assertIn('hreflang="en"',html)
    self.assertNotIn('security-engineer-portfolio',html)
 def test_exactly_three_flagships_and_old_categories(self):
  for prefix in ('','en/'):
   home=(DIST/prefix/'index.html').read_text(encoding='utf-8')
   hub=(DIST/prefix/'projects/engineering/index.html').read_text(encoding='utf-8')
   self.assertEqual(home.count('class="group-card"'),3)
   self.assertEqual(hub.count('class="eng-card eng-'),3)
   self.assertIn('projects/engineering/index.html',home)
 def test_explicit_evidence_limits(self):
  for prefix in ('','en/'):
   for slug in ('endpoint','identity','capstone'):
    html=(DIST/prefix/'projects/engineering'/f'{slug}.html').read_text(encoding='utf-8')
    self.assertIn('eng-detail-status',html)
    self.assertIn('eng-checks',html)
if __name__=='__main__': unittest.main()
