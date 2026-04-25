import importlib
import importlib.util
import sys

spec = importlib.util.find_spec("paddleocr")
if not spec:
    print("paddleocr not installed")
    sys.exit(1)

p = importlib.import_module("paddleocr")
print("paddleocr module version:", getattr(p, "__version__", "<unknown-version>"))
print("Has PPStructureV3:", hasattr(p, "PPStructureV3"))

# Try instantiation (may attempt to download/init models)
try:
    PPStructureV3 = getattr(p, "PPStructureV3", None)
    if PPStructureV3 is None:
        print("PPStructureV3 not present in installed paddleocr.")
        sys.exit(2)
    pipeline = PPStructureV3(lang="en")
    print("PPStructureV3 instantiated successfully.")
except Exception as e:
    print("Failed to instantiate PPStructureV3:", e)
    sys.exit(3)
