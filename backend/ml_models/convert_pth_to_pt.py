import torch

PTH_PATH = "cattle_model.pth"        # your input file
PT_PATH  = "cattle_scripted.pt"  # output file

# 1) Try loading as a full model
try:
    model = torch.load(PTH_PATH, map_location="cpu")
    print("Loaded as full PyTorch model.")
except Exception as e:
    print("Failed to load as full model:", e)
    raise SystemExit("This .pth is NOT a full model. It's a state_dict. You need the original model class.")

model.eval()

# 2) Try converting to TorchScript using scripting
try:
    scripted = torch.jit.script(model)
    torch.jit.save(scripted, PT_PATH)
    print(f"Successfully saved TorchScript model as {PT_PATH}")
except Exception as e:
    print("Scripting failed, trying tracing...", e)

    # If scripting fails, try tracing (requires dummy input)
    # Adjust input size according to your model's expected input
    dummy_input = torch.randn(1, 3, 640, 640)

    try:
        traced = torch.jit.trace(model, dummy_input)
        traced.save(PT_PATH)
        print(f"Successfully saved traced TorchScript model as {PT_PATH}")
    except Exception as e2:
        print("Tracing also failed:", e2)
        raise SystemExit("Both scripting and tracing failed. Need the model architecture.")
