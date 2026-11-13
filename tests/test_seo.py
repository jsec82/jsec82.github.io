"""SEO and AI search discovery regression: truthful metadata, microdata, and safe crawling."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SEARCH_PAGES=('index.html','projects/index.html','focus/index.html','roadmap/index.html',
    'contact/index.html','projects/engineering/endpoint.html',
    'projects/engineering/identity.html','projects/engineering/capstone.html')

class SEOTests(unittest.TestCase):
    def test_unique_localized_descriptions_and_open_graph(self):
        for locale in ('','en/'):
            descriptions=[]
            for rel in SEARCH_PAGES:
                page=(DIST/locale/rel).read_text(encoding='utf-8')
                match=re.search(r'<meta content="([^"]+)" name="description"/>',page)
                self.assertIsNotNone(match,locale+rel)
                desc=match.group(1)
                self.assertGreaterEqual(len(desc),75,locale+rel)
                self.assertLessEqual(len(desc),195,locale+rel)
                self.assertEqual(page.count('content="'+desc+'"'),2,locale+rel)
                self.assertIn('rel="canonical"',page)
                self.assertIn('hreflang="nl"',page)
                self.assertIn('hreflang="en"',page)
                descriptions.append(desc)
            self.assertEqual(len(descriptions),len(set(descriptions)),locale)
    def test_csp_safe_site_identity_schema(self):
        homepage=(DIST/'index.html').read_text(encoding='utf-8')
        self.assertIn('itemtype="https://schema.org/WebSite"',homepage)
        self.assertIn('itemprop="name" content="Weijden Security"',homepage)
        self.assertIn('itemprop="url" href="https://weijdensecurity.nl/"',homepage)
        self.assertNotIn('<script type="application/ld+json"',homepage)
    def test_public_profile_schema_no_private_identifiers(self):
        for locale in ('','en/'):
            doc=(DIST/locale/'contact/index.html').read_text(encoding='utf-8')
            self.assertIn('itemtype="https://schema.org/ProfilePage"',doc)
            self.assertIn('itemprop="mainEntity"',doc)
            self.assertIn('itemtype="https://schema.org/Person"',doc)
            self.assertIn('itemprop="name" content="Jeroen"',doc)
            self.assertIn('itemprop="jobTitle" content="Security Engineer"',doc)
            self.assertNotIn('security-engineer-portfolio',doc)
    def test_sitemap_and_searchbot_rule(self):
        robots=(DIST/'robots.txt').read_text(encoding='utf-8')
        self.assertIn('User-agent: OAI-SearchBot\nAllow: /',robots)
        self.assertIn('User-agent: *\nAllow: /',robots)
        self.assertIn('Sitemap: https://weijdensecurity.nl/sitemap.xml',robots)
        root=ET.parse(DIST/'sitemap.xml').getroot()
        self.assertEqual(len(root),29)
if __name__=='__main__':unittest.main()
