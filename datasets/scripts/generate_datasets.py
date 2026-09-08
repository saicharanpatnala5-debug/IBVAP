"""
IBVAP - Dataset Re-generation Tool
Regenerates all synthetic raw frames, test videos, and annotations on demand.
"""
import os, sys

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Triggering IBVAP Dataset Generation on: {target}")
    # Run the generator module
    from build_datasets_subsystem import build_full_dataset
    build_full_dataset(target)
