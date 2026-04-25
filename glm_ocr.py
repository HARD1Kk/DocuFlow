import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "zai-org/GLM-OCR"

# Load tokenizer & model (official requirement: trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

model = (
    AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype=torch.float16).cuda().eval()
)

# Load image
image = Image.open("example.png").convert("RGB")

# Prompt (official style = instruction-based)
prompt = "Extract all text from this document."

# Run inference
response, history = model.chat(tokenizer, query=prompt, image=image, history=[])

print(response)
