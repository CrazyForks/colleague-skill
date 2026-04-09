"""
share_life.py — /share-life orchestrator

Reads the current colleague's persona + meta, asks the model to generate
an image prompt that fits their personality, then fires async image generation.

Usage:
    python tools/share_life.py \
        --slug "example_tianyi" \
        --chat-id "123456789" \
        [--scene "傍晚下班路上"]   # optional override
"""

import argparse
import json
import os
import sys
from pathlib import Path

COLLEAGUES_DIR = Path(__file__).parent.parent / "colleagues"


def load_colleague(slug: str) -> dict:
    base = COLLEAGUES_DIR / slug
    if not base.exists():
        raise FileNotFoundError(f"Colleague '{slug}' not found in {COLLEAGUES_DIR}")

    meta = json.loads((base / "meta.json").read_text())
    persona = (base / "persona.md").read_text()
    work = (base / "work.md").read_text() if (base / "work.md").exists() else ""

    return {"meta": meta, "persona": persona, "work": work}


def build_image_prompt(colleague: dict, scene: str | None = None) -> str:
    """
    Generates a NanoBanana image prompt based on the colleague's persona.
    The prompt describes a slice-of-life moment that fits their personality.
    """
    meta = colleague["meta"]
    name = meta.get("name", "同事")
    role = meta.get("profile", {}).get("role", "")
    mbti = meta.get("profile", {}).get("mbti", "")
    tags = meta.get("tags", {}).get("personality", [])
    impression = meta.get("impression", "")

    # Extract vibe from persona for richer prompt
    persona_lines = [
        line.strip("- ").strip()
        for line in colleague["persona"].split("\n")
        if line.strip().startswith("-") and len(line) < 100
    ][:5]
    persona_summary = "；".join(persona_lines) if persona_lines else ""

    # Scene: auto-generate a fitting moment if not provided
    if not scene:
        scene = _pick_scene(tags, mbti, role)

    prompt = (
        f"A slice-of-life illustration of {name}, a {role}. "
        f"Scene: {scene}. "
        f"Personality: {', '.join(tags)}. "
        f"Vibe: {impression}. "
        f"Style: warm, cinematic, anime-influenced, soft lighting, "
        f"detailed environment, character in natural relaxed pose. "
        f"No text overlays."
    )

    return prompt


def _pick_scene(tags: list, mbti: str, role: str) -> str:
    """Pick a scene that fits the personality tags."""
    tag_set = {t.lower() for t in tags}

    scenes = []

    if any(t in tag_set for t in ["游戏", "游戏爱好者"]):
        scenes.append("playing a single-player game late at night, soft monitor glow")
    if any(t in tag_set for t in ["健谈", "热心"]):
        scenes.append("chatting over coffee with a colleague, animated discussion")
    if any(t in tag_set for t in ["代码", "技术", "靠谱"]):
        scenes.append("focused at a desk with code on screen, coffee mug nearby, golden hour light")
    if any(t in tag_set for t in ["温柔", "细腻"]):
        scenes.append("reading a book by a window on a rainy afternoon")
    if any(t in tag_set for t in ["直接", "严谨"]):
        scenes.append("presenting at a whiteboard, clear diagrams, confident posture")

    # Fallback scenes
    if not scenes:
        scenes = [
            "afternoon commute, earphones in, watching the city through a train window",
            "lunch break in a quiet corner, lost in thought",
            "evening walk in the neighborhood, streetlights just turning on",
        ]

    import random
    return random.choice(scenes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True, help="Colleague slug, e.g. example_tianyi")
    parser.add_argument("--chat-id", required=True, help="Telegram chat_id to send image to")
    parser.add_argument("--scene", default=None, help="Optional scene override")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt only, don't generate")
    args = parser.parse_args()

    # Load colleague data
    try:
        colleague = load_colleague(args.slug)
    except FileNotFoundError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    # Build image prompt
    prompt = build_image_prompt(colleague, scene=args.scene)

    if args.dry_run:
        print(json.dumps({"prompt": prompt}, ensure_ascii=False, indent=2))
        return

    # Fire async generation
    # Import here so dry-run works without image_generator deps
    sys.path.insert(0, str(Path(__file__).parent))
    from image_generator import cmd_generate

    result = cmd_generate(
        prompt=prompt,
        slug=args.slug,
        chat_id=args.chat_id,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
