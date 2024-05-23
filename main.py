from examgpt.core.question import LongForm, MultipleChoice


def main() -> None:
    print(LongForm(question="What is 2 + 2?", answer="4"))
    print(
        MultipleChoice(
            question="What is 2 + 2?", choices=["2", "3", "4", "5"], answer="4"
        )
    )


if __name__ == "__main__":
    main()
