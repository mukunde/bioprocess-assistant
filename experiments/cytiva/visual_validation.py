"""Local conversion/chunking experiment. No extraction pipeline, LLM or database.

Heavy dependencies are imported only inside network-guarded workers. Each output
directory is new; chunking requires a hash-bound diagnostic review of conversion.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SELECTION = ROOT / 'docs/experiments/cytiva-visual-validation-selection.json'
REVISION = 'bbcd0e4846fadfcadac2800784783e59cd2722a9'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fresh(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=False)


def network_guard() -> list[str]:
    """Deny Python network connection/DNS events, including library downloads.

    This is not an OS firewall for native code. No native networking service or
    external inference process is started by this module.
    """
    for name in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY'):
        os.environ[name] = '1'
    os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
    os.environ['DO_NOT_TRACK'] = '1'
    os.environ.setdefault('TIKTOKEN_CACHE_DIR', str(ROOT/'.local-tools/tiktoken-cache'))
    os.environ['OMP_NUM_THREADS'] = '4'
    os.environ['MKL_NUM_THREADS'] = '4'
    if os.environ.get('DOCLING_SERVE_URL'):
        raise ValueError('DOCLING_SERVE_URL is forbidden')
    attempts = []

    def deny(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto'):
            attempts.append(event)  # Never log endpoints, keys or request content.
            raise RuntimeError(f'Network blocked: {event}')

    sys.addaudithook(deny)
    return attempts


def choose_blocks(selection: dict, names: list[str]) -> list[dict]:
    if not names or len(names) != len(set(names)):
        raise ValueError('Use distinct block IDs')
    by_id = {b['id']: b for b in selection['blocks']}
    if not set(names) <= by_id.keys():
        raise ValueError('Unknown block ID')
    return [by_id[name] for name in names]


def preflight(source: Path, artifacts: Path, selection: dict) -> dict:
    if digest(source) != selection['source']['sha256']:
        raise ValueError('Source SHA-256 differs from selected manual')
    versions = {name: metadata.version(name) for name in
                ('docling', 'docling-core', 'docling-graph', 'tiktoken', 'pypdf')}
    if versions != selection['observed_installed_versions']:
        raise ValueError('Runtime differs from the prepared selection; version a new experiment')
    origin = json.loads(metadata.distribution('docling-graph').read_text('direct_url.json') or '{}')
    if origin.get('vcs_info', {}).get('commit_id') != REVISION:
        raise ValueError('Docling Graph revision mismatch')
    required = [artifacts/'docling-project--docling-layout-heron'/n for n in
                ('model.safetensors', 'config.json', 'preprocessor_config.json')]
    required += [artifacts/'docling-project--docling-models/model_artifacts/tableformer/accurate'/n
                 for n in ('tableformer_accurate.safetensors', 'tm_config.json')]
    for file in required:
        if not file.is_file():
            raise ValueError(f'Missing cached conversion asset: {file.name}')
    cache = Path(os.environ['TIKTOKEN_CACHE_DIR']) / hashlib.sha1(
        b'https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken').hexdigest()
    if not cache.is_file() or digest(cache) != '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7':
        raise ValueError('Missing or invalid cached cl100k_base tokenizer; no download is allowed')
    import tiktoken
    encoding = tiktoken.get_encoding('cl100k_base')  # Fails rather than downloading under guard.
    if encoding.name != 'cl100k_base':
        raise ValueError('Tokenizer mismatch')
    return {'versions': versions, 'docling_graph_revision': REVISION,
            'weights': {str(p.relative_to(artifacts)): digest(p) for p in required},
            'source_sha256': digest(source), 'tokenizer': encoding.name,
            'tokenizer_file_sha256': digest(cache)}


def supervised(command: list[str], log: Path, timeout: int = 900) -> dict:
    """Bound each worker independently and retain diagnostics on failure."""
    try:
        import psutil
    except ImportError:
        psutil = None
    start = time.monotonic()
    peak = None
    reason = None
    with log.open('w', encoding='utf-8') as stream:
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                   cwd=ROOT, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        while process.poll() is None:
            if time.monotonic() - start > timeout:
                reason = 'timeout'
            if psutil:
                try:
                    parent = psutil.Process(process.pid)
                    rss = sum(p.memory_info().rss for p in [parent] + parent.children(recursive=True))
                    peak = max(peak or 0, rss)
                    if rss > 8 * 1024**3:
                        reason = 'resource_limit'
                except psutil.Error:
                    pass
            if reason:
                if psutil:
                    try:
                        for child in psutil.Process(process.pid).children(recursive=True):
                            child.kill()
                    except psutil.Error:
                        pass
                process.kill()
                break
            time.sleep(.25)
        code = process.wait()
    return {'status': reason or ('success' if code == 0 else 'failed'), 'returncode': code,
            'wall_seconds': round(time.monotonic() - start, 3),
            'peak_sampled_rss_bytes': peak, 'memory_scope': 'worker_and_children' if psutil else 'unknown'}


def convert(args) -> None:
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    attempts = network_guard()
    selection = json.loads(SELECTION.read_text(encoding='utf-8'))
    blocks = choose_blocks(selection, args.blocks)
    pf = preflight(args.source, args.artifacts, selection)
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(args.source)
    if len(reader.pages) != selection['source']['pdf_page_count']:
        raise ValueError('Page count mismatch')
    fresh(args.output)
    dump(args.output/'selection.json', selection)
    manifest = {**pf, 'status': 'running', 'llm_calls': 0, 'api_calls': 0,
                'network_guard': 'Python audit deny; not an OS firewall', 'workers': []}
    dump(args.output/'manifest.json', manifest)
    for block in blocks:
        folder = args.output/block['id']; fresh(folder)
        writer = PdfWriter()
        for n in block['pdf_pages_1based']:
            writer.add_page(reader.pages[n-1])
        with (folder/'source.pdf').open('wb') as stream:
            writer.write(stream)
        dump(folder/'source-map.json', {'source_sha256': pf['source_sha256'],
             'excerpt_sha256': digest(folder/'source.pdf'), 'pages': [
                 {'excerpt_page_1based': i+1, 'original_pdf_page_1based': n,
                  'original_pdf_page_index_0based': n-1, 'printed_page': block['printed_pages'][i]}
                 for i,n in enumerate(block['pdf_pages_1based'])]})
        for profile in ('T0','T1'):
            print(f'Converting {block["id"]} {profile} (local CPU)...', flush=True)
            result = supervised([sys.executable, '-m', 'experiments.cytiva.visual_validation',
                '_convert', '--source', str((folder/'source.pdf').resolve()), '--output',
                str((folder/profile).resolve()), '--artifacts', str(args.artifacts.resolve()),
                '--profile', profile,
                '--cell-matching' if args.cell_matching else '--no-cell-matching'], folder/f'{profile}.log')
            manifest['workers'].append({'block': block['id'], 'profile': profile, **result})
            dump(args.output/'manifest.json', manifest)
            if result['status'] != 'success':
                manifest['status'] = result['status']; dump(args.output/'manifest.json', manifest)
                raise RuntimeError(f'Conversion failed; inspect {folder/profile}.log')
    manifest.update(status='converted_pending_review', network_attempts=attempts)
    dump(args.output/'manifest.json', manifest)


def conversion_worker(args) -> None:
    attempts = network_guard()
    started = time.monotonic()
    from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions, TableFormerMode
    from docling.document_converter import DocumentConverter, PdfFormatOption
    options = PdfPipelineOptions(do_ocr=False, do_table_structure=args.profile == 'T1',
        table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE,
                                                     do_cell_matching=args.cell_matching),
        enable_remote_services=False, artifacts_path=args.artifacts,
        generate_page_images=True, generate_picture_images=True, images_scale=2,
        accelerator_options=AcceleratorOptions(num_threads=4, device=AcceleratorDevice.CPU))
    if options.table_structure_options.kind != 'docling_tableformer':
        raise RuntimeError('Unexpected table backend')
    fresh(args.output)
    dump(args.output/'profile.json', options.model_dump(mode='json', serialize_as_any=True))
    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
    loaded = time.monotonic()
    result = converter.convert(args.source)
    converted = time.monotonic()
    if result.status.value != 'success':
        raise RuntimeError(f'Conversion status: {result.status.value}')
    doc = result.document
    dump(args.output/'document.json', doc.model_dump(mode='json'))
    (args.output/'document.md').write_text(doc.export_to_markdown(), encoding='utf-8')
    for n,page in doc.pages.items():
        if page.image:
            page.image.pil_image.save(args.output/f'page-{n}.png')
    for i,table in enumerate(doc.tables):
        (args.output/f'table-{i}.html').write_text(table.export_to_html(doc=doc), encoding='utf-8')
        table.export_to_dataframe(doc=doc).to_csv(args.output/f'table-{i}.csv', index=False)
        table.get_image(doc).save(args.output/f'table-{i}.png')
    for i,picture in enumerate(doc.pictures):
        im = picture.get_image(doc)
        if im is not None:
            im.save(args.output/f'picture-{i}.png')
    dump(args.output/'metrics.json', {'import_and_setup_seconds': round(loaded-started,3),
         'first_conversion_seconds_including_lazy_model_load': round(converted-loaded,3),
         'export_seconds': round(time.monotonic()-converted,3),
         'tables': len(doc.tables), 'pictures': len(doc.pictures),
         'document_sha256': digest(args.output/'document.json'), 'network_attempts': attempts,
         'llm_calls': 0, 'api_calls': 0})


def validate_review(review: dict, run: Path) -> list[str]:
    if review.get('purpose') != 'diagnostic_chunking_only' or review.get('human_approved') is not False:
        raise ValueError('Explicit diagnostic-only review required; no approval is inferred')
    blocks = review.get('blocks')
    if not isinstance(blocks, dict) or not blocks:
        raise ValueError('No reviewed conversion blocks')
    for name, record in blocks.items():
        if name not in ('p077','p088','p104','p152-153','p053','p086','p142'):
            raise ValueError('Invalid block')
        if record.get('document_sha256') != digest(run/name/'T1/document.json'):
            raise ValueError('Reviewed conversion hash mismatch')
        if record.get('status') not in ('usable_for_diagnostic', 'quarantined_diagnostic_only'):
            raise ValueError('Conversion has not been inspected')
    return list(blocks)


def chunk(args) -> None:
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    network_guard()
    manifest = json.loads((args.run/'manifest.json').read_text(encoding='utf-8'))
    if any(metadata.version(name) != value for name,value in manifest['versions'].items()):
        raise ValueError('Chunking runtime differs from frozen conversion runtime')
    review = json.loads(args.review.read_text(encoding='utf-8'))
    blocks = validate_review(review, args.run)
    if args.budgets != sorted(set(args.budgets)) or not set(args.budgets) <= {600,800,1400}:
        raise ValueError('Use distinct sorted budgets from 600, 800, 1400')
    fresh(args.output)
    dump(args.output/'conversion-review.json', review)
    results = []
    for name in blocks:
        print(f'Chunking frozen conversion {name} (no LLM)...', flush=True)
        result = supervised([sys.executable, '-m', 'experiments.cytiva.visual_validation',
            '_chunk', '--source', str((args.run/name/'T1/document.json').resolve()),
            '--output', str((args.output/name).resolve()), '--budgets', *map(str,args.budgets)],
            args.output/f'{name}.log')
        results.append({'block': name, **result})
        dump(args.output/'manifest.json', {'workers': results, 'review_sha256': digest(args.review),
             'status': 'complete' if len(results)==len(blocks) and result['status']=='success' else 'incomplete',
             'diagnostic_only': True, 'human_approved': False, 'llm_calls': 0, 'api_calls': 0})
        if result['status'] != 'success':
            raise RuntimeError(f'Chunking failed; inspect {name}.log')


def chunk_worker(args) -> None:
    attempts = network_guard()
    start = time.monotonic()
    import tiktoken
    from docling_core.types.doc import DoclingDocument, RefItem
    from docling_graph.core.extractors.document_processor import DocumentProcessor
    from docling_graph.core.utils.doclang_format import serialize_doclang
    doc = DoclingDocument.model_validate_json(args.source.read_text(encoding='utf-8'))
    fresh(args.output)
    full = serialize_doclang(doc, add_location=False)  # Direct serializer: no markdown fallback.
    (args.output/'K0.doclang').write_text(full, encoding='utf-8')
    stats = {'K0_tokens': len(tiktoken.get_encoding('cl100k_base').encode(full)),
             'conversion_sha256': digest(args.source), 'variants': {}}
    for budget in args.budgets:
        processor = DocumentProcessor(llm_input_format='doclang', chunker_config={
            'chunk_max_tokens': budget, 'tokenizer_name': 'tiktoken', 'merge_peers': True})
        tokenizer = processor.chunker.tokenizer
        if getattr(getattr(tokenizer, 'tokenizer', None), 'name', None) != 'cl100k_base':
            raise RuntimeError('Tokenizer fallback forbidden')
        variant_start = time.monotonic()
        raw = []
        for i,c in enumerate(processor.chunker.chunker.chunk(doc)):
            text = processor.chunker.chunker.contextualize(chunk=c)
            raw.append({'raw_id': i, 'text': text, 'tokens': tokenizer.count_tokens(text),
                        'meta': c.meta.model_dump(mode='json')})
        texts, metas = processor.extract_chunks_with_metadata(doc)
        folder = args.output/f'K{budget}'; fresh(folder)
        dump(folder/'raw.json', raw)
        children = []
        for text, meta in zip(texts, metas, strict=True):
            refs = [ref for ref in meta['doc_item_refs']]
            # Resolve all provenance entries, retaining native metadata separately.
            all_pages = sorted({p.page_no for ref in refs for p in
                                RefItem(cref=ref).resolve(doc=doc).prov})
            children.append({'text': text, 'native_metadata': meta,
                             'all_item_provenance_pages': all_pages,
                             'anchor_scope': 'parent_items_not_exact_child_span' if meta['resplit_of'] is not None else 'backing_items'})
        dump(folder/'chunks.json', children)
        for i,text in enumerate(texts):
            (folder/f'chunk-{i:03}.doclang').write_text(text, encoding='utf-8')
        counts = [tokenizer.count_tokens(t) for t in texts]
        stats['variants'][f'K{budget}'] = {'raw_count': len(raw), 'final_count': len(texts),
            'total_tokens': sum(counts), 'max_tokens': max(counts,default=0),
            'secondary_resplits': sum(m['resplit_of'] is not None for m in metas),
            'tokens_within_budget': all(n<=budget for n in counts),
            'seconds_including_raw_and_native_passes': round(time.monotonic()-variant_start,3)}
    stats.update(seconds_including_imports=round(time.monotonic()-start,3), network_attempts=attempts,
                 llm_calls=0, api_calls=0)
    dump(args.output/'metrics.json', stats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    convert_p = commands.add_parser('convert')
    convert_p.add_argument('--source',type=Path,required=True)
    convert_p.add_argument('--output',type=Path,required=True)
    convert_p.add_argument('--artifacts',type=Path,default=ROOT/'.local-tools/docling-models')
    convert_p.add_argument('--blocks',nargs='+',default=['p077','p088'])
    convert_p.add_argument('--cell-matching', action=argparse.BooleanOptionalAction, default=True,
                           help='Match predicted table cells to PDF text cells (default: enabled)')
    chunk_p = commands.add_parser('chunk')
    chunk_p.add_argument('--run',type=Path,required=True)
    chunk_p.add_argument('--review',type=Path,required=True)
    chunk_p.add_argument('--output',type=Path,required=True)
    chunk_p.add_argument('--budgets',nargs='+',type=int,default=[800])
    worker = commands.add_parser('_convert')
    for name in ('source','output','artifacts'):
        worker.add_argument('--'+name,type=Path,required=True)
    worker.add_argument('--profile',choices=['T0','T1'],required=True)
    worker.add_argument('--cell-matching', action=argparse.BooleanOptionalAction, default=True)
    worker = commands.add_parser('_chunk')
    worker.add_argument('--source',type=Path,required=True)
    worker.add_argument('--output',type=Path,required=True)
    worker.add_argument('--budgets',nargs='+',type=int,required=True)
    args = parser.parse_args()
    {'convert': convert, 'chunk': chunk, '_convert': conversion_worker, '_chunk': chunk_worker}[args.command](args)


if __name__ == '__main__':
    main()
