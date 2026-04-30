"""Capture stage — turn a URL into raw text + metadata."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from ..config import settings

log = logging.getLogger(__name__)

_URL_RE = re.compile(r"https?://[^\s)>\]]+")

VIDEO_HOSTS = {
    "instagram.com": "instagram",
    "www.instagram.com": "instagram",
    "youtube.com": "youtube",
    "www.youtube.com": "youtube",
    "youtu.be": "youtube",
    "m.youtube.com": "youtube",
    "tiktok.com": "tiktok",
    "www.tiktok.com": "tiktok",
    "vm.tiktok.com": "tiktok",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "www.twitter.com": "twitter",
}


@dataclass
class CaptureResult:
    kind: str  # 'reel' | 'video' | 'article' | 'note'
    platform: str
    title: str
    author: str | None
    body: str  # transcript / article text / note
    media_path: str | None
    duration_sec: float | None
    metadata: dict


def detect_url(text: str) -> str | None:
    m = _URL_RE.search(text or "")
    return m.group(0) if m else None


def platform_for(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return VIDEO_HOSTS.get(host, "web")


def capture(url_or_text: str, *, given_title: str | None = None) -> CaptureResult:
    """Dispatch a URL or raw note to the right capture strategy."""
    url = detect_url(url_or_text)
    if not url:
        return _capture_note(url_or_text, given_title)

    platform = platform_for(url)
    if platform == "instagram":
        return _capture_video(url, platform="instagram", kind="reel", given_title=given_title)
    if platform in ("youtube", "tiktok", "twitter"):
        return _capture_video(url, platform=platform, kind="video", given_title=given_title)
    return _capture_article(url, given_title=given_title)


def _capture_note(text: str, given_title: str | None) -> CaptureResult:
    title = given_title or _first_line(text)[:120] or "Note"
    return CaptureResult(
        kind="note",
        platform="manual",
        title=title,
        author=None,
        body=text or "",
        media_path=None,
        duration_sec=None,
        metadata={},
    )


def _capture_article(url: str, *, given_title: str | None) -> CaptureResult:
    """Use trafilatura to fetch + extract main content from an article URL."""
    body = ""
    title = given_title or url
    author: str | None = None
    metadata: dict = {"source_url": url}

    try:
        import trafilatura
        from trafilatura.metadata import extract_metadata

        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            body = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
            md = extract_metadata(downloaded)
            if md is not None:
                title = given_title or md.title or title
                author = md.author
                metadata.update({
                    "site_name": md.sitename,
                    "date": md.date,
                    "categories": md.categories,
                    "tags": md.tags,
                })
    except Exception as e:  # noqa: BLE001
        log.warning("trafilatura failed for %s: %s", url, e)

    return CaptureResult(
        kind="article",
        platform=platform_for(url),
        title=title,
        author=author,
        body=body,
        media_path=None,
        duration_sec=None,
        metadata=metadata,
    )


def _capture_video(url: str, *, platform: str, kind: str, given_title: str | None) -> CaptureResult:
    """Use yt-dlp to grab metadata + (optionally) audio. Transcription happens later."""
    settings.ensure_dirs()
    target_dir = Path(settings.media_dir) / platform
    target_dir.mkdir(parents=True, exist_ok=True)

    info: dict = {}
    media_path: str | None = None
    body_parts: list[str] = []
    duration_sec: float | None = None

    try:
        from yt_dlp import YoutubeDL
        from yt_dlp.utils import DownloadError

        ydl_opts = {
            "outtmpl": str(target_dir / "%(id)s.%(ext)s"),
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": not settings.enable_whisper,  # only fetch audio when we'll transcribe
            "writeinfojson": False,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-US", "en-GB"],
            "subtitlesformat": "vtt",
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=settings.enable_whisper) or {}
            if settings.enable_whisper:
                req = info.get("requested_downloads") or []
                if req:
                    media_path = str(Path(req[0].get("filepath", "")).resolve())
        except DownloadError as e:
            log.warning("yt-dlp DownloadError for %s: %s", url, e)
    except Exception as e:  # noqa: BLE001
        log.warning("yt-dlp unavailable for %s: %s", url, e)

    title = given_title or info.get("title") or url
    author = info.get("uploader") or info.get("channel")
    description = info.get("description") or ""
    if description:
        body_parts.append(description)

    # Pull subtitles if we got them.
    subs_text = _read_subtitles(target_dir, info.get("id"))
    if subs_text:
        body_parts.append(subs_text)

    duration_sec = info.get("duration")

    return CaptureResult(
        kind=kind,
        platform=platform,
        title=title,
        author=author,
        body="\n\n".join(p.strip() for p in body_parts if p),
        media_path=media_path,
        duration_sec=float(duration_sec) if duration_sec else None,
        metadata={
            "source_url": url,
            "id": info.get("id"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "thumbnail": info.get("thumbnail"),
            "tags": info.get("tags"),
            "categories": info.get("categories"),
        },
    )


def _read_subtitles(target_dir: Path, video_id: str | None) -> str:
    if not video_id:
        return ""
    for path in target_dir.glob(f"{video_id}*.vtt"):
        try:
            return _vtt_to_plain(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return ""


def _vtt_to_plain(vtt: str) -> str:
    out: list[str] = []
    for line in vtt.splitlines():
        s = line.strip()
        if not s or s == "WEBVTT" or "-->" in s or s.startswith("NOTE"):
            continue
        if re.fullmatch(r"\d+", s):
            continue
        # Strip <c> tags
        s = re.sub(r"<[^>]+>", "", s)
        out.append(s)
    seen, dedup = set(), []
    for line in out:
        if line not in seen:
            seen.add(line)
            dedup.append(line)
    return " ".join(dedup)


def _first_line(text: str) -> str:
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            return line
    return ""
