#!/usr/bin/env python3
"""Execute full refinement of annotations for dataset/labels/train/*.txt"""

import shutil
from pathlib import Path

train_lbl_dir = Path("dataset/labels/train")
backup_dir = Path("dataset/labels/train_backup")

# 1. Ensure backup
if not backup_dir.exists():
    backup_dir.mkdir(parents=True, exist_ok=True)
    for f in train_lbl_dir.glob("*.txt"):
        shutil.copy(f, backup_dir / f.name)
    print("Backup completed.")

def clamp(v, min_v=0.0, max_v=1.0):
    return max(min_v, min(max_v, v))

def sanitize_box(cls_id, xc, yc, w, h):
    x1 = clamp(xc - w / 2)
    y1 = clamp(yc - h / 2)
    x2 = clamp(xc + w / 2)
    y2 = clamp(yc + h / 2)
    new_w = max(0.001, x2 - x1)
    new_h = max(0.001, y2 - y1)
    new_xc = (x1 + x2) / 2
    new_yc = (y1 + y2) / 2
    return int(cls_id), new_xc, new_yc, new_w, new_h

def box_iou(b1, b2):
    x1 = max(b1[1] - b1[3]/2, b2[1] - b2[3]/2)
    y1 = max(b1[2] - b1[4]/2, b2[2] - b2[4]/2)
    x2 = min(b1[1] + b1[3]/2, b2[1] + b2[3]/2)
    y2 = min(b1[2] + b1[4]/2, b2[2] + b2[4]/2)
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    union = b1[3]*b1[4] + b2[3]*b2[4] - inter
    return inter / union if union > 0 else 0

def deduplicate_boxes(boxes, threshold=0.70):
    # Keep highest priority class or first box
    kept = []
    for b in boxes:
        is_dup = False
        for k in kept:
            if box_iou(b, k) > threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(b)
    return kept

