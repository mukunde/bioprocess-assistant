"""Serve a local, read-only view of graph chat traces."""
import argparse
from collections import defaultdict
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "tmp" / "graph-chat-traces"
SPAN_NAMES = {"graph_chat.request", "anthropic.messages.create", "neo4j.search"}


def read_traces(directory):
    traces = defaultdict(list)
    skipped = 0
    for path in sorted(directory.glob("graph-chat-*.jsonl")):
        try:
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    # The exporter may still be writing the final line.
                    if not line.endswith("\n"):
                        continue
                    try:
                        row = json.loads(line)
                        if (row["schema"] != "graph-chat-trace/v1"
                                or row["name"] not in SPAN_NAMES
                                or not isinstance(row["trace_id"], str)
                                or type(row["start_time_unix_nano"]) is not int
                                or type(row["duration_ms"]) not in (int, float)
                                or not math.isfinite(row["duration_ms"])
                                or row["duration_ms"] < 0
                                or not isinstance(row["attributes"], dict)):
                            raise ValueError("Unexpected span")
                        traces[row["trace_id"]].append(row)
                    except (KeyError, ValueError, TypeError, OverflowError):
                        skipped += 1
        except (OSError, UnicodeError):
            skipped += 1
    for spans in traces.values():
        spans.sort(key=lambda row: row["start_time_unix_nano"])
    return sorted(traces.items(), key=lambda item: item[1][0]["start_time_unix_nano"],
                  reverse=True), skipped


def number(value, places=0):
    if type(value) in (int, float) and math.isfinite(value) and value >= 0:
        return f"{value:,.{places}f}"
    return "—"


def render_span(row, origin, width):
    attributes = row["attributes"]
    offset = (row["start_time_unix_nano"] - origin) / 1e6
    left = 100 * offset / width
    size = 100 * row["duration_ms"] / width
    result = attributes.get("outcome") or row.get("status") or "—"
    for key in ("gen_ai.response.stop_reason", "grounding.rejection_reason"):
        reason = attributes.get(key)
        if reason:
            result = f"{result} · {reason}"
    failed = row.get("status") == "ERROR"
    usage = " · ".join(
        f"{label} {number(attributes.get(key))}" for label, key in (
            ("Input", "usage.input_tokens"), ("Output", "usage.output_tokens"),
            ("Cache read", "usage.cache_read_input_tokens"),
            ("Cache write", "usage.cache_creation_input_tokens"),
        )
    ) if row["name"] == "anthropic.messages.create" else "—"
    cost = number(attributes.get("cost.estimated_usd"), 6)
    label = {"graph_chat.request": "Graph chat", "anthropic.messages.create": "Anthropic",
             "neo4j.search": "Neo4j"}[row["name"]]
    color = "error" if failed else {"Anthropic": "model", "Neo4j": "database"}.get(label, "")
    return (f"<tr><th scope='row'>{label}</th>"
            f"<td><div class='track' title='Starts at {offset:.1f} ms'>"
            f"<span class='bar {color}' style='left:{left:.4f}%;width:{size:.4f}%'></span>"
            f"</div></td><td>{number(row['duration_ms'], 1)}</td>"
            f"<td>{escape(str(result))}</td><td>{usage}</td><td>{cost}</td></tr>")


def page(traces, selected, skipped):
    choices = dict(traces)
    if selected not in choices:
        selected = traces[0][0] if traces else None
    nav = []
    for trace_id, spans in traces:
        root = next((row for row in spans if row["name"] == "graph_chat.request"), None)
        label = (f"{number(root['duration_ms'], 1)} ms" if root else "Missing root")
        href = "?" + urlencode({"trace": trace_id})
        current = " aria-current='page'" if trace_id == selected else ""
        nav.append(f"<li><a href='{escape(href)}'{current}>"
                   f"<code>{escape(trace_id[:12])}</code> · {label}</a></li>")
    body = ("<p>No traces yet. Enable graph chat tracing, then refresh after "
            "a trace has been exported.</p>")
    if selected is not None:
        spans = choices[selected]
        start = spans[0]["start_time_unix_nano"]
        width = max(1, max((row["start_time_unix_nano"] - start) / 1e6 + row["duration_ms"]
                           for row in spans))
        costs = [row["attributes"].get("cost.estimated_usd") for row in spans
                 if row["name"] == "anthropic.messages.create"]
        known = [cost for cost in costs if number(cost) != "—"]
        total = f"${sum(known):.6f}" if known else "—"
        rows = "".join(render_span(row, start, width) for row in spans)
        body = (f"<h2>Trace <code>{escape(selected)}</code></h2>"
                f"<p>{len(spans)} spans · timeline {width:.1f} ms · "
                f"estimated USD {total} ({len(known)}/{len(costs)} model calls priced)</p>"
                "<div class='table'><table><thead><tr><th>Step</th><th>Timeline</th>"
                "<th>ms</th><th>Outcome</th><th>Tokens</th><th>Est. USD</th>"
                f"</tr></thead><tbody>{rows}</tbody></table></div>")
    warning = f"<p>Skipped {skipped} unreadable rows or files.</p>" if skipped else ""
    refresh = "?" + urlencode({"trace": selected}) if selected is not None else "/"
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Graph chat traces</title>
<style>
body{{font:16px system-ui,sans-serif;background:#f1f5f9;color:#152538;margin:0;padding:2rem}}
header,section,aside{{background:white;border:1px solid #d7e1ea;border-radius:12px;padding:1rem}}
main{{display:grid;grid-template-columns:minmax(13rem,19rem) minmax(0,1fr);gap:1rem;margin-top:1rem}}
h1,h2{{margin:.25rem 0}} h2{{overflow-wrap:anywhere}} ul{{list-style:none;padding:0;margin:0}}
a{{color:#14578e}} li a{{display:block;padding:.55rem}}
a[aria-current=page]{{background:#e0effb;font-weight:bold}}
.table{{overflow-x:auto}} table{{border-collapse:collapse;width:100%}}
th,td{{padding:.65rem;text-align:left;border-bottom:1px solid #e2e8f0}}
.track{{position:relative;height:.8rem;background:#e2e8f0;min-width:9rem;border-radius:5px}}
.bar{{position:absolute;height:100%;min-width:1px;background:#334155;border-radius:5px}}
.model{{background:#275dbe}} .database{{background:#137c68}} .error{{background:#b33439}}
@media(max-width:760px){{body{{padding:.7rem}}main{{grid-template-columns:1fr}}}}
</style>
<body><header><h1>Graph chat traces</h1><p>Local OpenTelemetry viewer ·
<a href="{escape(refresh)}">Refresh selected trace</a> · <a href="/">Latest trace</a></p></header>
<main><aside><h2>Requests ({len(traces)})</h2><ul>{''.join(nav)}</ul></aside>
<section>{warning}{body}</section></main></body></html>"""


def handler(directory):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            if url.path != "/":
                self.send_error(404)
                return
            traces, skipped = read_traces(directory)
            selected = parse_qs(url.query).get("trace", [None])[0]
            content = page(traces, selected, skipped).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(content)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler(TRACE_DIR)) as server:
        print(f"http://127.0.0.1:{server.server_port}/", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
