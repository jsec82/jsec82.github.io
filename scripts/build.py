#!/usr/bin/env python3
"""Generate public-safe, responsive pages from curated content, not private GitHub files."""
import datetime
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
def esc(value): return html.escape(str(value), quote=True)
site = json.loads((ROOT/'content/site.json').read_text(encoding='utf-8'))
projects = sorted(json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8')), key=lambda x:x['priority'])
updates = sorted(json.loads((ROOT/'content/lab-log.json').read_text(encoding='utf-8')), key=lambda x:x['date'], reverse=True)
STATUS = {'completed':'Completed', 'in-progress':'In progress', 'roadmap':'Planned'}
ARROW = '<svg class="arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>'
GITHUB = '<svg viewBox="0 0 24 24" aria-hidden="true" class="github-svg"><path d="M12 .7a11.3 11.3 0 0 0-3.56 22.04c.56.11.77-.24.77-.55v-2.12c-3.14.68-3.8-1.33-3.8-1.33-.51-1.29-1.25-1.64-1.25-1.64-1.02-.69.08-.68.08-.68 1.14.08 1.74 1.17 1.74 1.17 1 1.73 2.65 1.23 3.29.94.1-.73.4-1.25.72-1.53-2.5-.29-5.14-1.25-5.14-5.63 0-1.25.44-2.27 1.17-3.06-.12-.29-.51-1.45.12-3.01 0 0 .96-.31 3.14 1.17a10.86 10.86 0 0 1 5.71 0c2.18-1.48 3.14-1.17 3.14-1.17.63 1.56.24 2.72.12 3.01.73.79 1.16 1.81 1.16 3.06 0 4.39-2.63 5.34-5.15 5.63.41.36.76 1.04.76 2.09v2.84c0 .31.2.67.78.54A11.3 11.3 0 0 0 12 .7z"/></svg>'
ICONS = {
 'intune':'<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="4" y="5" width="24" height="16" rx="1"/><path d="M16 21v6m-7 0h14"/></svg>',
 'entra':'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="m16 2 14 24-14-4L2 26z" fill="currentColor" stroke="none"/><path d="m16 2-1 20L2 26z" fill="#269bea" stroke="none"/></svg>',
 'defender':'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2 29 7v9c0 9-7 12-13 14C9 28 3 25 3 16V7z" fill="currentColor" stroke="none"/><path d="M16 7v17M9 16h14" stroke="#072039" stroke-width="2"/></svg>',
 'sentinel':'<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="17" width="6" height="12" rx="1"/><rect x="13" y="11" width="6" height="18" rx="1"/><rect x="23" y="4" width="6" height="25" rx="1"/></svg>',
}

def date_label(d): return datetime.date.fromisoformat(d).strftime('%d %b %Y')
def pill(status): return f'<span class="status status-{esc(status)}"><i aria-hidden="true"></i>{STATUS[status]}</span>'
def header(nested=False):
    up='../' if nested else ''
    nav=''.join(f'<a href="{up}index.html#{a}">{b}</a>' for a,b in [('projects','Projects'),('skills','Skills'),('about','About'),('activity','Lab log')])
    return f'''<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="shell topbar"><a class="brand" href="{up}index.html" aria-label="Jeroen, homepage"><span class="logo-mark">J<span>⌁</span></span><span>Jeroen<small>Security Engineer</small></span></a><nav id="nav" class="nav" aria-label="Main navigation"><a href="{up}index.html" class="nav-overview">Overview</a>{nav}<a class="mobile-contact" target="_blank" rel="noopener noreferrer" href="{esc(site['linkedin_url'])}">Get in touch {ARROW}</a></nav><div class="topbar-actions"><a href="{esc(site['github_profile'])}" class="github-link" rel="noopener noreferrer" target="_blank">{GITHUB} GitHub</a><span class="top-divider"></span><a href="{esc(site['linkedin_url'])}" target="_blank" rel="noopener noreferrer" class="button primary small">Get in touch {ARROW}</a></div><button class="menu-button" type="button" aria-controls="nav" aria-expanded="false" aria-label="Open menu"><span></span><span></span><span></span></button></div></header>'''
def footer(nested=False):
    up='../' if nested else ''
    return f'''<footer class="footer shell"><div><strong>Jeroen <span class="accent">/</span> Security Engineering</strong><p>Practical labs. Verified results. Transparent limitations.</p></div><div class="footer-actions"><a href="{up}index.html#projects">Explore projects</a><a href="{esc(site['linkedin_url'])}" target="_blank" rel="noopener noreferrer">LinkedIn</a><a href="{esc(site['github_profile'])}" target="_blank" rel="noopener noreferrer">GitHub</a></div><p class="fineprint">Curated, sanitized case summaries. Original test-tenant details and private lab records are not publicly accessible.</p></footer>'''
def page(title, markup, nested=False, slug=None):
    up='../' if nested else ''
    public_path=f'projects/{slug}.html' if nested and slug else ''
    canonical='https://jsec82.github.io/'+public_path
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#071321"><meta name="description" content="Jeroen's security engineering portfolio: Windows Autopilot, Microsoft Intune, blue-team investigations and documented practical labs."><link rel="canonical" href="{esc(canonical)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="https://jsec82.github.io/assets/hero-globe.webp"><meta name="twitter:card" content="summary_large_image"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | Jeroen — Security Engineering"><meta property="og:description" content="Hands-on Microsoft Security and Blue Team labs. What I did, what I verified, and what remains open."><title>{esc(title)} | Jeroen — Security Engineering</title><link rel="icon" type="image/svg+xml" href="{up}assets/favicon.svg"><link rel="stylesheet" href="{up}assets/style.css"></head><body>{header(nested)}{markup}{footer(nested)}<script defer src="{up}assets/site.js"></script></body></html>'''

def focus_card(key,title,desc):
    return f'''<article class="focus-card focus-{key}"><div class="focus-head"><span class="focus-icon">{ICONS[key]}</span><span class="focus-arrow" aria-hidden="true">↗</span></div><h3>{title}</h3><p>{desc}</p></article>'''

def case_card(pr):
    cls={'ohsint-investigation':'osint','md102-autopilot-esp':'windows','identity-detection-roadmap':'detection'}[pr['slug']]
    label={'ohsint-investigation':'CTF / OSINT','md102-autopilot-esp':'ENDPOINT / INTUNE','identity-detection-roadmap':'FUTURE / DETECTION'}[pr['slug']]
    when=f'<time datetime="{esc(pr["date"])}">{date_label(pr["date"])}</time>' if pr['date'] else 'Future project'
    return f'''<article class="project-card project-{cls}"><div class="project-visual visual-{cls}"><span class="project-visual-label">{label}</span>{pill(pr['status'])}</div><div class="project-body"><div class="project-kicker">{esc(pr['discipline'])} <span>·</span> {when}</div><h3><a href="projects/{esc(pr['slug'])}.html">{esc(pr['title'])}</a></h3><p class="project-desc">{esc(pr['description'])}</p><dl class="proof-list"><div><dt>What I did</dt><dd>{esc(pr['card_approach'])}</dd></div><div><dt>Validation</dt><dd>{esc(pr['card_validation'])}</dd></div><div><dt>Outcome</dt><dd>{esc(pr['card_outcome'])}</dd></div></dl><a class="card-link" href="projects/{esc(pr['slug'])}.html">{'Explore planned scope' if pr['status']=='roadmap' else 'Read case study'} {ARROW}</a></div></article>'''

def activity_panel():
    li=''.join(f'<li><span class="time-dot" aria-hidden="true"></span><time datetime="{esc(item["date"])}">{date_label(item["date"])}</time><a href="projects/{esc(item["project_slug"])}.html">{esc(item["label"])}</a><p>{esc(item["detail"])}</p></li>' for item in updates[:5])
    return f'''<aside class="activity-panel panel" id="activity" aria-labelledby="activity-heading"><div class="panel-top"><div class="panel-title"><span class="mini-icon" aria-hidden="true">▤</span><h2 id="activity-heading">Recent lab log</h2></div><span class="review-badge">Reviewed</span></div><ol class="timeline">{li}</ol><p class="panel-foot">Documented updates, not a live feed. <a href="#projects">See projects {ARROW}</a></p></aside>'''

def home():
    cards=''.join(case_card(p) for p in projects)
    return f'''<main id="main"><div class="hero-background"><div class="shell hero-grid"><section class="hero-copy" aria-labelledby="hero-title"><p class="eyebrow hero-overline"><span class="short-line"></span>BUILD <b>·</b> DETECT <b>·</b> INVESTIGATE <b>·</b> IMPROVE</p><h1 id="hero-title">Security<br>Engineering<br><em>Portfolio</em></h1><p class="hero-subtitle">Microsoft Security <span>·</span> Blue Team <span>·</span> Practical Labs</p><p class="hero-description">{esc(site['intro'])}</p><div class="hero-buttons"><a href="#projects" class="button primary">Explore my projects {ARROW}</a><a href="{esc(site['linkedin_url'])}" target="_blank" rel="noopener noreferrer" class="button ghost">Get in touch {ARROW}</a></div><p class="hero-footnote"><span class="tiny-check">✓</span> Evidence-led case studies · No inflated claims</p></section><div class="hero-art"><img src="assets/hero-globe.webp" width="692" height="403" alt="" decoding="async" fetchpriority="high"><span class="art-glow" aria-hidden="true"></span></div>{activity_panel()}</div></div>
    <div class="shell content-shell"><section class="focus-section" id="skills" aria-labelledby="focus-title"><div class="section-heading"><div class="section-heading-main"><span class="section-icon">◈</span><h2 id="focus-title">Core focus areas</h2><span class="heading-rule" aria-hidden="true"></span></div><p>MY TECHNICAL FOCUS · MICROSOFT SECURITY</p></div><div class="focus-grid">{focus_card('intune','Microsoft Intune','Endpoint management, enrollment and device configuration.')}{focus_card('entra','Microsoft Entra ID','Identity, device trust and access management.')}{focus_card('defender','Microsoft Defender','Endpoint protection and threat investigation as a learning focus.')}{focus_card('sentinel','Microsoft Sentinel','Planned detection engineering and KQL practice.')}</div></section>
    <section class="projects-section" id="projects" aria-labelledby="projects-title"><div class="section-heading"><div class="section-heading-main"><span class="section-icon">▱</span><h2 id="projects-title">Featured projects</h2><span class="heading-rule" aria-hidden="true"></span></div><p>THE WORK · THE EVIDENCE · THE LIMITS</p></div><p class="section-intro">A curated selection of work I have completed, work in progress, and future projects. Each case distinguishes hands-on results from planned controls.</p><div class="projects-grid">{cards}<aside class="about-card" id="about"><div class="about-heading"><span class="section-icon">♙</span><h2>About Jeroen</h2></div><div class="about-art" role="presentation"></div><p>I am building Microsoft-focused Security Engineering skills through hands-on labs, investigation and validation. My portfolio is intentionally evidence-first: I describe what worked, what was observed, and what still needs testing.</p><div class="about-divider"></div><h3>How to read my work</h3><div class="legend"><div>{pill('completed')}<span>Exercise completed; limits disclosed</span></div><div>{pill('in-progress')}<span>Work started; checks remain</span></div><div>{pill('roadmap')}<span>Future work, not demonstrated</span></div></div><a class="button ghost about-link" href="{esc(site['linkedin_url'])}" target="_blank" rel="noopener noreferrer">Connect on LinkedIn {ARROW}</a></aside></div></section>
    <section class="workflow-section" aria-labelledby="approach-title"><div><p class="eyebrow">HOW I APPROACH PRACTICAL LABS</p><h2 id="approach-title">From configuration to confirmed results.</h2><p>A professional case study should make it easy to distinguish configuration, observed behaviour and validated outcomes.</p></div><div class="workflow-steps"><span>01 <strong>Objective</strong></span><span>02 <strong>Implementation</strong></span><span>03 <strong>Validation</strong></span><span>04 <strong>Lessons learned</strong></span></div></section></div></main>'''

def detail_item(idx,heading,body):return f'<section class="detail-section"><span class="detail-numeral">{idx}</span><div><h2>{esc(heading)}</h2><p>{esc(body)}</p></div></section>'
def detail(pr):
    planned=pr['status']=='roadmap'
    steps=(detail_item('01','Proposed scope' if planned else 'Approach and tools',pr['approach'])+detail_item('02','Validation to be completed' if planned else 'Evidence and validation',pr['validation'])+detail_item('03','Result and limitations',pr['outcome'])+detail_item('04','Next criteria' if planned else 'Lessons learned',pr['learned']))
    tools=''.join(f'<span>{esc(t)}</span>' for t in pr['tools'])
    timestamp=(f'<time datetime="{esc(pr["date"])}">{date_label(pr["date"])}</time>' if pr['date'] else 'Not yet started')
    checks=''.join(f'<tr><th scope="row">{esc(row["item"])}</th><td>{esc(row["result"])}</td><td><span class="evidence-state">{esc(row["state"])}</span></td></tr>' for row in pr.get('evidence_checks',[]))
    command=(f'<div class="example-command"><p class="eyebrow">READ-ONLY COMMAND USED IN LAB</p><pre><code>{esc(pr["example_command"])}</code></pre></div>' if pr.get('example_command') else '')
    evidence_section=(f'<section class="evidence-snapshot"><h2>Evidence snapshot</h2><p>Summarized observations from the documented lab. No private logs or tenant identifiers are included.</p><div class="table-scroll"><table><thead><tr><th scope="col">Check</th><th scope="col">Recorded result</th><th scope="col">Evidence status</th></tr></thead><tbody>{checks}</tbody></table></div>{command}</section>' if checks else '')
    evidence=('This is a future learning track. No completed lab is claimed.' if planned else 'This case is a curated public summary; private source records are not directly accessible to visitors.')
    return f'''<main id="main" class="shell detail-page"><a class="back" href="../index.html#projects">← All projects</a><div class="detail-hero"><p class="eyebrow">{esc(pr['eyebrow'])}</p><div class="detail-hero-heading"><h1>{esc(pr['title'])}</h1>{pill(pr['status'])}</div><p class="detail-summary">{esc(pr['description'])}</p><p class="detail-disclaimer">{evidence}</p></div><div class="detail-layout"><div class="detail-main"><h2 class="detail-intro-heading">{'Planned case scope' if planned else 'Case study'}</h2>{evidence_section}{steps}</div><aside class="detail-sidebar"><div class="panel detail-panel"><h2>At a glance</h2><dl class="detail-facts"><div><dt>Status</dt><dd>{pill(pr['status'])}</dd></div><div><dt>Area</dt><dd>{esc(pr['discipline'])}</dd></div><div><dt>Last update</dt><dd>{timestamp}</dd></div></dl></div><div class="panel detail-panel"><h2>Tools & context</h2><div class="toolchips">{tools}</div></div><div class="panel detail-panel"><h2>Evidence boundary</h2><p>Only selected, anonymized project summaries are published here. Screenshots, private tenant identifiers and raw log exports are not shared.</p></div></aside></div><div class="detail-bottom"><a href="../index.html#projects" class="button ghost">Back to projects {ARROW}</a><a href="{esc(site['linkedin_url'])}" class="button primary" target="_blank" rel="noopener noreferrer">Discuss on LinkedIn {ARROW}</a></div></main>'''
def run():
    subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],check=True)
    if OUT.is_symlink(): raise SystemExit('dist must not be a symlink')
    if OUT.exists():shutil.rmtree(OUT)
    (OUT/'assets').mkdir(parents=True)
    (OUT/'projects').mkdir()
    for asset in ('style.css','site.js','favicon.svg','hero-globe.webp','osint-map.webp','windows-art.webp','detection-art.webp'):
        shutil.copyfile(ROOT/'assets'/asset,OUT/'assets'/asset)
    (OUT/'index.html').write_text(page('Portfolio',home()),encoding='utf-8')
    for pr in projects:
        (OUT/'projects'/f'{pr["slug"]}.html').write_text(page(pr['title'],detail(pr),nested=True,slug=pr['slug']),encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://jsec82.github.io/sitemap.xml\n',encoding='utf-8')
    from xml.sax.saxutils import escape as xml_escape
    urls=['https://jsec82.github.io/']+[f'https://jsec82.github.io/projects/{pr["slug"]}.html' for pr in projects]
    items=''.join(f'<url><loc>{xml_escape(u)}</loc></url>' for u in urls)
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+items+'</urlset>\n',encoding='utf-8')
    print('Generated:',len(projects),'case pages and homepage')
if __name__=='__main__': run()
