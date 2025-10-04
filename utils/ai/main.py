"""
Gemini client and web search/analyze tool.

This module provides a reusable Gemini client and a web_search_and_analyze() tool that searches the web (DuckDuckGo), fetches page content, and asks Gemini to analyze with citations. Adds logging and input validation.
"""

from os import getenv
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from google import genai


# Basic logging for diagnostics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load env and init Gemini client
load_dotenv()
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in your environment/.env. Please set it to use Gemini."
    )

client = genai.Client(api_key=GEMINI_API_KEY)


@dataclass
class SearchResult:
    title: str
    href: str
    snippet: str


def _ddg_search(query: str, max_results: int = 5) -> List[SearchResult]:
    """Search the web using DuckDuckGo and return top results.

    No API key required. Safe for quick prototyping.
    """
    results: List[SearchResult] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(
                query,
                max_results=max_results,
                safesearch="moderate",
                timelimit="y",
                region="wt-wt",
            ):
                title = r.get("title") or ""
                href = r.get("href") or r.get("url") or ""
                snippet = r.get("body") or r.get("snippet") or ""
                if href:
                    results.append(
                        SearchResult(title=title, href=href, snippet=snippet)
                    )
    except Exception as e:
        logger.exception("DuckDuckGo search failed: %s", e)
    return results


def _fetch_page_text(url: str, timeout: int = 12) -> Optional[str]:
    """Fetch and clean visible text from a web page."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200 or not resp.content:
            return None

        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup(["script", "style", "noscript", "template"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text or None
    except Exception:
        logger.debug("Failed to fetch or parse: %s", url, exc_info=True)
        return None


def _is_url(text: str) -> bool:
    """Heuristic to detect if a string is a URL (http/https)."""
    try:
        parsed = urlparse(text.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def web_search_and_analyze(
    query: str,
    max_results: int = 5,
    max_chars_per_doc: int = 2000,
    model: str = "gemini-2.5-flash",
) -> Dict:
    """
    Perform a web search, fetch results, and ask Gemini to analyze with citations.

    Returns a dict with keys:
    - answer: Gemini's synthesized response.
    - sources: list of dicts: {title, url, snippet}
    - used_model: model name used
    """
    compiled_context_parts: List[str] = []
    sources: List[Dict[str, str]] = []

    # 1) Direct URL path
    if _is_url(query):
        text = _fetch_page_text(query)
        if text:
            excerpt = text[:max_chars_per_doc]
            hostname = urlparse(query).netloc
            compiled_context_parts.append(
                f"SOURCE: {hostname}\nURL: {query}\nSNIPPET: (direct URL)\nCONTENT: {excerpt}\n---\n"
            )
            sources.append({"title": hostname, "url": query, "snippet": "direct URL"})
        else:
            return {
                "answer": "No pude extraer contenido de la URL proporcionada.",
                "sources": [{"title": query, "url": query, "snippet": ""}],
                "used_model": model,
            }
    else:
        # 2) Search path
        hits = _ddg_search(query, max_results=max_results)
        if not hits:
            return {
                "answer": "No pude encontrar resultados en la búsqueda web.",
                "sources": [],
                "used_model": model,
            }

        # 3) Fetch content for top results
        for h in hits:
            text = _fetch_page_text(h.href)
            if not text:
                continue
            excerpt = text[:max_chars_per_doc]
            hostname = urlparse(h.href).netloc
            compiled_context_parts.append(
                f"SOURCE: {h.title or hostname}\nURL: {h.href}\nSNIPPET: {h.snippet}\nCONTENT: {excerpt}\n---\n"
            )
            sources.append(
                {"title": h.title or hostname, "url": h.href, "snippet": h.snippet}
            )

        if not compiled_context_parts:
            return {
                "answer": "Pude realizar la búsqueda pero no logré extraer contenido útil de las páginas.",
                "sources": [
                    {"title": h.title, "url": h.href, "snippet": h.snippet}
                    for h in hits
                ],
                "used_model": model,
            }

    context_blob = "\n".join(compiled_context_parts)

    prompt = (
        "Eres un analista que sintetiza información de la web. "
        "Usa las fuentes provistas para responder la consulta del usuario de forma concisa, "
        "incluye puntos clave y proporciona citas entre corchetes con el dominio principal (por ejemplo, [example.com]) "
        "cuando corresponda. Si hay desacuerdos entre fuentes, explícalos brevemente.\n\n"
        f"Consulta: {query}\n\n"
        "Fuentes (no inventes información fuera de esto):\n"
        f"{context_blob}\n"
        "Respuesta:"
    )

    # 3) Ask Gemini to analyze
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    answer_text = getattr(response, "text", None) or str(response)
    return {"answer": answer_text, "sources": sources, "used_model": model}


# Tool declaration for Gemini function calling
WEB_SEARCH_TOOL_DECLARATION: Dict = {
    "function_declarations": [
        {
            "name": "web_search_and_analyze",
            "description": "Busca en la web o analiza una URL y sintetiza una respuesta con citas.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "Consulta o URL directa",
                    },
                    "max_results": {
                        "type": "INTEGER",
                        "description": "Número de resultados de DuckDuckGo",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5,
                    },
                    "max_chars_per_doc": {
                        "type": "INTEGER",
                        "description": "Límite de caracteres por documento",
                        "default": 2000,
                    },
                    "model": {
                        "type": "STRING",
                        "description": "Modelo de Gemini",
                        "default": "gemini-2.5-flash",
                    },
                },
                "required": ["query"],
            },
        }
    ]
}


def execute_tool_call(name: str, arguments: Dict) -> Optional[Dict]:
    """Execute the declared tool by name with provided arguments."""
    if name == "web_search_and_analyze":
        return web_search_and_analyze(
            query=arguments.get("query", ""),
            max_results=int(arguments.get("max_results", 5)),
            max_chars_per_doc=int(arguments.get("max_chars_per_doc", 2000)),
            model=arguments.get("model", "gemini-2.5-flash"),
        )
    return None


__all__ = [
    "client",
    "web_search_and_analyze",
    "WEB_SEARCH_TOOL_DECLARATION",
    "execute_tool_call",
]
