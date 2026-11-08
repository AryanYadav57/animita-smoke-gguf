import json
import random
from pathlib import Path

HEADLINES = [
    "Ship faster with Nimbus",
    "Meet Orbit",
    "Build with Flux",
    "Scale with Atlas",
]

PRESETS = [
    "fade_in",
    "slide_up",
    "scale_in",
    "pop",
    "slide_left",
]

SYSTEM_PROMPT = "You are Animita. Output only valid Animita spec JSON."


def generate_example():
    headline = random.choice(HEADLINES)
    preset = random.choice(PRESETS)
    anim_name = preset.replace("_", " ")
    user_prompt = f'A dark hero scene where the headline "{headline}" uses a {anim_name} animation'

    spec = {
        "version": "0.1",
        "canvas": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "background": "#0B0D17",
        },
        "scenes": [
            {
                "id": "hero",
                "duration": 4.0,
                "elements": [
                    {
                        "id": "title",
                        "type": "text",
                        "content": headline,
                        "style": {
                            "size": 96,
                            "weight": 800,
                            "x": 160,
                            "y": 300,
                        },
                        "animations": [
                            {
                                "preset": preset,
                                "start": 0.2,
                                "duration": 0.8,
                                "easing": "ease_out_cubic",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    assistant_content = json.dumps(spec, separators=(",", ":"))

    message = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_content},
        ]
    }
    return message


def main():
    random.seed(1)

    repo_root = Path(__file__).resolve().parents[2]
    clean_dir = repo_root / "data" / "clean"
    clean_dir.mkdir(parents=True, exist_ok=True)

    train_path = clean_dir / "train.jsonl"
    val_path = clean_dir / "val.jsonl"

    with open(train_path, "w", encoding="utf-8") as f:
        for _ in range(50):
            example = generate_example()
            f.write(json.dumps(example, separators=(",", ":")) + "\n")

    with open(val_path, "w", encoding="utf-8") as f:
        for _ in range(10):
            example = generate_example()
            f.write(json.dumps(example, separators=(",", ":")) + "\n")

    print(f"Wrote 50 train examples to {train_path}")
    print(f"Wrote 10 validation examples to {val_path}")


if __name__ == "__main__":
    main()
