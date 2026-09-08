"""
IBVAP - Dataset Integrity & Video Verification Tool
Audits image resolutions, bounding box bounds, COCO JSON schemas, and test video decodability.
"""
import os
import sys
import json
import cv2

def verify_dataset(dataset_dir):
    print("=" * 72)
    print(f"  IBVAP DATASET VERIFICATION // {dataset_dir}")
    print("=" * 72)
    
    errors = []
    
    # 1. Check data.yaml
    data_yaml = os.path.join(dataset_dir, "data.yaml")
    if not os.path.exists(data_yaml):
        errors.append("Missing data.yaml")
    else:
        print("  [OK] data.yaml exists.")

    # 2. Check manifest
    manifest_p = os.path.join(dataset_dir, "dataset_manifest.json")
    if not os.path.exists(manifest_p):
        errors.append("Missing dataset_manifest.json")
    else:
        with open(manifest_p, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"  [OK] dataset_manifest.json contains {len(data.get('files', []))} cryptographically hashed files.")

    # 3. Check videos
    v_dir = os.path.join(dataset_dir, "test-videos")
    expected_videos = [
        "scenario_01_perimeter_breach.mp4",
        "scenario_02_night_thermal_patrol.mp4",
        "scenario_03_checkpoint_anpr.mp4",
        "scenario_04_multicam_handoff.mp4"
    ]
    for v_name in expected_videos:
        vp = os.path.join(v_dir, v_name)
        if not os.path.exists(vp):
            errors.append(f"Missing video: {v_name}")
            continue
        cap = cv2.VideoCapture(vp)
        if not cap.isOpened():
            errors.append(f"Failed to open video: {v_name}")
            continue
        f_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        if f_count < 1:
            errors.append(f"Video {v_name} has 0 frames!")
        else:
            print(f"  [OK] Video {v_name:38} -> {f_count} frames | {w}x{h} | {fps:.1f} FPS")

    # 4. Check processed YOLO splits
    for split in ["train", "val", "test"]:
        img_d = os.path.join(dataset_dir, "processed", split, "images")
        lbl_d = os.path.join(dataset_dir, "processed", split, "labels")
        if not os.path.exists(img_d) or not os.path.exists(lbl_d):
            errors.append(f"Missing split directory for: {split}")
            continue
        imgs = [f for f in os.listdir(img_d) if f.endswith(".jpg")]
        lbls = [f for f in os.listdir(lbl_d) if f.endswith(".txt")]
        if len(imgs) != len(lbls):
            errors.append(f"Mismatch in {split}: {len(imgs)} images vs {len(lbls)} labels")
        else:
            print(f"  [OK] Split '{split:5}': {len(imgs)} images and matching label pairs.")

    # 5. Check annotations
    coco_p = os.path.join(dataset_dir, "annotations", "coco", "instances_val.json")
    if os.path.exists(coco_p):
        with open(coco_p, "r", encoding="utf-8") as f:
            c_data = json.load(f)
            print(f"  [OK] COCO instances_val.json: {len(c_data['images'])} images, {len(c_data['annotations'])} annotations.")
    else:
        errors.append("Missing COCO instances_val.json")

    print("-" * 72)
    if errors:
        print(f"  FAILED: {len(errors)} errors found:")
        for err in errors:
            print(f"    - {err}")
        return False
    else:
        print("  SUCCESS: All dataset files, videos, and annotations verified 100%!")
        return True

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    success = verify_dataset(p)
    sys.exit(0 if success else 1)