def process_file(file_path):
    stem = file_path.stem
    # Always read from pristine backup to prevent re-modifications!
    backup_file = backup_dir / file_path.name
    lines = backup_file.read_text().splitlines()
    boxes = []
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        cls_id = int(parts[0])
        xc, yc, w, h = map(float, parts[1:])
        boxes.append([cls_id, xc, yc, w, h])

    new_boxes = []

    # Custom per-file rules:
    if stem == "drive_001":
        for b in boxes:
            # line 12 duplicate taxi van -> skip
            if b[0] == 3 and abs(b[1] - 0.933) < 0.02 and abs(b[2] - 0.334) < 0.02:
                continue
            # line 11 white SUV van -> car
            if b[0] == 3 and abs(b[1] - 0.409) < 0.02:
                b[0] = 0
            new_boxes.append(b)
        # Add missing
        new_boxes.append([0, 0.975, 0.207, 0.030, 0.038])
        new_boxes.append([0, 0.518, 0.300, 0.040, 0.042])

    elif stem == "drive_002":
        for b in boxes:
            # coach bus & transit bus
            if b[0] == 3 and (abs(b[1] - 0.369) < 0.03 or abs(b[1] - 0.316) < 0.03):
                b[0] = 2
            # silver microvan on right
            if b[0] == 0 and b[1] > 0.90 and b[2] > 0.50:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.append([3, 0.180, 0.360, 0.075, 0.110])

    elif stem == "drive_003":
        for b in boxes:
            # buses
            if b[0] == 3 and (abs(b[1] - 0.970) < 0.03 or abs(b[1] - 0.142) < 0.03):
                b[0] = 2
            # pickup
            if b[0] == 3 and abs(b[1] - 0.976) < 0.02 and abs(b[2] - 0.323) < 0.03:
                b[0] = 0
            new_boxes.append(b)

    elif stem == "drive_004":
        for b in boxes:
            # ghost box
            if b[1] > 0.95 and b[2] > 0.65 and b[3] < 0.05:
                continue
            # Jinbei van
            if b[0] == 0 and abs(b[1] - 0.43) < 0.05 and abs(b[2] - 0.05) < 0.04:
                b[0] = 3
            # minivan
            if b[0] == 0 and abs(b[1] - 0.69) < 0.05 and abs(b[2] - 0.09) < 0.04:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_005":
        for b in boxes:
            # tow truck
            if b[0] == 3 and abs(b[1] - 0.666) < 0.03:
                b[0] = 1
            # double decker bus
            if b[0] == 3 and abs(b[1] - 0.708) < 0.03:
                b[0] = 2
            # microvan
            if b[0] == 0 and abs(b[1] - 0.302) < 0.04 and abs(b[2] - 0.190) < 0.04:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_006":
        for b in boxes:
            # ghost box
            if b[0] == 0 and abs(b[1] - 0.823) < 0.03 and abs(b[2] - 0.709) < 0.03:
                continue
            # tow truck
            if b[0] == 3 and abs(b[1] - 0.668) < 0.03:
                b[0] = 1
            # green microvan
            if b[0] == 0 and abs(b[1] - 0.869) < 0.04 and abs(b[2] - 0.627) < 0.04:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_007":
        for b in boxes:
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.320, 0.185, 0.032, 0.050],
            [0, 0.332, 0.165, 0.030, 0.045],
            [0, 0.345, 0.150, 0.028, 0.042],
            [0, 0.355, 0.138, 0.026, 0.038],
            [0, 0.365, 0.126, 0.025, 0.035],
            [0, 0.740, 0.100, 0.035, 0.055],
            [0, 0.795, 0.138, 0.040, 0.055],
            [0, 0.822, 0.115, 0.035, 0.050],
        ])

    elif stem == "drive_008":
        for b in boxes:
            # bus on left
            if b[0] == 3 and abs(b[1] - 0.145) < 0.03:
                b[0] = 2
            # ghost box
            if b[1] > 0.95 and abs(b[2] - 0.477) < 0.05:
                continue
            # microvans
            if b[0] == 0 and abs(b[1] - 0.491) < 0.04 and abs(b[2] - 0.470) < 0.04:
                b[0] = 3
            if b[0] == 0 and abs(b[1] - 0.272) < 0.04 and abs(b[2] - 0.235) < 0.04:
                b[0] = 3
            if b[0] == 0 and abs(b[1] - 0.290) < 0.04 and abs(b[2] - 0.177) < 0.04:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_009":
        for b in boxes:
            # buses labeled van
            if b[0] == 3:
                b[0] = 2
            new_boxes.append(b)
        new_boxes.extend([
            [3, 0.585, 0.038, 0.062, 0.052],
            [3, 0.745, 0.033, 0.082, 0.055],
            [0, 0.485, 0.078, 0.065, 0.050],
            [0, 0.412, 0.055, 0.050, 0.045],
            [0, 0.860, 0.045, 0.085, 0.050],
            [0, 0.940, 0.105, 0.095, 0.060],
        ])

    elif stem == "drive_010":
        for b in boxes:
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.895, 0.245, 0.045, 0.040],
            [0, 0.940, 0.255, 0.050, 0.040],
        ])

    elif stem == "drive_011":
        for b in boxes:
            # bus
            if b[0] == 3 and abs(b[1] - 0.365) < 0.03:
                b[0] = 2
            # tow truck
            if b[0] == 3 and abs(b[1] - 0.977) < 0.03:
                b[0] = 1
            # microvan
            if b[0] == 0 and abs(b[1] - 0.303) < 0.03 and abs(b[2] - 0.342) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_012":
        for b in boxes:
            # all 6 buses labeled van -> bus
            if b[0] == 3:
                b[0] = 2
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.428, 0.282, 0.065, 0.060],
            [0, 0.558, 0.388, 0.075, 0.095],
            [0, 0.738, 0.332, 0.055, 0.075],
            [0, 0.850, 0.235, 0.045, 0.055],
        ])

    elif stem == "drive_013":
        for b in boxes:
            # ghost boxes
            if b[1] > 0.85 and b[2] > 0.85: continue
            if b[1] > 0.60 and b[1] < 0.75 and b[2] > 0.65 and b[3] < 0.15: continue
            new_boxes.append(b)

    elif stem == "drive_014":
        for b in boxes:
            # double decker & tour coach
            if b[0] == 3 and (abs(b[1] - 0.352) < 0.03 or abs(b[1] - 0.971) < 0.03):
                b[0] = 2
            # white microvan
            if b[0] == 0 and abs(b[1] - 0.195) < 0.04 and abs(b[2] - 0.130) < 0.04:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.420, 0.060, 0.035, 0.045],
            [0, 0.450, 0.060, 0.035, 0.045],
        ])

    elif stem == "drive_015":
        for b in boxes:
            # articulated bus
            if b[0] == 3 and abs(b[1] - 0.243) < 0.03:
                b[0] = 2
            # flatbed truck
            if b[0] == 3 and abs(b[1] - 0.745) < 0.03:
                b[0] = 1
            new_boxes.append(b)

    elif stem == "drive_016":
        for b in boxes:
            # microvan
            if b[0] == 0 and abs(b[1] - 0.177) < 0.03 and abs(b[2] - 0.207) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_018":
        for b in boxes:
            new_boxes.append(b)

    elif stem == "drive_019":
        for b in boxes:
            # buses labeled van
            if b[0] == 3 and b[1] > 0.75:
                b[0] = 2
            if b[0] == 3 and abs(b[1] - 0.256) < 0.03:
                b[0] = 2
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.385, 0.165, 0.070, 0.065],
            [0, 0.465, 0.278, 0.082, 0.082],
            [0, 0.238, 0.195, 0.095, 0.085],
        ])

    elif stem == "drive_020":
        for b in boxes:
            # microvan
            if b[0] == 0 and abs(b[1] - 0.254) < 0.03 and abs(b[2] - 0.418) < 0.03:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.305, 0.215, 0.075, 0.065],
            [0, 0.448, 0.085, 0.045, 0.055],
            [0, 0.495, 0.085, 0.045, 0.055],
            [3, 0.980, 0.055, 0.040, 0.055],
        ])

    elif stem == "drive_021":
        for b in boxes:
            # transit buses
            if b[0] == 3 and b[1] > 0.70:
                b[0] = 2
            # silver minivan in foreground
            if b[0] == 1 and abs(b[1] - 0.166) < 0.05:
                b[0] = 3
            # microvan
            if b[0] == 0 and abs(b[1] - 0.868) < 0.03 and abs(b[2] - 0.517) < 0.03:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.130, 0.550, 0.085, 0.110],
            [0, 0.240, 0.480, 0.085, 0.095],
            [0, 0.640, 0.430, 0.050, 0.060],
        ])

    elif stem == "drive_022":
        for b in boxes:
            # box truck
            if b[0] == 3 and abs(b[1] - 0.942) < 0.03:
                b[0] = 1
            # minivan
            if b[0] == 0 and abs(b[1] - 0.518) < 0.03 and abs(b[2] - 0.528) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_024":
        for b in boxes:
            # buses
            if b[0] == 3 and (abs(b[1] - 0.438) < 0.03 or abs(b[1] - 0.133) < 0.03):
                b[0] = 2
            # microvan
            if b[0] == 0 and abs(b[1] - 0.390) < 0.03 and abs(b[2] - 0.367) < 0.03:
                b[0] = 3
            # dark blue MPV
            if b[0] == 0 and abs(b[1] - 0.836) < 0.03 and abs(b[2] - 0.411) < 0.03:
                b[0] = 3
            # silver microvan
            if abs(b[1] - 0.783) < 0.03 and abs(b[2] - 0.492) < 0.03:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.extend([
            [3, 0.738, 0.032, 0.082, 0.058],
            [0, 0.855, 0.042, 0.082, 0.055],
            [0, 0.935, 0.095, 0.090, 0.065],
        ])

    elif stem == "drive_025":
        for b in boxes:
            # white transit bus
            if b[0] == 3 and abs(b[1] - 0.168) < 0.03:
                b[0] = 2
            # silver microvan
            if b[0] == 0 and abs(b[1] - 0.326) < 0.03 and abs(b[2] - 0.320) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_026":
        for b in boxes:
            # transit buses in bus lane
            if b[0] == 3 and b[1] < 0.50:
                b[0] = 2
            # utility truck on right
            if b[0] == 3 and abs(b[1] - 0.933) < 0.03:
                b[0] = 1
            new_boxes.append(b)
        new_boxes.extend([
            [2, 0.205, 0.440, 0.095, 0.180],
            [2, 0.265, 0.355, 0.085, 0.145],
        ])

    elif stem == "drive_027":
        for b in boxes:
            # buses
            if b[0] == 3 and (abs(b[1] - 0.436) < 0.03 or abs(b[1] - 0.139) < 0.03):
                b[0] = 2
            # microvan
            if b[0] == 0 and abs(b[1] - 0.388) < 0.03 and abs(b[2] - 0.363) < 0.03:
                b[0] = 3
            # dark blue MPV
            if b[0] == 0 and abs(b[1] - 0.833) < 0.03 and abs(b[2] - 0.407) < 0.03:
                b[0] = 3
            # silver microvan
            if abs(b[1] - 0.781) < 0.03 and abs(b[2] - 0.490) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_028":
        for b in boxes:
            new_boxes.append(b)

    elif stem == "drive_029":
        for b in boxes:
            # buses labeled van
            if b[0] == 3:
                b[0] = 2
            new_boxes.append(b)
        new_boxes.extend([
            [2, 0.035, 0.170, 0.055, 0.065],
            [0, 0.518, 0.215, 0.055, 0.040],
            [0, 0.555, 0.225, 0.055, 0.042],
        ])

    elif stem == "drive_030":
        for b in boxes:
            # blue coach bus
            if b[0] == 3 and abs(b[1] - 0.401) < 0.03:
                b[0] = 2
            # Buick GL8 minivan
            if abs(b[1] - 0.826) < 0.03 and abs(b[2] - 0.679) < 0.03:
                b[0] = 3
            # blue Jinbei van
            if b[0] == 0 and abs(b[1] - 0.836) < 0.03 and abs(b[2] - 0.505) < 0.03:
                b[0] = 3
            # silver minivan
            if b[0] == 0 and abs(b[1] - 0.914) < 0.03 and abs(b[2] - 0.290) < 0.03:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.extend([
            [2, 0.158, 0.150, 0.055, 0.085],
            [2, 0.110, 0.140, 0.045, 0.075],
        ])

    elif stem == "drive_031":
        for b in boxes:
            # Forester SUV
            if b[0] == 3 and abs(b[1] - 0.285) < 0.03:
                b[0] = 0
            # coach bus
            if b[0] == 3 and abs(b[1] - 0.467) < 0.03:
                b[0] = 2
            # Jinbei van
            if abs(b[1] - 0.844) < 0.04 and abs(b[2] - 0.593) < 0.04:
                b[0] = 3
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.378, 0.405, 0.070, 0.115],
            [0, 0.505, 0.325, 0.065, 0.090],
            [0, 0.412, 0.295, 0.055, 0.080],
            [0, 0.315, 0.335, 0.065, 0.085],
            [0, 0.218, 0.280, 0.060, 0.075],
            [0, 0.055, 0.330, 0.065, 0.080],
        ])

    elif stem == "drive_033":
        for b in boxes:
            # transit bus entering right
            if abs(b[1] - 0.971) < 0.03 and abs(b[2] - 0.574) < 0.03:
                b[0] = 2
            new_boxes.append(b)

    elif stem == "drive_035":
        for b in boxes:
            # transit buses
            if b[0] == 3:
                b[0] = 2
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.130, 0.550, 0.085, 0.110],
            [0, 0.240, 0.480, 0.085, 0.095],
            [0, 0.640, 0.430, 0.050, 0.060],
        ])

    elif stem == "drive_036":
        for b in boxes:
            new_boxes.append(b)
        new_boxes.append([2, 0.050, 0.070, 0.045, 0.065])

    elif stem == "drive_038":
        for b in boxes:
            # buses labeled van
            if b[0] == 3 and (abs(b[1] - 0.126) < 0.03 or abs(b[1] - 0.035) < 0.03 or abs(b[1] - 0.943) < 0.03):
                b[0] = 2
            # dark blue MPV
            if b[0] == 0 and abs(b[1] - 0.042) < 0.03 and abs(b[2] - 0.352) < 0.03:
                b[0] = 3
            # white microvan
            if b[0] == 0 and abs(b[1] - 0.214) < 0.03 and abs(b[2] - 0.099) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_039":
        for b in boxes:
            # ghost box
            if b[1] > 0.95 and abs(b[2] - 0.498) < 0.03:
                continue
            # dump truck
            if b[0] == 3 and abs(b[1] - 0.682) < 0.03:
                b[0] = 1
            # buses
            if b[0] == 3:
                b[0] = 2
            new_boxes.append(b)

    elif stem == "drive_040":
        for b in boxes:
            # buses
            if b[0] == 3 and (abs(b[1] - 0.115) < 0.03 or abs(b[1] - 0.570) < 0.03):
                b[0] = 2
            # microvans
            if b[0] == 0 and abs(b[1] - 0.469) < 0.04 and abs(b[2] - 0.443) < 0.04:
                b[0] = 3
            if b[0] == 0 and abs(b[1] - 0.252) < 0.04 and abs(b[2] - 0.225) < 0.04:
                b[0] = 3
            if b[0] == 0 and abs(b[1] - 0.266) < 0.04 and abs(b[2] - 0.166) < 0.04:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_041":
        for b in boxes:
            # double decker bus
            if b[0] == 3 and abs(b[1] - 0.199) < 0.03:
                b[0] = 2
            # tow truck
            if abs(b[1] - 0.666) < 0.03 and abs(b[2] - 0.272) < 0.03:
                b[0] = 1
            # microvans
            if b[0] == 0 and abs(b[1] - 0.511) < 0.03 and abs(b[2] - 0.196) < 0.03:
                b[0] = 3
            if b[0] == 0 and abs(b[1] - 0.572) < 0.03 and abs(b[2] - 0.199) < 0.03:
                b[0] = 3
            if b[0] == 0 and abs(b[1] - 0.399) < 0.03 and abs(b[2] - 0.160) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_042":
        for b in boxes:
            # distance bus
            if b[0] == 3 and abs(b[1] - 0.222) < 0.03:
                b[0] = 2
            # foreground bus
            if abs(b[1] - 0.454) < 0.04 and abs(b[2] - 0.825) < 0.04:
                b[0] = 2
            new_boxes.append(b)

    elif stem == "drive_043":
        for b in boxes:
            # white SUV labeled truck
            if b[0] == 1 and abs(b[1] - 0.652) < 0.04:
                b[0] = 0
            new_boxes.append(b)

    elif stem == "drive_044":
        for b in boxes:
            # ghost box
            if b[1] < 0.05 and b[2] < 0.10:
                continue
            # coach bus & transit bus
            if b[0] == 3 and (abs(b[1] - 0.750) < 0.03 or abs(b[1] - 0.971) < 0.03):
                b[0] = 2
            # microvan
            if b[0] == 0 and abs(b[1] - 0.470) < 0.03 and abs(b[2] - 0.638) < 0.03:
                b[0] = 3
            # Jinbei van
            if b[0] == 0 and abs(b[1] - 0.734) < 0.03 and abs(b[2] - 0.426) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_046":
        for b in boxes:
            new_boxes.append(b)
        new_boxes.append([0, 0.220, 0.060, 0.035, 0.045])

    elif stem == "drive_047":
        for b in boxes:
            # box truck
            if b[0] == 3 and abs(b[1] - 0.734) < 0.03:
                b[0] = 1
            # minivan
            if b[0] == 0 and abs(b[1] - 0.054) < 0.03 and abs(b[2] - 0.602) < 0.03:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_048":
        for b in boxes:
            # 4 buses labeled van
            if b[0] == 3:
                b[0] = 2
            new_boxes.append(b)
        new_boxes.extend([
            [0, 0.525, 0.205, 0.055, 0.040],
            [0, 0.548, 0.210, 0.055, 0.042],
        ])

    elif stem == "drive_049":
        for b in boxes:
            # approaching bus
            if b[0] == 3 and abs(b[1] - 0.535) < 0.03:
                b[0] = 2
            # bus shelter false positive
            if b[0] == 1 and abs(b[1] - 0.193) < 0.05 and abs(b[2] - 0.663) < 0.05:
                continue
            # microvan
            if b[0] == 0 and abs(b[1] - 0.361) < 0.04 and abs(b[2] - 0.207) < 0.04:
                b[0] = 3
            new_boxes.append(b)

    elif stem == "drive_050":
        for b in boxes:
            new_boxes.append(b)
        new_boxes.extend([
            [3, 0.530, 0.555, 0.060, 0.105],
            [0, 0.662, 0.590, 0.070, 0.115],
        ])

    else:
        new_boxes = boxes

    # Sanitize and deduplicate
    sanitized = [sanitize_box(*b) for b in new_boxes]
    deduped = deduplicate_boxes(sanitized, threshold=0.75)

    # Write back
    out_lines = [f"{b[0]} {b[1]:.6f} {b[2]:.6f} {b[3]:.6f} {b[4]:.6f}" for b in deduped]
    file_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

def main():
    files = sorted(train_lbl_dir.glob("*.txt"))
    for f in files:
        process_file(f)
    print(f"Processed and refined all {len(files)} files.")

if __name__ == "__main__":
    main()
