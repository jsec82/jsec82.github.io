"""Release regression tests for the dashboard design and actual public case count."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
class DashboardTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.projects=json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
  cls.home=(DIST/'index.html').read_text(encoding='utf-8')
  cls.work=(DIST/'projects/index.html').read_text(encoding='utf-8')
  cls.focus=(DIST/'focus/index.html').read_text(encoding='utf-8')
  cls.roadmap=(DIST/'roadmap/index.html').read_text(encoding='utf-8')
 def test_all_public_cases_in_catalogue(self):
  for p in self.projects:
   self.assertIn('href="../projects/'+p['slug']+'.html"',self.work)
   self.assertTrue((DIST/'projects'/(p['slug']+'.html')).is_file())
   expected='planned' if p['status']=='roadmap' else p['status']
   self.assertIn('data-status="'+expected+'"',self.work)
 def test_dynamic_project_count(self):
  self.assertEqual(self.work.count('data-project=""'),len(self.projects))
 def test_focus_navigation(self):
  for id in ('intune','entra','defender','sentinel'):
   self.assertIn('focus/index.html?area='+id,self.home)
   self.assertIn('data-focus-filter="'+id+'"',self.focus)
 def test_roadmap_evidence_states(self):
  for credential in ('MD-102','SC-300','AZ-900','SC-900'):self.assertIn(credential,self.roadmap)
  self.assertNotIn('100% complete',self.roadmap)
 def test_three_categories(self):
  self.assertEqual(self.home.count('class="group-card"'),3)
 def test_photo_only_in_small_header(self):
  self.assertEqual(self.home.count('src="assets/jeroen-portrait.webp"'),1)
  contact=(DIST/'contact/index.html').read_text(encoding='utf-8')
  self.assertEqual(contact.count('jeroen-portrait.webp'),1)
 def test_security_metadata_and_legacy_routes(self):
  for page in DIST.rglob('*.html'):
   text=page.read_text(encoding='utf-8')
   self.assertNotIn('noindex,nofollow',text)
   self.assertIn('Content-Security-Policy',text)
   self.assertIn('https://weijdensecurity.nl/',text)
  for p in ('about/index.html','skills/index.html','activity/index.html'):self.assertTrue((DIST/p).is_file())
 def test_high_res_project_images(self):
  for p in self.projects:self.assertTrue((DIST/'assets'/p['image']).is_file())
if __name__=='__main__':unittest.main()
