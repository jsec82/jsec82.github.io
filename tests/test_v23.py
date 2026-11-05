#!/usr/bin/env python3
"""V2.3 regression tests; use approved public data and Python stdlib only."""
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
FOCUS = ('intune','entra','defender','sentinel')
COVERS = ('osint-map-hd.svg','windows-art-hd.svg','detection-art-hd.svg')

class V23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = (DIST/'index.html').read_text(encoding='utf-8')
        cls.about = (DIST/'about/index.html').read_text(encoding='utf-8')
        cls.focus = (DIST/'focus/index.html').read_text(encoding='utf-8')
        cls.projects = json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
        cls.mapping = json.loads((ROOT/'content/focus-map.json').read_text(encoding='utf-8'))

    def test_existing_featured_projects_and_statuses(self):
        region = self.home.split('<section class="projects-section"',1)[1].split('</section>',1)[0]
        cards = re.findall(r'<article class="project-card\b[\s\S]*?</article>', region)
        self.assertEqual(len(cards),3)
        for project in self.projects[:3]:
            matching = [c for c in cards if 'projects/'+project['slug']+'.html' in c]
            self.assertEqual(len(matching),1,project['slug'])
            self.assertIn('status-'+project['status'],matching[0])

    def test_fakebank_recruiter_routes_and_evidence_boundaries(self):
        slug = 'fakebank-attack-defend'
        matching = [p for p in self.projects if p['slug'] == slug]
        self.assertEqual(len(matching),1)
        self.assertEqual(matching[0]['status'],'completed')
        self.assertIn('href="projects/'+slug+'.html"',self.home)
        catalog = (DIST/'projects/index.html').read_text(encoding='utf-8')
        detail = (DIST/'projects'/f'{slug}.html').read_text(encoding='utf-8')
        focus = (DIST/'focus/index.html').read_text(encoding='utf-8')
        activity = (DIST/'activity/index.html').read_text(encoding='utf-8')
        self.assertIn('href="'+slug+'.html"',catalog)
        self.assertIn('Proposed',detail)
        self.assertIn(slug+'.html',focus)
        self.assertIn(slug+'.html',activity)
        self.assertNotIn('BANK-HACKED',detail)
        self.assertNotIn('/bank-transfer',detail)

    def test_focus_links_exist_and_are_accessible(self):
        for area in FOCUS:
            self.assertEqual(self.home.count('href="focus/index.html?area='+area+'"'),1)
            self.assertIn('data-focus-filter="'+area+'"',self.focus)
            self.assertIn('aria-label="View related projects, CTFs and cases',self.home)

    def test_mapping_exactly_covers_approved_public_work(self):
        self.assertEqual(set(self.mapping),{p['slug'] for p in self.projects})
        for key,detail in self.mapping.items():
            self.assertIsInstance(detail['type'],str)
            self.assertTrue(set(detail['focus_areas']).issubset(FOCUS),key)

    def test_real_photo_is_present_both_places(self):
        self.assertIn('class="about-art about-art--portrait"',self.home)
        self.assertIn('src="assets/jeroen-portrait.webp"',self.home)
        self.assertIn('src="../assets/jeroen-portrait.webp"',self.about)
        asset = (DIST/'assets/jeroen-portrait.webp')
        self.assertTrue(asset.is_file())
        self.assertGreater(asset.stat().st_size,3000)
        self.assertNotIn(b'EXIF',asset.read_bytes())
        self.assertNotIn(b'XMP ',asset.read_bytes())

    def test_crisp_native_art_resolutions_and_safety(self):
        for filename in COVERS:
            img = DIST/'assets'/filename
            element = ET.parse(img).getroot()
            self.assertEqual(element.attrib['width'],'1600')
            self.assertEqual(element.attrib['height'],'900')
            text = img.read_text(encoding='utf-8').lower()
            for dangerous in ('<script','foreignobject','onload=','javascript:'):
                self.assertNotIn(dangerous,text)

    def test_published_page_count_and_correct_domain(self):
        self.assertEqual(len(list(DIST.rglob('*.html'))),6+len(self.projects))
        self.assertIn('https://weijdensecurity.nl/focus/',self.focus)
        self.assertIn('<meta http-equiv="Content-Security-Policy"',self.focus)

    def test_release_integrity_includes_focus(self):
        from scripts import check_release
        self.assertIn('focus',check_release.GENERATED_DIRS)

if __name__ == '__main__':
    unittest.main()
