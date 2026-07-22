import pytest
from docuflow.utils.text_cleaner import TextCleaner


def test_text_cleaner_whitespace():
    cleaner = TextCleaner()
    input_text = "This  is   a   test  with   multiple   spaces.  "
    expected = "This is a test with multiple spaces."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_leading_indent():
    cleaner = TextCleaner()
    input_text = "    This is indented.\n  This is also indented."
    expected = "    This is indented.\n  This is also indented."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_unicode_normalization():
    cleaner = TextCleaner()
    # Smart quotes and dashes
    input_text = "“Hello” – said the ‘expert’—"
    expected = '"Hello" - said the \'expert\'--'
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_control_characters():
    cleaner = TextCleaner()
    # Contains null byte and backspace, etc.
    input_text = "Hello\x00 World\x07!"
    expected = "Hello World!"
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_hyphen_merge():
    cleaner = TextCleaner()
    # Simple word continuation
    input_text = "This is an outstand-\ning result."
    expected = "This is an outstanding result."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_hyphen_merge_multiple_lines():
    cleaner = TextCleaner()
    input_text = "This is an out-\nstand-\ning result."
    expected = "This is an outstanding result."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_compound_word_hyphen():
    cleaner = TextCleaner()
    # Compound word hyphenation across lines should keep the hyphen
    input_text = "This is a state-\nof-the-art model."
    expected = "This is a state-of-the-art model."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_hyphen_no_merge_uppercase():
    cleaner = TextCleaner()
    # If the next line starts with an uppercase letter, do not merge
    input_text = "This is a sentence ending with a hyphen-\nIng result."
    expected = "This is a sentence ending with a hyphen-\nIng result."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_markdown_structure_preserved():
    cleaner = TextCleaner()
    input_text = (
        "# Heading with  extra   spaces\n"
        "Some normal  text   here.\n"
        "| Table  | Header |\n"
        "|---|---|\n"
        "| col 1  | col 2 |\n"
        "- List  item   1\n"
        "* List  item   2\n"
        "1. List  item   3\n"
        "> Block  quote   here\n"
        "```\n"
        "code  block   retains   spaces\n"
        "```"
    )
    # The header, table, list items, blockquote, and code block lines should NOT have internal spaces collapsed
    # Only "Some normal text here." should be normalized
    expected = (
        "# Heading with  extra   spaces\n"
        "Some normal text here.\n"
        "| Table  | Header |\n"
        "|---|---|\n"
        "| col 1  | col 2 |\n"
        "- List  item   1\n"
        "* List  item   2\n"
        "1. List  item   3\n"
        "> Block  quote   here\n"
        "```\n"
        "code  block   retains   spaces\n"
        "```"
    )
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_pdf_multiple_word_continuations():
    cleaner = TextCleaner()
    input_text = (
        "The organi-\n"
        "zation intro-\n"
        "duced an inter-\n"
        "national stan-\n"
        "dard."
    )
    expected = "The organization introduced an international standard."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_complex_pdf_ocr_document():
    cleaner = TextCleaner()
    input_text = (
        "# Executive  Summary\n"
        "\n"
        "The  “DocuFlow”  plat-\n"
        "form\x00  provides   state-\n"
        "of-the-art  processing—"
        "for   enterprise   users.\x07"
    )
    expected = (
        "# Executive  Summary\n"
        "\n"
        'The "DocuFlow" platform provides state-of-the-art processing--for enterprise users.'
    )
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_nested_markdown_with_wrapped_paragraph():
    cleaner = TextCleaner()
    input_text = (
        "> Quote  with   extra   spaces\n"
        "> and another line.\n"
        "\n"
        "Normal   para-\n"
        "graph   continues   here."
    )
    expected = (
        "> Quote  with   extra   spaces\n"
        "> and another line.\n"
        "\n"
        "Normal paragraph continues here."
    )
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_preserve_code_block_with_embedded_control_chars():
    cleaner = TextCleaner()
    input_text = (
        "Example:\n"
        "```\n"
        "hello\x00  world\n"
        "value   =   10\n"
        "```\n"
        "\n"
        "Some   normal   text."
    )
    expected = (
        "Example:\n"
        "```\n"
        "hello\x00  world\n"
        "value   =   10\n"
        "```\n"
        "\n"
        "Some normal text."
    )
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_do_not_merge_numeric_ranges():
    cleaner = TextCleaner()
    input_text = "Pages 123-\n456 contain the appendix."
    expected = "Pages 123-\n456 contain the appendix."
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_preserve_email_and_url_wrapping():
    cleaner = TextCleaner()
    input_text = (
        "Contact us at support@example.\n"
        "com or visit https://example.\n"
        "com/docs for more information."
    )
    # Note: URLs/emails end in period or slash, not lower case letters, so hyphen merge is bypassed
    expected = (
        "Contact us at support@example.\n"
        "com or visit https://example.\n"
        "com/docs for more information."
    )
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_do_not_modify_yaml_frontmatter():
    cleaner = TextCleaner()
    input_text = (
        "---\n"
        "title:   My   Document\n"
        "author:  Jane Doe\n"
        "---\n"
        "\n"
        "Some   normal   text."
    )
    expected = (
        "---\n"
        "title:   My   Document\n"
        "author:  Jane Doe\n"
        "---\n"
        "\n"
        "Some normal text."
    )
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_mixed_unicode_and_word_wrapping():
    cleaner = TextCleaner()
    input_text = (
        "The ‘well-\n"
        "known’ author said,\n"
        "“Extra   spaces   matter.”"
    )
    expected = "The 'well-known' author said,\n" '"Extra spaces matter."'
    assert cleaner.clean(input_text) == expected


def test_text_cleaner_extremely_messy_realistic_pdf_page():
    cleaner = TextCleaner()
    input_text = (
        "# Report\n"
        "\n"
        "The   organi-\n"
        "zation\x00  intro-\n"
        "duced  a  state-\n"
        "of-the-art   sys-\n"
        "tem—designed   for   large-\n"
        "scale deployments.\x07\n"
        "\n"
        "- Bullet   should   stay   untouched\n"
        "| Table  | Value |\n"
        "|---|---|\n"
        "| A  |  B |\n"
    )
    expected = (
        "# Report\n"
        "\n"
        "The organization introduced a state-of-the-art system--designed for large-scale deployments.\n"
        "\n"
        "- Bullet   should   stay   untouched\n"
        "| Table  | Value |\n"
        "|---|---|\n"
        "| A  |  B |\n"
    )
    assert cleaner.clean(input_text) == expected
