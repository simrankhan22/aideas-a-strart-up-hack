import argparse
import json
import os
import re
import sys
from dataclasses import replace
from html import unescape
import math
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlparse
import xml.etree.ElementTree as ET

import requests

from config_app import AppConfig, as_dict, load_config


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
BLOCKED_SOURCE_DOMAINS = {
    "zhihu.com",
    "m.zhihu.com",
    "baidu.com",
    "tieba.baidu.com",
    "pinterest.com",
}
RESEARCH_REQUIRED_KEYS = [
    "client_name",
    "client_business",
    "target_country",
    "summary",
    "compliance_requirements",
    "unclear_or_unsure",
    "possibly_outdated",
    "follow_up_research_queries",
    "sources_used",
]


def extract_json(text: str, required_keys: list[str] | None = None) -> dict:
    raw = text.strip()
    if not raw:
        raise ValueError("Model returned an empty response.")

    candidates: list[str] = []
    candidates.append(raw)

    fenced = re.findall(r"```(?:json)?\s*([\s\S]*?)```", raw, flags=re.IGNORECASE)
    for block in fenced:
        block = block.strip()
        if block:
            candidates.append(block)

    decoder = json.JSONDecoder()
    for idx, ch in enumerate(raw):
        if ch != "{":
            continue
        try:
            parsed, end = decoder.raw_decode(raw[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            candidates.append(raw[idx : idx + end])

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(raw[start : end + 1])

    seen = set()
    ordered = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        ordered.append(candidate)

    ordered.sort(key=len, reverse=True)
    for candidate in ordered:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            if required_keys and not all(key in parsed for key in required_keys):
                continue
            return parsed

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse valid JSON object from model response: {exc}")
    if isinstance(parsed, dict):
        if required_keys and not all(key in parsed for key in required_keys):
            raise ValueError("Parsed JSON missing required top-level keys.")
        return parsed
    raise ValueError("Could not parse valid JSON object from model response.")


def build_queries(config: AppConfig) -> list[str]:
    business = config.client_business
    country = config.target_country
    return [
        f"{business} licensing requirements in {country}",
        f"{business} compliance paperwork in {country}",
        f"{country} company registration steps for {business}",
        f"{country} tax and VAT obligations for {business}",
        f"{country} labor law and payroll compliance for {business}",
        f"{country} privacy and data protection requirements for {business}",
        f"{country} official business registration authority",
        f"{country} government website permits licenses business",
    ]


def clean_html_fragment(value: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", value)
    no_whitespace = re.sub(r"\s+", " ", no_tags)
    return unescape(no_whitespace).strip()


def is_allowed_source_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
    except ValueError:
        return False
    if not host:
        return False
    if host.startswith("www."):
        host = host[4:]
    return host not in BLOCKED_SOURCE_DOMAINS


def search_web_bing_rss(query: str, max_results: int) -> list[dict]:
    url = (
        "https://www.bing.com/search?"
        f"q={quote_plus(query)}&format=rss&setlang=en-US&cc=us&mkt=en-US"
    )
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=25,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)

    results = []
    seen = set()
    for item in root.findall("./channel/item"):
        title = clean_html_fragment(item.findtext("title") or "")
        item_url = (item.findtext("link") or "").strip()
        description = clean_html_fragment(item.findtext("description") or "")
        if not title or not item_url:
            continue
        if not is_allowed_source_url(item_url):
            continue
        if item_url in seen:
            continue
        seen.add(item_url)
        results.append(
            {
                "title": title,
                "url": item_url,
                "query": query,
                "description": description,
            }
        )
        if len(results) >= max_results:
            break
    return results


def extract_text_from_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def score_source(item: dict, config: AppConfig) -> int:
    text = " ".join(
        [
            item.get("title", ""),
            item.get("url", ""),
            item.get("query", ""),
            item.get("description", ""),
        ]
    ).lower()
    host = urlparse(item.get("url", "")).netloc.lower()

    score = 0
    if config.target_country.lower() in text:
        score += 4
    if ".gov" in host or host.endswith(".gov"):
        score += 5
    if any(token in host for token in ("ministry", "agency", "authority", "tax")):
        score += 3
    if any(token in text for token in ("official", "government", "authority", "agency")):
        score += 3
    if any(
        token in text
        for token in (
            "compliance",
            "license",
            "permit",
            "registration",
            "tax",
            "vat",
            "privacy",
            "payroll",
            "labor law",
            "gdpr",
        )
    ):
        score += 2
    if "wikipedia.org" in host:
        score -= 1
    return score


def fetch_page_excerpt(url: str, max_chars: int = 3000) -> str:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=20,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException:
        return ""

    text = extract_text_from_html(response.text)
    return text[:max_chars]


def gather_sources(config: AppConfig) -> list[dict]:
    queries = build_queries(config)
    gathered: list[dict] = []
    seen_urls = set()

    per_query = max(2, math.ceil(config.max_search_results / max(1, len(queries))) * 2)
    for query in queries:
        for item in search_web_bing_rss(query, per_query):
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            gathered.append(item)

    gathered.sort(key=lambda item: score_source(item, config), reverse=True)
    shortlisted = gathered[: config.max_search_results]

    enriched = []
    for source in shortlisted[: config.max_pages_to_read]:
        excerpt = fetch_page_excerpt(source["url"])
        if not excerpt:
            excerpt = source.get("description", "")
        if not excerpt:
            continue
        enriched.append(
            {
                "title": source["title"],
                "url": source["url"],
                "query": source["query"],
                "excerpt": excerpt,
            }
        )
    return enriched


def research_with_claude(
    api_key: str,
    config: AppConfig,
    sources: list[dict],
) -> dict:
    system_prompt = (
        "You are a compliance research analyst. "
        "Use the provided web excerpts to produce light operational compliance research. "
        "Return ONLY valid JSON with this exact schema: "
        "{"
        "\"client_name\": string,"
        "\"client_business\": string,"
        "\"target_country\": string,"
        "\"summary\": string,"
        "\"compliance_requirements\": ["
        "  {\"item\": string, \"details\": string, \"confidence\": \"high|medium|low\", \"source_urls\": [string]}"
        "],"
        "\"unclear_or_unsure\": ["
        "  {\"topic\": string, \"reason\": string, \"what_to_verify\": string, \"priority\": \"high|medium|low\"}"
        "],"
        "\"possibly_outdated\": ["
        "  {\"topic\": string, \"reason\": string, \"what_to_recheck\": string, \"priority\": \"high|medium|low\"}"
        "],"
        "\"follow_up_research_queries\": [string],"
        "\"sources_used\": ["
        "  {\"title\": string, \"url\": string}"
        "]"
        "}. "
        "Rules: "
        "1) Keep findings practical and concise. "
        "2) If evidence is weak/unclear, put it in unclear_or_unsure. "
        "3) If you suspect date-sensitive changes, put them in possibly_outdated. "
        "4) Return compact JSON only, no markdown/code fences/preface text. "
        "5) Max 5 compliance_requirements, 4 unclear_or_unsure, 4 possibly_outdated, "
        "5 follow_up_research_queries. "
        "6) Keep each details/reason/what_to_verify/what_to_recheck short (max 160 chars)."
    )

    payload = {
        "config": as_dict(config),
        "sources": sources,
    }

    last_error = None
    for attempt, extra_constraint in enumerate(
        [
            "",
            "Previous output was not parseable JSON or was truncated. "
            "Return a shorter valid JSON object only.",
        ],
        start=1,
    ):
        user_text = json.dumps(payload, ensure_ascii=False)
        if extra_constraint:
            user_text = f"{extra_constraint}\n\n{user_text}"

        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": config.anthropic_model,
                "max_tokens": 2000,
                "temperature": 0.2,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_text}],
                    }
                ],
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        chunks = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                chunks.append(block.get("text", ""))
        raw_text = "\n".join(chunks)

        try:
            return extract_json(raw_text, required_keys=RESEARCH_REQUIRED_KEYS)
        except ValueError as exc:
            stop_reason = data.get("stop_reason")
            debug_path = Path("debug_web_research_raw.txt")
            debug_path.write_text(raw_text, encoding="utf-8")
            last_error = (
                f"{exc}; stop_reason={stop_reason}; "
                f"attempt={attempt}; raw_saved={debug_path}"
            )
            if stop_reason != "max_tokens" and attempt == 1:
                continue

    raise ValueError(last_error or "Unknown Claude parsing error.")


