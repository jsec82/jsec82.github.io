"""Bilingual security engineering preview regression checks."""
from pathlib import Path
from html.parser import HTMLParser
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

 def test_localized_switch_targets_actual_counterpart(self):
  class SwitchParser(HTMLParser):
   def __init__(self):
    super().__init__(); self.switches={}
   def handle_starttag(self,tag,attrs):
    if tag=='a':
     item=dict(attrs)
     if item.get('data-language-switch') in ('nl','en'):
      self.switches[item['data-language-switch']]=item.get('href')
  for slug in ('index.html','endpoint.html','identity.html','capstone.html'):
   for prefix in ('','en/'):
    file=DIST/prefix/'projects/engineering'/slug
    parser=SwitchParser()
    parser.feed(file.read_text(encoding='utf-8'))
    self.assertEqual(set(parser.switches), {'nl','en'})
    for language,href in parser.switches.items():
     target=(file.parent/href).resolve()
     expected=(DIST/('en/' if language=='en' else '')/'projects/engineering'/slug).resolve()
     self.assertEqual(target,expected)
     self.assertTrue(target.is_file())

if __name__=='__main__': unittest.main()
