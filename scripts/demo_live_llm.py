#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src/ to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docuflow.services.llm_service import LLMService


def main():
    print("Initializing LLMService in LIVE mode (mock=False)...")
    llm = LLMService(mock=False)

    prompt = "Explain why RAG systems use chunking in one sentence."
    print(f"\nPrompt: '{prompt}'")

    try:
        response = llm.generate(prompt)
        print("\n=== RESPONSE ===")
        print(response)
        print("================\n")

        print(f"Model used: {llm.model_name}")
        print(f"Tokens: Input={llm.last_input_tokens}, Output={llm.last_output_tokens}")
        print(f"Estimated Cost: ${llm.last_cost_usd:.6f} USD")
    except Exception as e:
        print(f"Error occurred during generation: {e}")


if __name__ == "__main__":
    main()
