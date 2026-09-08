"""
IBVAP - Dedicated Datasets Subsystem Test Suite
Validates dataset directories, manifest signatures, YOLO splits, annotations, and MP4 video decodability.
"""
import os
import json
import pytest
import cv2
import yaml

DATASET_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets"))

def test_dataset_structure_and_manifest():
    assert os.path.isdir(DATASET_ROOT), f"Dataset directory missing at {DATASET_ROOT}"
    
    # 1. Key top-level files
    assert os.path.exists(os.path.join(DATASET_ROOT, "README.md"))
    assert os.path.exists(os.path.join(DATASET_ROOT, "data.yaml"))
    assert os.path.exists(os.path.join(DATASET_ROOT, "dataset_manifest.json"))
    
    # 2. Manifest integrity
    with open(os.path.join(DATASET_ROOT, "dataset_manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)
        assert len(manifest.get("files", [])) >= 30
        for entry in manifest["files"]:
            assert "path" in entry
            assert "sha256" in entry
            assert len(entry["sha256"]) == 64

def test_data_yaml_descriptor():
    yaml_path = os.path.join(DATASET_ROOT, "data.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        assert "train" in config
        assert "val" in config
        assert "test" in config
        assert "names" in config
        assert len(config["names"]) == 6
        assert config["names"][0] == "person"
        assert config["names"][1] == "vehicle"
        assert config["names"][2] == "license_plate"

def test_tactical_test_videos_playable():
    video_dir = os.path.join(DATASET_ROOT, "test-videos")
    expected_videos = [
        "scenario_01_perimeter_breach.mp4",
        "scenario_02_night_thermal_patrol.mp4",
        "scenario_03_checkpoint_anpr.mp4",
        "scenario_04_multicam_handoff.mp4"
    ]
    for v_name in expected_videos:
        vp = os.path.join(video_dir, v_name)
        assert os.path.exists(vp), f"Missing video: {v_name}"
        assert os.path.getsize(vp) > 10000, f"Video {v_name} is too small"
        
        cap = cv2.VideoCapture(vp)
        assert cap.isOpened(), f"OpenCV failed to decode {v_name}"
        f_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        assert f_count >= 50, f"Expected >= 50 frames in {v_name}, got {f_count}"
        assert w == 1280
        assert h == 720
        assert fps == 25.0

def test_processed_yolo_splits_and_normalization():
    splits = ["train", "val", "test"]
    for s in splits:
        img_dir = os.path.join(DATASET_ROOT, "processed", s, "images")
        lbl_dir = os.path.join(DATASET_ROOT, "processed", s, "labels")
        assert os.path.isdir(img_dir)
        assert os.path.isdir(lbl_dir)
        
        imgs = [f for f in os.listdir(img_dir) if f.endswith(".jpg")]
        lbls = [f for f in os.listdir(lbl_dir) if f.endswith(".txt")]
        assert len(imgs) >= 4
        assert len(imgs) == len(lbls)
        
        # Verify bounding box values are within [0.0, 1.0]
        for lf_name in lbls:
            with open(os.path.join(lbl_dir, lf_name), "r", encoding="utf-8") as lf:
                for line in lf:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    assert len(parts) == 5
                    cls_id = int(parts[0])
                    cx, cy, bw, bh = map(float, parts[1:])
                    assert 0 <= cls_id <= 5
                    assert 0.0 <= cx <= 1.0
                    assert 0.0 <= cy <= 1.0
                    assert 0.0 < bw <= 1.0
                    assert 0.0 < bh <= 1.0

def test_multi_format_annotations():
    # 1. COCO
    coco_p = os.path.join(DATASET_ROOT, "annotations", "coco", "instances_val.json")
    assert os.path.exists(coco_p)
    with open(coco_p, "r", encoding="utf-8") as f:
        coco = json.load(f)
        assert len(coco["images"]) >= 8
        assert len(coco["annotations"]) >= 8
        assert len(coco["categories"]) == 6

    # 2. MOT
    mot_p = os.path.join(DATASET_ROOT, "annotations", "mot", "gt.txt")
    assert os.path.exists(mot_p)
    with open(mot_p, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
        assert len(lines) >= 8

    # 3. ANPR
    anpr_p = os.path.join(DATASET_ROOT, "annotations", "anpr", "plates_gt.json")
    assert os.path.exists(anpr_p)
    with open(anpr_p, "r", encoding="utf-8") as f:
        plates = json.load(f)
        assert len(plates) >= 6
        for p in plates:
            assert "plate_number" in p
            assert "state_jurisdiction" in p
            assert "is_hotlisted" in p
