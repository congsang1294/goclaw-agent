#!/usr/bin/env python3
"""Deterministic workflow/state manager for Facebook organic and ads content."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import gen_caption
import gen_image


SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "output"
ADS_ANGLES = ("pain_point", "solution", "social_proof")


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def slugify(text: str, fallback: str) -> str:
    normalized = text.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-")[:48] or fallback


def new_run_dir(prefix: str, topic: str, output_dir: str | None) -> Path:
    if output_dir:
        path = Path(output_dir).expanduser()
        if not path.is_absolute():
            path = SKILL_DIR / path
    else:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        suffix = uuid.uuid4().hex[:6]
        path = OUTPUT_DIR / f"{prefix}-{slugify(topic, 'content')}-{stamp}-{suffix}"
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=False)
    return path


def resolve_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = SKILL_DIR / path
    return path.resolve()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_state(raw: str) -> tuple[Path, dict[str, Any]]:
    path = resolve_path(raw)
    if path.is_dir():
        path = path / "state.json"
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy state: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return path, payload


def brand_inputs(args: argparse.Namespace) -> tuple[Path | None, Path | None, str]:
    brain_db = gen_caption.resolve_brain_db(args.brain_db)
    context_dir = gen_caption.resolve_context_dir(args.context_dir, brain_db)
    context = gen_caption.build_brand_context(brain_db, context_dir)
    return brain_db, context_dir, context


def command_ideas(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = new_run_dir("organic", args.topic, args.output_dir)
    brain_db, context_dir, context = brand_inputs(args)
    ideas = gen_caption.call_openai(
        task="ideas",
        topic=args.topic,
        angle="",
        context=context,
        model=args.model,
    )
    state = {
        "version": 1,
        "mode": "organic",
        "status": "awaiting_choice",
        "topic": args.topic,
        "ideas": ideas["ideas"],
        "selected": None,
        "brain_db": str(brain_db) if brain_db else None,
        "context_dir": str(context_dir) if context_dir else None,
        "run_dir": str(run_dir),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    write_json(run_dir / "state.json", state)
    return {"ok": True, "state_path": str(run_dir / "state.json"), **state}


def command_organic(args: argparse.Namespace) -> dict[str, Any]:
    state_path, state = read_state(args.state)
    if state.get("mode") != "organic":
        raise ValueError("State không thuộc Mode 1 organic")
    ideas = state.get("ideas", [])
    selected = next(
        (idea for idea in ideas if int(idea.get("number", -1)) == args.choice),
        None,
    )
    if not selected:
        raise ValueError(f"Không tìm thấy ý tưởng số {args.choice} trong state")

    run_dir = state_path.parent
    original_topic = state.get("topic", "")
    concept = (
        f"Chủ đề gốc: {original_topic}. "
        f"Ý tưởng đã chọn: {selected['title']}. "
        f"Angle: {selected['angle']}"
    )
    brain_db, context_dir, context = brand_inputs(args)
    caption_payload = gen_caption.call_openai(
        task="organic",
        topic=concept,
        angle=selected["angle"],
        context=context,
        model=args.model,
    )

    caption_json = run_dir / "caption.json"
    caption_txt = run_dir / "caption.txt"
    image_path = run_dir / "organic-image.png"
    write_json(caption_json, {"ok": True, "task": "organic", "data": caption_payload})
    caption_txt.write_text(caption_payload["caption"], encoding="utf-8")
    image_result = gen_image.generate_image(
        caption_payload["image_prompt"],
        "organic",
        image_path,
    )

    preview_path = run_dir / "preview.md"
    preview_path.write_text(
        "# Preview bài Facebook\n\n"
        f"Ảnh: {image_path}\n\n"
        f"{caption_payload['caption']}\n",
        encoding="utf-8",
    )
    state.update({
        "status": "awaiting_approval",
        "selected": selected,
        "concept": concept,
        "caption_path": str(caption_txt),
        "caption_json": str(caption_json),
        "image_path": str(image_path),
        "preview_path": str(preview_path),
        "brain_db": str(brain_db) if brain_db else state.get("brain_db"),
        "context_dir": (
            str(context_dir) if context_dir else state.get("context_dir")
        ),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    write_json(state_path, state)
    return {
        "ok": True,
        "status": state["status"],
        "state_path": str(state_path),
        "selected": selected,
        "caption": caption_payload["caption"],
        "image": image_result,
        "preview_path": str(preview_path),
    }


def command_ads(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = new_run_dir("ads", args.topic, args.output_dir)
    state_path = run_dir / "state.json"
    brain_db, context_dir, context = brand_inputs(args)
    state: dict[str, Any] = {
        "version": 1,
        "mode": "ads",
        "status": "generating",
        "topic": args.topic,
        "sets": [],
        "run_dir": str(run_dir),
        "brain_db": str(brain_db) if brain_db else None,
        "context_dir": str(context_dir) if context_dir else None,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    write_json(state_path, state)

    try:
        for index, angle in enumerate(ADS_ANGLES, start=1):
            stem = f"{index:02d}-{angle.replace('_', '-')}"
            copy_payload = gen_caption.call_openai(
                task="ads",
                topic=args.topic,
                angle=angle,
                context=context,
                model=args.model,
            )
            copy_json = run_dir / f"{stem}-copy.json"
            copy_txt = run_dir / f"{stem}-copy.txt"
            image_path = run_dir / f"{stem}.png"
            write_json(copy_json, {"ok": True, "task": "ads", "data": copy_payload})
            copy_txt.write_text(copy_payload["caption"], encoding="utf-8")
            image_result = gen_image.generate_image(
                copy_payload["image_prompt"],
                "ads",
                image_path,
            )
            state["sets"].append({
                "number": index,
                "angle": angle,
                "copy_path": str(copy_txt),
                "copy_json": str(copy_json),
                "image_path": str(image_path),
                "caption": copy_payload["caption"],
                "image": image_result,
            })
            write_json(state_path, state)
    except Exception:
        state["status"] = "partial_failure"
        state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        write_json(state_path, state)
        raise

    if len(state["sets"]) != 3:
        raise RuntimeError("Mode 2 chưa tạo đủ 3 bộ creative")

    manifest_path = run_dir / "creative-sets.md"
    sections = ["# 3 bộ Creative Ads", ""]
    for item in state["sets"]:
        sections.extend([
            f"## Bộ {item['number']} — {item['angle']}",
            "",
            f"Ảnh: {item['image_path']}",
            "",
            item["caption"],
            "",
        ])
    manifest_path.write_text("\n".join(sections), encoding="utf-8")
    state.update({
        "status": "complete",
        "manifest_path": str(manifest_path),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    write_json(state_path, state)
    return {
        "ok": True,
        "status": "complete",
        "state_path": str(state_path),
        "manifest_path": str(manifest_path),
        "sets": state["sets"],
    }


def add_context_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--brain-db")
    parser.add_argument("--context-dir")
    parser.add_argument("--model", default="gpt-4.1-mini")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Điều phối Mode 1/Mode 2 và lưu state ghép cặp ảnh + văn bản."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ideas = subparsers.add_parser("ideas", help="Mode 1 bước A: tạo 3 ý tưởng.")
    ideas.add_argument("--topic", required=True)
    ideas.add_argument("--output-dir")
    add_context_args(ideas)

    organic = subparsers.add_parser(
        "organic", help="Mode 1 bước B: chọn ý và tạo ảnh + caption."
    )
    organic.add_argument("--state", required=True)
    organic.add_argument("--choice", required=True, type=int, choices=(1, 2, 3))
    add_context_args(organic)

    ads = subparsers.add_parser(
        "ads", help="Mode 2: tạo đủ 3 bộ pain/solution/social proof."
    )
    ads.add_argument("--topic", required=True)
    ads.add_argument("--output-dir")
    add_context_args(ads)
    return parser.parse_args()


def main() -> int:
    configure_console()
    gen_caption.load_environment()
    args = parse_args()
    try:
        if args.command == "ideas":
            result = command_ideas(args)
        elif args.command == "organic":
            result = command_organic(args)
        else:
            result = command_ads(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "command": args.command,
            "error": {"type": type(exc).__name__, "message": str(exc)[:500]},
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