def research_with_claude_web_search_tool(api_key: str, config: AppConfig) -> dict:
    system_prompt = (
        "You are a compliance research analyst. "
        "Use web search to gather light, practical compliance and paperwork guidance "
        "for operating a business in the target country. "
        "Return ONLY valid JSON with this exact schema: "
        "{"
        "\"client_name\": string,"
        "\"client_business\": string,"
        "\"target_country\": string,"
        "\"summary\": string,"
        "\"compliance_requirements\": ["
        "  {\"item\": string, \"details\": string, \"confidence\": \"high|medium|low\", \"source_urls\": [string]}"
        "],"
        "\"unclear_or_unsure\": ["
        "  {\"topic\": string, \"reason\": string, \"what_to_verify\": string, \"priority\": \"high|medium|low\"}"
        "],"
        "\"possibly_outdated\": ["
        "  {\"topic\": string, \"reason\": string, \"what_to_recheck\": string, \"priority\": \"high|medium|low\"}"
        "],"
        "\"follow_up_research_queries\": [string],"
        "\"sources_used\": ["
        "  {\"title\": string, \"url\": string}"
        "]"
        "}. "
        "Rules: "
        "1) Return compact JSON only, no markdown/code fences/preface text. "
        "2) Max 4 compliance_requirements, 3 unclear_or_unsure, 3 possibly_outdated, "
        "4 follow_up_research_queries. "
        "3) Keep each details/reason/what_to_verify/what_to_recheck short (max 140 chars). "
        "4) No <cite> tags and no markdown."
    )
    user_prompt = (
        f"Client name: {config.client_name}\n"
        f"Client business: {config.client_business}\n"
        f"Target country: {config.target_country}\n"
        "Do light research with a focus on compliance/paperwork needed to operate."
    )

    last_error = None
    for attempt, retry_prefix in enumerate(
        [
            "",
            "Your previous answer was not parseable JSON and/or too long. "
            "Return much shorter valid JSON only.",
        ],
        start=1,
    ):
        message_text = user_prompt
        if retry_prefix:
            message_text = f"{retry_prefix}\n\n{user_prompt}"
        max_uses = 3 if attempt == 1 else 2

        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": config.anthropic_model,
                "max_tokens": 2000,
                "temperature": 0.2,
                "system": system_prompt,
                "messages": [{"role": "user", "content": message_text}],
                "tools": [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": max_uses,
                    }
                ],
            },
            timeout=150,
        )
        response.raise_for_status()
        data = response.json()

        chunks = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                chunks.append(block.get("text", ""))
        raw_text = "\n".join(chunks)

        try:
            return extract_json(raw_text, required_keys=RESEARCH_REQUIRED_KEYS)
        except ValueError as exc:
            stop_reason = data.get("stop_reason")
            debug_path = Path("debug_web_research_raw.txt")
            debug_path.write_text(raw_text, encoding="utf-8")
            last_error = (
                f"{exc}; stop_reason={stop_reason}; "
                f"attempt={attempt}; raw_saved={debug_path}"
            )
            if stop_reason != "max_tokens" and attempt == 1:
                continue

    raise ValueError(last_error or "Unknown Claude parsing error.")


