"""
Utilities for non-AI browser tasks (e.g., taking webpage screenshots).

Requires Playwright runtime. After installing the Python package, run once:

    playwright install chromium

Example:
    from utils.ai.tools import save_page_screenshot
    path = save_page_screenshot("https://www.nasa.gov", "out/nasa.png", full_page=True)
    print(path)
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def save_page_screenshot(
    url: str,
    out_path: str = "screenshot.png",
    *,
    full_page: bool = True,
    width: int = 1280,
    height: int = 800,
    wait_until: str = "load",
    device_scale_factor: float = 1,
    timeout_ms: int = 120000,
    ready_selector: str = "canvas",
    post_wait_ms: int = 6000,
) -> str:
    """
    Take a screenshot of a URL using headless Chromium (Playwright) and save it to disk.

    Args:
        url: Target page URL.
        out_path: Output file path (PNG). Parent dirs are created if needed.
        full_page: If True, capture full-page (can be long for infinite pages).
        width/height: Viewport size.
        wait_until: Initial navigation wait state ("load", "domcontentloaded", "networkidle").
        device_scale_factor: Pixel density (1=normal, 2=retina-like, etc.).
        timeout_ms: Navigation and waits timeout in milliseconds.
        ready_selector: CSS selector to wait until visible (default 'canvas').
        post_wait_ms: Extra settling time after network idle to allow dynamic tiles to render.

    Returns:
        Absolute path where the screenshot was saved.

    Raises:
        RuntimeError on browser/runtime issues (e.g., missing Chromium install).
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=device_scale_factor,
                )
                page = context.new_page()
                # 1) Navigate
                page.goto(url, wait_until=wait_until, timeout=timeout_ms)

                # 2) Ensure DOM base is present
                page.wait_for_selector("body", state="visible", timeout=timeout_ms)

                # 3) Wait for a visible map/canvas container if provided
                if ready_selector:
                    page.wait_for_selector(
                        ready_selector, state="visible", timeout=timeout_ms
                    )

                # 4) Let network settle and give extra time for tiles/layers to paint
                try:
                    page.wait_for_load_state("networkidle", timeout=timeout_ms)
                except Exception:
                    # Some apps never reach networkidle due to polling; continue best effort
                    pass

                if post_wait_ms > 0:
                    page.wait_for_timeout(post_wait_ms)

                # 5) Sanity check: ensure at least one canvas has non-zero bbox
                try:
                    canvases = page.query_selector_all("canvas")
                    any_ok = False
                    for c in canvases:
                        box = c.bounding_box()
                        if box and box.get("width", 0) > 4 and box.get("height", 0) > 4:
                            any_ok = True
                            break
                    # If no canvas sized, wait a bit more
                    if not any_ok:
                        page.wait_for_timeout(4000)
                except Exception:
                    # Ignore if site has no canvas or access fails
                    pass

                page.screenshot(path=str(out), full_page=full_page)
                return str(out.resolve())
            finally:
                browser.close()
    except Exception as e:
        msg = (
            "Playwright failed. Make sure browsers are installed with: "
            "`playwright install chromium`. Original error: %s" % (e,)
        )
        raise RuntimeError(msg) from e


__all__ = ["save_page_screenshot"]
