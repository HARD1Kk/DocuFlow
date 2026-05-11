from dataclasses import dataclass


@dataclass
class PaddleConfig:
    lang: str = "en"
    use_textline_orientation: bool = True
    use_doc_orientation_classify: bool = True
    use_doc_unwarping: bool = True

    # models
    text_detection_model: str = "PP-OCRv5_server_det"
    text_recognition_model: str = "PP-OCRv5_server_rec"