def normalize_output(result: dict, config: AppConfig, sources: list[dict]) -> dict:
    normalized = {
        "client_name": result.get("client_name") or config.client_name,
        "client_business": result.get("client_business") or config.client_business,
        "target_country": result.get("target_country") or config.target_country,
        "summary": result.get("summary") or "",
        "compliance_requirements": result.get("compliance_requirements") or [],
        "unclear_or_unsure": result.get("unclear_or_unsure") or [],
        "possibly_outdated": result.get("possibly_outdated") or [],
        "follow_up_research_queries": result.get("follow_up_research_queries") or [],
        "sources_used": result.get("sources_used") or [],
        "meta": {
            "model": config.anthropic_model,
            "source_count": len(sources),
        },
    }
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run light web research for client/country compliance and output "
            "JSON with unsure/outdated follow-up items."
        )
    )
    parser.add_argument("--client-name", default=None)
    parser.add_argument("--client-business", default=None)
    parser.add_argument("--target-country", default=None)
    parser.add_argument(
        "--output-json",
        default="research.json",
        help="Output path for research JSON (default: research.json)",
    )
    parser.add_argument("--max-search-results", type=int, default=None)
    parser.add_argument("--max-pages-to-read", type=int, default=None)
    parser.add_argument(
        "--allow-rss-fallback",
        action="store_true",
        help=(
            "Allow Bing RSS + page scraping fallback if Anthropic web-search tool "
            "is unavailable."
        ),
    )
    return parser.parse_args()


