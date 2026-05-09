from pathlib import Path
import json
import shutil
import pandas as pd

SOURCES = [
    Path("/home/hassaan/robotics/isaac_tuts/datasets/banana_pick_clean_v2"),
    Path("/home/hassaan/robotics/isaac_tuts/datasets/banana_pick_dr"),
    Path("/home/hassaan/Downloads/banana_pick_real_v1"),
]

OUT = Path("/home/hassaan/robotics/isaac_tuts/datasets/banana_pick_all_merged")
TASK_TEXT = "Pick up the banana and place it in the cup"


def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r") as f:
        return json.load(f)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def copy_base_meta(base: Path, out: Path):
    src_meta = base / "meta"
    dst_meta = out / "meta"
    dst_meta.mkdir(parents=True, exist_ok=True)

    for item in src_meta.iterdir():
        if item.is_file():
            if item.name in {"episodes.jsonl", "episodes_stats.jsonl", "tasks.jsonl"}:
                continue
            shutil.copy2(item, dst_meta / item.name)


def find_matching_videos(src_root: Path, old_episode_name: str):
    videos_root = src_root / "videos"
    if not videos_root.exists():
        return []

    matches = []
    for vid in videos_root.rglob("*.mp4"):
        if vid.stem == old_episode_name:
            matches.append(vid)

    return sorted(matches)


def camera_subpath_from_video(src_root: Path, vid: Path):
    """
    Handles common LeRobot layouts like:

    videos/chunk-000/observation.images.front/episode_000000.mp4
    videos/observation.images.front/chunk-000/episode_000000.mp4
    videos/observation.images.front/episode_000000.mp4
    """
    rel = vid.relative_to(src_root / "videos")
    parts = list(rel.parts[:-1])

    # Drop any chunk-* folder from the camera path.
    parts = [p for p in parts if not p.startswith("chunk-")]

    if not parts:
        return Path("observation.images.front")

    return Path(*parts)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)

    (OUT / "data" / "chunk-000").mkdir(parents=True, exist_ok=True)
    (OUT / "videos" / "chunk-000").mkdir(parents=True, exist_ok=True)
    (OUT / "meta").mkdir(parents=True, exist_ok=True)

    copy_base_meta(SOURCES[0], OUT)

    episode_idx = 0
    global_frame_idx = 0
    total_videos = 0
    episodes = []

    for src_root in SOURCES:
        if not src_root.exists():
            raise FileNotFoundError(f"Missing dataset: {src_root}")

        data_files = sorted((src_root / "data").rglob("*.parquet"))
        print(f"\nSource: {src_root}")
        print(f"Found parquet episodes: {len(data_files)}")

        for data_file in data_files:
            old_episode_name = data_file.stem
            new_episode_name = f"episode_{episode_idx:06d}"

            df = pd.read_parquet(data_file)
            num_frames = len(df)

            if "episode_index" in df.columns:
                df["episode_index"] = episode_idx

            if "task_index" in df.columns:
                df["task_index"] = 0

            if "index" in df.columns:
                df["index"] = range(global_frame_idx, global_frame_idx + num_frames)

            out_parquet = OUT / "data" / "chunk-000" / f"{new_episode_name}.parquet"
            df.to_parquet(out_parquet, index=False)

            videos = find_matching_videos(src_root, old_episode_name)
            if len(videos) == 0:
                print(f"[WARN] No videos found for {old_episode_name}")

            for vid in videos:
                cam_subpath = camera_subpath_from_video(src_root, vid)
                dst_dir = OUT / "videos" / "chunk-000" / cam_subpath
                dst_dir.mkdir(parents=True, exist_ok=True)

                dst = dst_dir / f"{new_episode_name}.mp4"
                shutil.copy2(vid, dst)
                total_videos += 1

            episodes.append({
                "episode_index": episode_idx,
                "tasks": [TASK_TEXT],
                "length": num_frames,
            })

            print(f"Mapped {old_episode_name} -> {new_episode_name}, frames={num_frames}, videos={len(videos)}")

            episode_idx += 1
            global_frame_idx += num_frames

    with open(OUT / "meta" / "episodes.jsonl", "w") as f:
        for ep in episodes:
            f.write(json.dumps(ep) + "\n")

    with open(OUT / "meta" / "tasks.jsonl", "w") as f:
        f.write(json.dumps({"task_index": 0, "task": TASK_TEXT}) + "\n")

    info_path = OUT / "meta" / "info.json"
    info = load_json(info_path, {})

    info["total_episodes"] = episode_idx
    info["total_frames"] = global_frame_idx
    info["total_tasks"] = 1
    info["total_videos"] = total_videos
    info["total_chunks"] = 1
    info["chunks_size"] = max(info.get("chunks_size", 1000), episode_idx)

    # Common LeRobot path templates.
    info["data_path"] = "data/chunk-{episode_chunk:03d}/episode_{episode_index:06d}.parquet"
    if total_videos > 0:
        info["video_path"] = "videos/chunk-{episode_chunk:03d}/{video_key}/episode_{episode_index:06d}.mp4"

    write_json(info_path, info)

    print("\nDONE")
    print(f"Merged dataset: {OUT}")
    print(f"Episodes: {episode_idx}")
    print(f"Frames: {global_frame_idx}")
    print(f"Videos copied: {total_videos}")
    print("\nCheck with:")
    print(f"find {OUT} -maxdepth 4 -type f | head -80")
    print(f"find {OUT}/data -name '*.parquet' | wc -l")
    print(f"find {OUT}/videos -name '*.mp4' | wc -l")


if __name__ == "__main__":
    main()
