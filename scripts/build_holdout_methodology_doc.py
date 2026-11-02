from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT = Path("docs/medical_test_holdout_methodology.docx")
FONT_NAME = "Arial"
EAST_ASIA_FONT = "Spoqa Han Sans Neo"


def set_run_font(run, size=None, bold=None, color=None):
    run.font.name = FONT_NAME
    run._element.rPr.rFonts.set(qn("w:ascii"), FONT_NAME)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), FONT_NAME)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), EAST_ASIA_FONT)
    run._element.rPr.rFonts.set(qn("w:cs"), FONT_NAME)
    run._element.rPr.rFonts.set(qn("w:hint"), "eastAsia")
    lang = run._element.rPr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        run._element.rPr.append(lang)
    lang.set(qn("w:val"), "ko-KR")
    lang.set(qn("w:eastAsia"), "ko-KR")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "D9E0E8")
        borders.append(element)
    tbl_pr.append(borders)


def style_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    styles = doc.styles
    normal = styles["Normal"]
    font_name = FONT_NAME
    normal.font.name = font_name
    normal._element.rPr.rFonts.set(qn("w:ascii"), font_name)
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), font_name)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), EAST_ASIA_FONT)
    normal._element.rPr.rFonts.set(qn("w:cs"), font_name)
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(40, 48, 58)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12
    for style_name, size in (("Title", 24), ("Heading 1", 15), ("Heading 2", 11)):
        style = styles[style_name]
        style.font.name = font_name
        style._element.rPr.rFonts.set(qn("w:ascii"), font_name)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), font_name)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), EAST_ASIA_FONT)
        style._element.rPr.rFonts.set(qn("w:cs"), font_name)
        style.font.size = Pt(size)
        style.font.bold = style_name != "Title"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(12 if style_name != "Title" else 0)
        style.paragraph_format.space_after = Pt(5)
    title_style = styles["Title"]._element
    p_pr = title_style.pPr
    if p_pr is not None:
        borders = p_pr.find(qn("w:pBdr"))
        if borders is not None:
            p_pr.remove(borders)