def apply_overrides(config: AppConfig, args: argparse.Namespace) -> AppConfig:
    updated = config
    if args.client_name:
        updated = replace(updated, client_name=args.client_name)
    if args.client_business:
        updated = replace(updated, client_business=args.client_business)
    if args.target_country:
        updated = replace(updated, target_country=args.target_country)
    if args.max_search_results is not None:
        updated = replace(updated, max_search_results=max(1, args.max_search_results))
    if args.max_pages_to_read is not None:
        updated = replace(updated, max_pages_to_read=max(1, args.max_pages_to_read))
    return updated


def main() -> int:
    args = parse_args()
    config = apply_overrides(load_config(), args)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Missing ANTHROPIC_API_KEY in environment or .env", file=sys.stderr)
        return 1

    sources: list[dict] = []
    try:
        result = research_with_claude_web_search_tool(api_key=api_key, config=config)
        method = "anthropic_web_search_tool"
    except requests.HTTPError as exc:
        body = exc.response.text if exc.response is not None else ""
        if not args.allow_rss_fallback:
            print(
                "Anthropic web-search tool request failed. "
                "Enable web search in Anthropic Console or run with "
                "--allow-rss-fallback.",
                file=sys.stderr,
            )
            print(f"Reason: {exc}", file=sys.stderr)
            if body:
                print(body, file=sys.stderr)
            return 1

        print(
            "Anthropic web search tool failed, using RSS fallback. "
            f"Reason: {exc}",
            file=sys.stderr,
        )
        if body:
            print(body, file=sys.stderr)

        try:
            sources = gather_sources(config)
        except requests.HTTPError as search_exc:
            print(f"Fallback web search failed: {search_exc}", file=sys.stderr)
            return 1

        if not sources:
            print("No web sources were collected. Try broader inputs.", file=sys.stderr)
            return 1

        try:
            result = research_with_claude(api_key=api_key, config=config, sources=sources)
            method = "rss_search_fallback"
        except requests.HTTPError as model_exc:
            model_body = model_exc.response.text if model_exc.response is not None else ""
            print(f"Claude API request failed: {model_exc}\n{model_body}", file=sys.stderr)
            return 1
        except ValueError as parse_exc:
            print(f"Failed to parse Claude output: {parse_exc}", file=sys.stderr)
            return 1
    except ValueError as parse_exc:
        print(f"Failed to parse Claude output: {parse_exc}", file=sys.stderr)
        return 1

    output = normalize_output(result=result, config=config, sources=sources)
    output["meta"]["research_method"] = method
    output_json = json.dumps(output, indent=2, ensure_ascii=False)
    print(output_json)

    output_path = Path(args.output_json)
    output_path.write_text(output_json + "\n", encoding="utf-8")
    print(f"Saved research JSON to: {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
