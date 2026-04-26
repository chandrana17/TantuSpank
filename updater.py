"""
updater.py — TantuSpank Update Checker
Checks GitHub Releases API for newer versions on startup.
Privacy-first: only pings GitHub's public API, sends zero user data.
"""
import threading
import urllib.request
import json
import webbrowser
import logging

from constants import APP_VERSION, APP_NAME

_logger = logging.getLogger(APP_NAME)

# GitHub Releases API endpoint (public, no auth needed)
GITHUB_OWNER = "chandrana17"
GITHUB_REPO = "TantuSpank"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _parse_version(version_str: str) -> tuple:
    """Parse 'v1.2.3' or '1.2.3' into (1, 2, 3) tuple for comparison."""
    clean = version_str.strip().lstrip("v")
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _is_newer(remote: str, local: str) -> bool:
    """Return True if remote version is strictly newer than local."""
    return _parse_version(remote) > _parse_version(local)


def _check_for_update(icon_ref, on_result=None):
    """
    Background worker: hits GitHub Releases API, compares versions.
    If a newer version exists, fires a tray notification.
    """
    try:
        req = urllib.request.Request(
            RELEASES_URL,
            headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        remote_tag = data.get("tag_name", "")
        remote_name = data.get("name", remote_tag)
        download_url = data.get("html_url", f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases")

        if _is_newer(remote_tag, APP_VERSION):
            _logger.info(f"[UPDATE] New version available: {remote_tag} (current: v{APP_VERSION})")

            # Show tray notification
            if icon_ref:
                try:
                    icon_ref.notify(
                        f"Update available! {remote_name}\nRight-click tray → Check for Updates",
                        f"{APP_NAME} Update"
                    )
                except Exception:
                    pass

            # Store result for menu callback
            if on_result:
                on_result(remote_tag, download_url)
        else:
            _logger.info(f"[UPDATE] Up to date (v{APP_VERSION})")

    except Exception as e:
        # Silently fail — don't annoy users with network errors
        _logger.info(f"[UPDATE] Check failed (offline?): {e}")


# ── Module-level state for latest release info ──
_latest_version = None
_latest_url = None
_update_lock = threading.Lock()


def _store_result(version, url):
    """Callback to store update info for the tray menu."""
    global _latest_version, _latest_url
    with _update_lock:
        _latest_version = version
        _latest_url = url


def check_for_updates_async(icon_ref):
    """
    Non-blocking update check. Call this once on startup.
    Runs in a daemon thread so it won't block the app.
    """
    t = threading.Thread(
        target=_check_for_update,
        args=(icon_ref, _store_result),
        daemon=True
    )
    t.start()


def has_update() -> bool:
    """Return True if a newer version was found."""
    with _update_lock:
        return _latest_version is not None


def get_update_info() -> tuple:
    """Return (version_tag, download_url) or (None, None)."""
    with _update_lock:
        return _latest_version, _latest_url


def open_download_page(icon_ref=None, item=None):
    """Open the GitHub releases page in the browser."""
    _, url = get_update_info()
    if url:
        webbrowser.open(url)
    else:
        webbrowser.open(f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases")


def on_check_updates_clicked(icon_ref, item):
    """Manual 'Check for Updates' menu handler."""
    def _manual_check():
        _check_for_update(icon_ref, _store_result)
        if has_update():
            ver, _ = get_update_info()
            if icon_ref:
                try:
                    icon_ref.notify(
                        f"Version {ver} is available! Click 'Download Update' in the menu.",
                        f"{APP_NAME} Update"
                    )
                except Exception:
                    pass
        else:
            if icon_ref:
                try:
                    icon_ref.notify(
                        f"You're on the latest version (v{APP_VERSION})!",
                        f"{APP_NAME}"
                    )
                except Exception:
                    pass

    threading.Thread(target=_manual_check, daemon=True).start()