def add_table(doc: Document, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    set_borders(table)
    header = table.rows[0]
    set_repeat_table_header(header)
    for index, label in enumerate(headers):
        cell = header.cells[index]
        cell.text = label
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, "17365D")
        set_cell_margins(cell)
        for run in cell.paragraphs[0].runs:
            set_run_font(run, size=9, bold=True, color=(255, 255, 255))
        if widths:
            cell.width = Inches(widths[index])
    for row_i, row_values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row_values):
            cells[index].text = str(value)
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cells[index])
            if row_i % 2 == 1:
                set_cell_shading(cells[index], "F2F6FA")
            for paragraph in cells[index].paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    set_run_font(run, size=9, color=(40, 48, 58))
            if widths:
                cells[index].width = Inches(widths[index])
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    style_document(doc)

    title = doc.add_paragraph(style="Title")
    p_pr = title._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is not None:
        p_pr.remove(p_bdr)
    set_run_font(title.add_run("의료 QA 테스트셋 Holdout 방법"), size=24, bold=False, color=(0, 0, 0))
    title.paragraph_format.space_after = Pt(8)
    intro = doc.add_paragraph()
    intro.add_run(
        "기존 train 데이터에서 350개 질문을 평가용으로 분리했습니다. "
        "학습에는 분리 후 남은 6,047개만 사용하고, 모델 평가에는 보류한 350개를 사용합니다. "
        "질문과 정답, 문맥은 원본 행을 유지해 별도 생성 과정에서 생기는 내용 오류를 피합니다."
    )

    doc.add_heading("분할 개요", level=1)
    add_table(
        doc,
        ["구분", "행 수", "사용 목적"],
        [
            ("원본 train", "6,397", "분리 전 학습 데이터"),
            ("학습용 잔여 train", "6,047", "모델 학습 및 튜닝"),
            ("holdout test", "350", "학습에 사용하지 않는 최종 평가"),
            ("기존 validation", "1,162", "원본 validation 용도 유지"),
        ],
        [1.75, 0.85, 4.35],
    )
    p = doc.add_paragraph()
    p.add_run("분할 관계: ").bold = True
    p.add_run("원본 train 6,397 = 학습용 6,047 + holdout test 350")

    category_heading = doc.add_heading("유형별 할당", level=1)
    category_heading.paragraph_format.page_break_before = True
    p = doc.add_paragraph(
        "제공된 17개 유형의 원본 개수(합계 6,397)를 기준으로 각 비율을 350개에 적용했습니다. "
        "소수점 할당은 최대잔여 방식으로 정수화해 총합을 정확히 350개로 맞췄습니다."
    )
    p.paragraph_format.space_after = Pt(5)
    categories = [
        ("정의·의미", 1525, 83), ("원인", 863, 47), ("해부·생리", 627, 34),
        ("검사·정상수치", 559, 31), ("기타", 509, 28), ("기간·시기", 348, 19),
        ("효능·용도", 305, 17), ("약물", 272, 15), ("영양·식이", 263, 14),
        ("증상", 257, 14), ("예/아니오 확인", 247, 14), ("치료·관리", 162, 9),
        ("종류·분류", 157, 9), ("감염·전파", 149, 8), ("질환 특성·예후", 92, 5),
        ("비용·보험", 37, 2), ("예방", 25, 1),
    ]
    add_table(
        doc,
        ["유형", "원본 train", "테스트 할당", "테스트 비율"],
        [(name, f"{src:,}", n, f"{n/350:.1%}") for name, src, n in categories],
        [2.6, 1.25, 1.25, 1.85],
    )

    doc.add_heading("데이터 구성과 검증", level=1)
    doc.add_paragraph(
        "테스트 행은 원본 질문, answers, context 및 나머지 메타데이터를 유지합니다. "
        "question_category와 matched_keyword 열을 추가해 유형과 분류 근거를 확인할 수 있게 했습니다. "
        "테스트 파일의 split 값은 test로 설정했습니다."
    )
    for item in [
        "테스트 350개에서 query_id와 query가 각각 고유합니다.",
        "테스트 query_id는 학습용 잔여 train과 겹치지 않습니다.",
        "테스트 행의 결측치는 0개이며, 기존 validation 1,162개는 그대로 보존했습니다.",
        "고정 시드 20261102를 사용해 같은 원본에서 같은 표본을 재현할 수 있습니다.",
    ]:
        add_bullet(doc, item)

    doc.add_heading("사용 절차", level=1)
    add_table(
        doc,
        ["단계", "파일", "주의사항"],
        [
            ("학습", "data/derived/medical_train_without_test.parquet", "이 파일의 train 6,047개로 학습합니다."),
            ("평가", "data/derived/medical_test_350.parquet", "학습 및 튜닝에 사용하지 않은 뒤 최종 평가합니다."),
        ],
        [0.85, 3.0, 3.1],
    )
    doc.add_paragraph(
        "평가 결과를 보고 모델이나 프롬프트를 반복해서 조정하면 holdout 정보가 튜닝에 반영됩니다. "
        "그 경우에는 이 holdout을 최종 독립 평가로 간주하지 말고, 추가로 보류한 평가 데이터가 필요합니다."
    )

    doc.add_heading("파일과 재생성", level=1)
    add_bullet(doc, "테스트셋: data/derived/medical_test_350.parquet")
    add_bullet(doc, "학습용 잔여 데이터: data/derived/medical_train_without_test.parquet")
    add_bullet(doc, "분포표와 검증 기록: data/derived/medical_test_350_distribution.csv 및 medical_test_350_manifest.json")
    add_bullet(doc, "생성 스크립트: scripts/create_medical_test.py")
    p = doc.add_paragraph()
    p.add_run("재생성 명령: ").bold = True
    p.add_run("python scripts/create_medical_test.py")
    doc.save(OUT)
    print(OUT.resolve())


if __name__ == "__main__":
    main()
