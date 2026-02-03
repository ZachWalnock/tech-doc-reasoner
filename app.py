from ai.client import call_openai_with_graph_reasoning


def query_kg(user_query: str) -> str:
    return call_openai_with_graph_reasoning(user_query)


def main() -> None:
    prompt_style = "\033[1;34m"
    response_style = "\033[1;32m"
    reset_style = "\033[0m"
    while True:
        user_query = input(
            f"{prompt_style}What would you like to know about your technical documents? {reset_style}\n"
        )
        result = query_kg(user_query)
        print(f"{response_style}{result}{reset_style}")


if __name__ == "__main__":
    main()
