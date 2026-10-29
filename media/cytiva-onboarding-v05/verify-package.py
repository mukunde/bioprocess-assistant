"""Read-only, dependency-free checks of the approved onboarding package."""
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

def read(name): return (ROOT/name).read_text(encoding='utf-8')
def load(name): return json.loads(read(name))
def digest(path, algorithm='sha256'):
    data=path.read_bytes()
    if algorithm == 'sha256_lf': data=data.replace(b'\r\n',b'\n')
    else: assert algorithm == 'sha256'
    return hashlib.sha256(data).hexdigest()
def norm(text): return ' '.join(text.split())
def shapes(svg):
    # Ignore editor metadata and wrapper transforms, never shape/style attributes.
    return [(e.tag.split('}')[-1],{k:v for k,v in e.attrib.items()
             if k not in ('id','data-hf-id')}) for e in ET.fromstring(svg).iter()
            if e.tag.split('}')[-1] in ('path','polygon')]

def verify():
    manifest=load('manifest.json')
    assert manifest['excluded_from_self_hash']==['manifest.json']
    for name, entry in manifest['files'].items():
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), name
        assert digest(path,entry['algorithm'])==entry['digest'], name
    # Working renderer outputs may exist, but are never package members.
    inventory={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
               and not any(part in ('node_modules','vendor','renders','__pycache__','.hyperframes',
                                     '.thumbnails','.waveform-cache') for part in p.relative_to(ROOT).parts)
               and p.suffix != '.log'}
    assert inventory==set(manifest['files'])|{'manifest.json'}, inventory ^ (set(manifest['files'])|{'manifest.json'})
    pkg=load('package.json'); lock=load('package-lock.json')
    assert pkg['name']==lock['name']==lock['packages']['']['name']
    assert pkg['dependencies']==lock['packages']['']['dependencies']
    for name,version in pkg['dependencies'].items():
        assert lock['packages']['node_modules/'+name]['version']==version
    index=read('composition/index.html')
    clips=re.findall(r'data-composition-src="([^"]+)"[^>]*data-start="([\d.]+)"[^>]*data-duration="([\d.]+)"',index)
    assert len(clips)==6
    edge=0
    for src,start,duration in clips:
        assert abs(float(start)-edge)<.0001
        edge=float(start)+float(duration)
        assert (ROOT/'composition'/src).is_file()
    assert edge==34
    refs=0
    for path in (ROOT/'composition').rglob('*.html'):
        for ref in re.findall(r'(?:src|href)="([^"]+)"',path.read_text(encoding='utf-8')):
            if ref.startswith('#'): continue
            assert not re.match(r'(?:https?:|file:|[A-Z]:)',ref), ref
            if ref=='assets/vendor/gsap.min.js': continue
            assert (path.parent/ref).is_file(), (path.name,ref)
            refs+=1
    provenance=load('provenance.json')
    for name,expected in provenance['decision_sha256'].items():
        assert digest(ROOT/'decisions'/name)==expected, name
    approved=load('decisions/human-decision-005.json')
    assert approved['status']=='human_approved' and approved['human_quote']=='validé'
    for key in ('video','poster'):
        entry=approved[key]
        assert digest(ROOT/'exports'/entry['file'])==entry['sha256']
    integration=load('integration-map.json')
    for case, expected in integration['source_svg_sha256'].items():
        assert digest(ROOT/'approved-arrows'/f'{case}.svg')==expected
    doc=read('composition/compositions/evidence.html')
    request=read('composition/compositions/request.html')
    actual_arrows=re.findall(r'<svg[^>]*class="guide-arrow".*?</svg>',request+doc,re.S)
    expected_cases=['case-long','case-short','case-short','case-source']
    assert len(actual_arrows)==4
    for arrow,case in zip(actual_arrows,expected_cases):
        assert shapes(arrow)==shapes(read(f'approved-arrows/{case}.svg')), case
    assert 'translate(0 99.5)' in actual_arrows[2]
    assert request.count('>GUIDE</div>')==3 and doc.count('>GUIDE</div>')==1
    evidence=json.loads((REPO/provenance['evidence_file']).read_text(encoding='utf-8'))
    source=next(p for p in evidence['passages'] if p['id']=='E121-W')
    blocks=[norm(html.unescape(re.sub('<[^>]+>','',s))).strip('… ').strip()
            for s in re.findall(r'<blockquote[^>]*>(.*?)</blockquote>',doc,re.S)]
    assert len(blocks)==1 and blocks[0]==provenance['production_receipt']['shown_quote']['text']
    assert blocks[0] in norm(source['quote']) and source['pdf_page_1based']==121
    assert provenance['production_receipt']['quarantine_remains_excluded']==['E118-I','E121-EQ']
    links=0
    for path in ROOT.glob('*.md'):
        for ref in re.findall(r'\[[^\]]+\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if ref.startswith(('https://','http://','#')): continue
            assert (path.parent/ref.split('#')[0]).resolve().is_file(), (path.name,ref)
            links+=1
    result={'status':'passed','package_files':len(inventory),'hashed_files':len(manifest['files']),
            'scenes':6,'duration_seconds':34,'approved_exports':2,'verbatim_decisions':5,
            'canonical_arrow_instances':4,'source_fragments_matched':1,'lock_consistent':True,
            'local_asset_references':refs,'local_documentation_links':links}
    print(json.dumps(result))
    return result

if __name__=='__main__': verify()
