"""Prepare a fresh, immutable PDF-based subscription test; no LLM/API calls.

Conversion uses cached Docling layout weights, CPU and native PDF text only.
"""
from __future__ import annotations

import argparse
import faulthandler
import importlib.metadata
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from ingestion.claim_contract import ClaimExtraction, VERSION
from ingestion.claim_bundle import digest, verify_bundle


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def prepare(source: Path, output: Path, pages: list[int], resume_failed: bool = False, artifacts: Path | None = None,
            *, document_reference: str | None = None, document_version: str | None = None,
            selection_reason: str | None = None):
    # This stage never calls the legacy dense extraction pipeline.
    if output.exists() and not resume_failed:
        raise ValueError('Choose a new directory; prepared tests are never overwritten')
    metadata = {'document_reference': document_reference, 'document_version': document_version,
                'selection_reason': selection_reason}
    if any(not isinstance(v, str) or not v.strip() for v in metadata.values()):
        raise ValueError('Explicit document_reference, document_version and selection_reason are required')
    metadata = {k: v.strip() for k, v in metadata.items()}
    source = source.resolve(strict=True)
    if source.suffix.lower() != '.pdf' or source.read_bytes()[:5] != b'%PDF-':
        raise ValueError('A local PDF is required')
    if not pages or len(pages) > 3 or pages != sorted(set(pages)):
        raise ValueError('Use one to three distinct increasing page numbers')
    if os.environ.get('DOCLING_SERVE_URL'):
        raise ValueError('Remote Docling conversion is not supported by this test')
    artifacts = (artifacts or Path(__file__).resolve().parents[1] / '.local-tools/docling-models').resolve(strict=True)
    layout_folder = artifacts / 'docling-project--docling-layout-heron'
    if not (layout_folder / 'model.safetensors').is_file():
        raise ValueError('Preloaded Heron weights are required; this command never downloads weights')
    for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY'):
        os.environ[key] = '1'
    os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(source)
    if min(pages) < 1 or max(pages) > len(reader.pages):
        raise ValueError('Page outside PDF')
    if output.exists():
        status = json.loads((output / 'status.json').read_text(encoding='utf8'))
        previous = json.loads((output / 'source-map.json').read_text(encoding='utf8'))
        if status['status'] not in ('preparing', 'preparation_failed'):
            raise ValueError('Only an incomplete preparation may be resumed')
        if previous['original_sha256'] != digest(source) or [p['original_pdf_page'] for p in previous['pages']] != pages:
            raise ValueError('Resume requires identical source and pages')
        if any(previous.get(k) != v for k, v in metadata.items()):
            raise ValueError('Resume requires identical document metadata and selection reason')
        if any((output / name).exists() for name in ('plan.json', 'input.json', 'manual-prompt.txt', 'document.json')):
            raise ValueError('Resume cannot overwrite prepared benchmark material')
    else:
        output.mkdir(parents=True, exist_ok=False)
    dump(output / 'status.json', {'status': 'preparing', 'llm_calls': 0, 'api_calls': 0})
    writer = PdfWriter()
    for page in pages:
        writer.add_page(reader.pages[page - 1])
    excerpt = output / 'source.pdf'
    with excerpt.open('wb') as stream:
        writer.write(stream)
    source_map = {
        **metadata, 'metadata_status': 'supplied_by_operator_not_independently_verified',
        'original_pdf': str(source), 'original_sha256': digest(source),
        'original_page_count': len(reader.pages), 'excerpt_sha256': digest(excerpt),
        'pages': [{'excerpt_pdf_page': i + 1, 'original_pdf_page': p} for i, p in enumerate(pages)],
    }
    dump(output / 'source-map.json', source_map)
    # Installed Docling 2.140.0 supports these options. Disabled features are
    # explicit: no OCR/table inference for this born-digital, non-tabular excerpt.
    print('Loading cached local conversion runtime...', flush=True)
    faulthandler.dump_traceback_later(45, repeat=False)
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
    options = PdfPipelineOptions(
        do_ocr=False, do_table_structure=False, enable_remote_services=False,
        artifacts_path=artifacts,
        accelerator_options=AcceleratorOptions(num_threads=4, device=AcceleratorDevice.CPU),
    )
    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
    faulthandler.cancel_dump_traceback_later()
    print(f'Converting {len(pages)} PDF pages on CPU...', flush=True)
    try:
        result = converter.convert(excerpt)
        if str(result.status.value) != 'success':
            raise ValueError(f'Docling conversion did not succeed: {result.status}')
        document = result.document
        raw_document = document.model_dump(mode='json')
        dump(output / 'document.json', raw_document)
        elements = []
        for order, (item, level) in enumerate(document.iterate_items()):
            raw = item.model_dump(mode='json')
            prov = raw.get('prov', [])
            if not prov:
                continue
            text = raw.get('text')
            if not text and raw.get('label') == 'table':
                # Preserve row/cell structure instead of dropping table text.
                text = item.export_to_markdown(doc=document)
            if not text:
                continue
            original_pages = sorted({pages[p['page_no'] - 1] for p in prov})
            element = {
                'item_ref': raw['self_ref'], 'label': raw['label'], 'text': text,
                'marker': raw.get('marker'), 'original_pages': original_pages,
                'excerpt_pages': sorted({p['page_no'] for p in prov}),
                'provenance': prov, 'order_in_document': order, 'tree_level': level,
                'parent_ref': (raw.get('parent') or {}).get('$ref'),
                'heading_level': raw.get('level'),
            }
            if raw.get('label') == 'table':
                element['table_data'] = raw.get('data')
            elements.append(element)
        if not elements or {p for e in elements for p in e['original_pages']} != set(pages):
            raise ValueError('Missing text on an excerpt page')
        if len({e['item_ref'] for e in elements}) != len(elements):
            raise ValueError('Duplicate item IDs in conversion')
        corpus = {
            'document_reference': metadata['document_reference'],
            'document_version': metadata['document_version'],
            'metadata_status': source_map['metadata_status'],
            'original_pdf_sha256': source_map['original_sha256'],
            'document_sha256': digest(output / 'document.json'),
            'original_pages': pages, 'document_tree': raw_document['body'],
            'groups': raw_document.get('groups', []), 'elements': elements,
            'source_flags': [],
        }
        # No known answers, previous candidate results, old reference cards or
        # manually authored new-page claims enter the model input.
        schema = ClaimExtraction.model_json_schema()
        prompt = Path(__file__).with_name('claim_prompt_v02.txt').read_text(encoding='utf8')
        dump(output / 'input.json', corpus)
        dump(output / 'schema.json', schema)
        (output / 'prompt.txt').write_text(prompt, encoding='utf8')
        (output / 'manual-prompt.txt').write_text(
            prompt + '\nJSON SCHEMA:\n' + json.dumps(schema, ensure_ascii=False) +
            '\nDOCUMENT:\n' + json.dumps(corpus, ensure_ascii=False), encoding='utf8')
        dump(output / 'review-template.json', {
            'reviewer': None, 'human_approval': False, 'reference_status': 'not_annotated',
            'claim_reviews': [], 'source_issue_resolutions': [],
            'dimensions': ['source_entailment', 'predicate_direction', 'force_and_negation',
                'purpose_vs_applicability', 'quantity_units_denominators',
                'product_phase_scope', 'source_quarantine', 'omissions'],
        })
        conversion = {'docling_version': importlib.metadata.version('docling'),
            'do_ocr': False, 'do_table_structure': False, 'device': 'cpu',
            'remote_services': False, 'huggingface_offline': True,
            'artifacts_path': str(artifacts),
            'layout_files_sha256': {p.name: digest(p) for p in layout_folder.iterdir() if p.is_file()},
            'note': 'Different conversion profile from the old benchmark; no direct numerical score comparison without controlled re-execution.'}
        dump(output / 'conversion-profile.json', conversion)
        files = ['source.pdf', 'source-map.json', 'document.json', 'input.json',
                 'schema.json', 'prompt.txt', 'manual-prompt.txt', 'conversion-profile.json', 'review-template.json']
        dump(output / 'plan.json', {
            'status': 'prepared_not_executed', 'prepared_on': datetime.now(timezone.utc).date().isoformat(),
            'prepared_date_timezone': 'UTC',
            'contract_version': VERSION, 'selected_model': 'gpt-6.1-sol', 'effort': 'medium',
            'execution_mode': 'subscription_interface', 'api_calls_authorized': False,
            'additional_api_spend_eur': '0.00', 'max_generation_attempts': 1, 'automatic_retries': 0,
            'original_pages': pages, 'earlier_development_pages': [97, 98, 99],
            'selection_reason': metadata['selection_reason'],
            'document_reference': metadata['document_reference'],
            'document_version': metadata['document_version'],
            'evaluation_role': 'fresh development test, selected and inspected by the author; not a blind held-out benchmark',
            'reference_status': 'not_annotated', 'no_previous_answers_in_prompt': True,
            'publication_allowed': False, 'human_approval': False,
            'files': {name: digest(output / name) for name in files},
        })
        dump(output / 'status.json', {'status': 'prepared_not_executed', 'llm_calls': 0, 'api_calls': 0})
        verify_bundle(output)
    except Exception:
        dump(output / 'status.json', {'status': 'preparation_failed', 'llm_calls': 0, 'api_calls': 0})
        raise
    return {'prepared': True, 'pages': pages, 'elements': len(elements),
            'llm_calls': 0, 'manual_prompt_characters': len((output / 'manual-prompt.txt').read_text(encoding='utf8'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pages', type=int, nargs='+', required=True)
    parser.add_argument('--document-reference', required=True, help='Reference read from the source document')
    parser.add_argument('--document-version', required=True, help='Edition/version read from the source document')
    parser.add_argument('--selection-reason', required=True, help='Why these pages were selected; no preset rationale')
    parser.add_argument('--resume-failed', action='store_true', help='Resume only an identical, incomplete conversion with no prepared inputs')
    parser.add_argument('--artifacts', type=Path, help='Existing preloaded Docling artifacts directory')
    args = parser.parse_args()
    print(json.dumps(prepare(args.pdf, args.output.resolve(), args.pages, args.resume_failed, args.artifacts,
                             document_reference=args.document_reference, document_version=args.document_version,
                             selection_reason=args.selection_reason)))


if __name__ == '__main__':
    main()
