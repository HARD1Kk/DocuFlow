from pathlib import Path

def save_pdf_to_md(text:str, filename:str, folder:str="debug")-> None:

    path = Path(folder)
    path.mkdir(exist_ok=True)

    return path







