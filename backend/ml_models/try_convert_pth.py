# try_convert_pth.py
# Place this file in backend/ml_models and run: python try_convert_pth.py
import torch, sys, traceback
from pathlib import Path
from ultralytics import YOLO

HERE = Path(__file__).parent
PTH = HERE / "cattle_model.pth"
OUT_TS = HERE / "cattle_model_torchscript.pt"
# candidate YOLO base .pt files in the folder above (common names)
CANDIDATES = [
    HERE.parent / "yolov8n-cls.pt",
    HERE.parent / "yolov8m-cls.pt",
    HERE.parent / "yolo11s-cls.pt",
    HERE.parent / "yolo11n-cls.pt",
    HERE.parent / "yolo11m-cls.pt"
]

def safe_print(s): 
    print(s); sys.stdout.flush()

if not PTH.exists():
    safe_print("ERROR: cattle_model.pth not found at: " + str(PTH))
    sys.exit(1)

safe_print("Loading cattle_model.pth ...")
data = torch.load(PTH, map_location="cpu")
safe_print("Loaded. type=" + str(type(data)))

# CASE A: it's a pickled module instance
if not isinstance(data, dict):
    safe_print("Detected pickled model object (torch.nn.Module or similar). Trying to export via tracing...")
    try:
        model = data
        model.eval()
        # default dummy: 1x3x224x224 — change if you know input size
        dummy = torch.randn(1, 3, 224, 224)
        try:
            ts = torch.jit.trace(model, dummy)
        except Exception as e:
            safe_print("trace failed, trying script(): " + str(e))
            ts = torch.jit.script(model)
        ts.save(OUT_TS)
        safe_print(f"SUCCESS: saved TorchScript to {OUT_TS}")
        sys.exit(0)
    except Exception:
        safe_print("Failed to export pickled model. Traceback:")
        traceback.print_exc()
        sys.exit(1)

# From here data is a dict
keys = list(data.keys())
safe_print("DICT keys (first 20): " + str(keys[:20]))

# helper to find nested state_dict
sd = None
for possible in ["state_dict", "model", "model_state_dict", "weights"]:
    if possible in data:
        safe_print(f"Found key '{possible}' — assuming that is state_dict")
        sd = data[possible]
        break
# if dict looks like param tensors (e.g. keys contain 'conv' or 'weight')
if sd is None:
    # heuristic: many keys look like 'backbone.conv1.weight' or '0.weight'
    if any(('weight' in k or 'backbone' in k or '.' in k) for k in keys):
        safe_print("Heuristic: using the top-level dict as state_dict")
        sd = data

if sd is None:
    safe_print("Unable to find a state_dict inside the .pth. Paste the printed DICT keys to the dev for further help.")
    sys.exit(1)

# Try to load into a YOLO base .pt and export from there
found_base = None
for cand in CANDIDATES:
    if cand.exists():
        found_base = cand
        break

if found_base is None:
    safe_print("No YOLO base .pt candidate found next to repo. Looking for any *.pt in parent folder...")
    for cand in sorted(HERE.parent.glob("*.pt")):
        safe_print(" - candidate: " + str(cand))
        if cand.name != "cattle_model.pth":
            found_base = cand
            break

if found_base:
    safe_print("Using YOLO base model: " + str(found_base))
    try:
        y = YOLO(str(found_base))
        # ultralytics' internal model is y.model (nn.Module)
        try:
            y.model.load_state_dict(sd, strict=False)
            safe_print("Loaded state_dict into YOLO base with strict=False")
        except Exception as e:
            safe_print("load_state_dict failed with strict=False? traceback:\n" + str(e))
            # try mapping if nested (e.g. sd['model'] etc.)
            # already handled earlier
        safe_print("Attempting to export YOLO object to torchscript via ultralytics.export() ...")
        y.export(format="torchscript")
        # ultralytics export writes files like model.torchscript.pt in current dir or same dir
        # search for newly created files
        found = list(HERE.glob("*.torchscript*")) + list(HERE.glob("*.pt"))
        safe_print("Export attempted. Check for created files: " + str([str(p.name) for p in found]))
        safe_print("If you see a file named *.torchscript.pt or similar, use that as the model.")
        sys.exit(0)
    except Exception:
        safe_print("Failed to use ultralytics export. Traceback:")
        traceback.print_exc()
        # fallthrough to try direct TorchScript tracing of a freshly loaded model object

# Last resort: try to construct a simple nn.Module wrapper & trace — not always possible
safe_print("As final fallback: try to wrap state_dict into a simple nn.Module (best-effort).")
try:
    import torch.nn as nn
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            # create a small conv if possible — this is a HACK and may fail
            self.conv = nn.Conv2d(3, 16, 3, padding=1)
            self.pool = nn.AdaptiveAvgPool2d(1)
            self.fc = nn.Linear(16, 10)
        def forward(self, x):
            x = self.conv(x)
            x = self.pool(x)
            x = x.view(x.shape[0], -1)
            return self.fc(x)
    m = DummyModel()
    try:
        m.load_state_dict(sd, strict=False)
        m.eval()
        ts = torch.jit.trace(m, torch.randn(1,3,224,224))
        ts.save(OUT_TS)
        safe_print(f"Saved dummy-traced TorchScript to {OUT_TS} (may not be correct).")
        sys.exit(0)
    except Exception:
        safe_print("Dummy approach failed.")
        traceback.print_exc()
        sys.exit(1)
except Exception:
    safe_print("Could not run fallback dummy approach.")
    traceback.print_exc()
    sys.exit(1)
