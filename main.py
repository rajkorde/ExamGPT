from dotenv import load_dotenv

from examgpt.core.question import LongForm, MultipleChoice
from examgpt.core.sources import PDFFile, Sources

assert load_dotenv()


def main() -> None:
    print(LongForm(question="What is 2 + 2?", answer="4"))
    print(
        MultipleChoice(
            question="What is 2 + 2?", choices=["2", "3", "4", "5"], answer="4"
        )
    )

    pdf_source = PDFFile(location="test.pdf")
    print(pdf_source)

    sources = Sources(sources=[pdf_source])
    print(sources)


if __name__ == "__main__":
    main()
