from docuflow.utils.id_generator import generate_chunk_id


def get_meta_content_id(documents):
    ids = [generate_chunk_id(doc.page_content) for doc in documents]
    contents = [doc.page_content for doc in documents]
    metadata = [doc.metadata for doc in documents]

    return {"ids": ids, "documents": contents, "metadatas": metadata}


# if __name__ == "__main__":
#     pdf = get_latest_pdf(settings.pdf_dir)
#     markdown = convert_pdf_to_md(str(pdf))
#     documents = get_sections(markdown)

#     result = get_meta_content_id(documents)
#     print(result)
