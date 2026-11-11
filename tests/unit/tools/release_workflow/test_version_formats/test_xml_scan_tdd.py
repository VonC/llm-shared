"""The expat scanner locates wanted XML element text with its byte span.

Step 7 of v0.14.0 version-sources: `xml_scan.scan` records each element whose
path the caller wants, in document order, with its text, the byte span of that
text and the start offset of its parent element, which groups the fields of
one `<dependency>`. Spans skip the XML whitespace around the text and stay
right after accented and non-BMP text, behind a byte-order mark and in CRLF
files; attributes and indentation around an element change nothing, and the
same name at another path is ignored. A comment, CDATA section, processing
instruction, child element, or entity or character reference inside a wanted
element keeps its parsed text but makes it unusable as an owned field. A
declared encoding other than UTF-8, invalid UTF-8 and malformed XML fail.
"""

from __future__ import annotations

import re

import pytest

from tests.unit.tools.release_workflow.version_support import BOM, crlf
from tools.release_workflow.sources import xml_scan
from tools.release_workflow.sources.model import SourceError, Span

_WANTED = re.compile(r"project/(?:version|parent/version|dependencies/dependency/(?:groupId|artifactId|version))")
_POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <description>Café 🎉 <version>9.9.9</version></description>
  <parent><version>1.0.0</version></parent>
  <version>0.13.0-SNAPSHOT</version>
  <dependencies>
    <dependency><groupId>com.demo</groupId><artifactId>core</artifactId><version>0.13.0</version></dependency>
    <dependency>
      <groupId>org.ext</groupId>
      <artifactId>lib</artifactId>
    </dependency>
  </dependencies>
  <build><plugins><plugin><version>3.0</version></plugin></plugins></build>
</project>
""".encode()


def _scan(content: bytes) -> xml_scan.PomDocument:
    """Scan with the test's wanted paths."""
    return xml_scan.scan(content, "pom.xml", _WANTED)


def _located(content: bytes, value: xml_scan.XmlValue) -> bytes:
    """Return the bytes a value's span covers."""
    return content[value.span.start:value.span.end]


def _version(inner: str) -> xml_scan.XmlValue:
    """Scan a project whose `<version>` element holds `inner` and return that value."""
    value = _scan(f"<project><version>{inner}</version></project>".encode()).first("project/version")
    assert value is not None
    return value


@pytest.mark.parametrize("content", [_POM, crlf(_POM), BOM + _POM])
def test_wanted_paths_are_located_with_byte_spans(content: bytes) -> None:
    """Every wanted element, and only those, in document order with spans over its exact bytes."""
    document = _scan(content)
    assert document.root == "project"
    assert [(value.path, value.text, _located(content, value)) for value in document.values] == [
        ("project/parent/version", "1.0.0", b"1.0.0"),
        ("project/version", "0.13.0-SNAPSHOT", b"0.13.0-SNAPSHOT"),
        ("project/dependencies/dependency/groupId", "com.demo", b"com.demo"),
        ("project/dependencies/dependency/artifactId", "core", b"core"),
        ("project/dependencies/dependency/version", "0.13.0", b"0.13.0"),
        ("project/dependencies/dependency/groupId", "org.ext", b"org.ext"),
        ("project/dependencies/dependency/artifactId", "lib", b"lib"),
    ]
    first, second = (frozenset(value.parent for value in document.values[2:5]), frozenset(value.parent for value in document.values[5:]))
    assert len(first) == len(second) == 1
    assert first != second


def test_lookups_by_path() -> None:
    """`first` gives the first value of a path, `every` all of them, absent paths give nothing."""
    document = _scan(_POM)
    assert [value.text for value in document.every("project/dependencies/dependency/groupId")] == ["com.demo", "org.ext"]
    assert document.first("project/version") == document.every("project/version")[0]
    assert (document.first("project/groupId"), document.every("project/groupId")) == (None, ())


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_whitespace_and_attributes_around_an_owned_element(newline: str) -> None:
    """Indentation, attributes and whitespace inside the element stay outside the span."""
    content = f'<project>{newline}  <version id="v" >{newline}   0.13.0 \t{newline}  </version >{newline}</project>'.encode()
    value = _scan(content).first("project/version")
    assert value is not None
    assert (value.text, _located(content, value), value.problem) == ("0.13.0", b"0.13.0", None)
    assert value.owned("pom.xml") == value.span


@pytest.mark.parametrize("element", ["<version></version>", "<version/>", "<version>  \n </version>"])
def test_an_empty_element_reads_as_empty_text(element: str) -> None:
    """An empty, self-closing or blank element gives empty text and an empty span."""
    value = _scan(f"<project>{element}</project>".encode()).first("project/version")
    assert value is not None
    assert (value.text, value.span.start == value.span.end, value.problem) == ("", True, None)


@pytest.mark.parametrize(("inner", "text", "problem"), [
    ("0.13.0<!-- next -->", "0.13.0", "a comment"),
    ("<![CDATA[0.13.0]]>", "0.13.0", "a CDATA section"),
    ("<?pi data?>0.13.0", "0.13.0", "a processing instruction"),
    ("<x/>0.13.0", "0.13.0", "child markup <x>"),
    ("0.13&#46;0", "0.13.0", "an entity or character reference"),
    ("0.13.0&amp;", "0.13.0&", "an entity or character reference"),
])
def test_markup_inside_an_owned_element_makes_it_unusable(inner: str, text: str, problem: str) -> None:
    """The parsed text stays readable; owning the field fails, naming the file, the path and the markup."""
    value = _version(inner)
    assert (value.text, value.problem) == (text, problem)
    with pytest.raises(SourceError, match=rf"^pom\.xml: <project/version> holds {re.escape(problem)}, which versions set cannot edit"):
        value.owned("pom.xml")


@pytest.mark.parametrize("declaration", ['<?xml version="1.0"?>', '<?xml version="1.0" encoding="UTF-8"?>',
                                         "<?xml version='1.0' encoding='utf8'?>", ""])
def test_utf8_or_no_declared_encoding_is_accepted(declaration: str) -> None:
    """A POM is UTF-8 by default or by declaration."""
    assert _scan(f"{declaration}<project><version>1</version></project>".encode()).first("project/version") is not None


@pytest.mark.parametrize(("content", "named"), [
    (b'<?xml version="1.0" encoding="ISO-8859-1"?><project/>', r"pom\.xml declares encoding 'ISO-8859-1': a POM must be UTF-8"),
    (b"<project><version>\xff</version></project>", r"pom\.xml is not valid UTF-8 at byte 18"),
    (b"<project><version>1</project>", r"pom\.xml is not well-formed XML: .*; correct the file"),
    (b"", r"pom\.xml is not well-formed XML"),
])
def test_encodings_and_malformed_files_fail(content: bytes, named: str) -> None:
    """Only well-formed UTF-8 XML is scanned."""
    with pytest.raises(SourceError, match=named):
        _scan(content)


def test_spans_are_byte_offsets() -> None:
    """Multi-byte text and a byte-order mark before the value shift the span by their bytes."""
    content = BOM + "<project><name>é😀</name><version>1.0</version></project>".encode()
    value = _scan(content).first("project/version")
    assert value is not None
    start = len(BOM) + len("<project><name>é😀</name><version>".encode())
    assert value.span == Span(start, start + 3)


# eof
