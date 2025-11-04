#!/usr/bin/env python
"""
Simple terminal test script for the Law Assistant RAG system.
This allows you to test the RAG system directly from the terminal.
"""

import sys
import os

# Add the law_assistant directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'law_assistant'))

from rag import rag


def main():
    print("=" * 60)
    print("Law Assistant - Terminal Test")
    print("=" * 60)
    print("\nThis script allows you to test the RAG system.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("\nВопрос (Question): ").strip()

            if question.lower() in ['exit', 'quit', 'выход']:
                print("\nДо свидания! (Goodbye!)")
                break

            if not question:
                print("Пожалуйста, введите вопрос. (Please enter a question.)")
                continue

            print("\nОбрабатываю вопрос... (Processing question...)")

            # Get answer from RAG system
            answer_data = rag(question)

            print("\n" + "=" * 60)
            print("Ответ (Answer):")
            print("=" * 60)
            print(answer_data['answer'])
            print("\n" + "-" * 60)
            print(f"Модель (Model): {answer_data['model_used']}")
            print(f"Время ответа (Response time): {answer_data['response_time']:.2f} секунд")
            print(f"Релевантность (Relevance): {answer_data['relevance']}")
            print(f"Токены (Tokens): {answer_data['total_tokens']}")
            print(f"Стоимость (Cost): ${answer_data['openai_cost']:.6f}")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\nПрервано пользователем. До свидания! (Interrupted. Goodbye!)")
            break
        except Exception as e:
            print(f"\nОшибка (Error): {str(e)}")
            print("Пожалуйста, убедитесь, что:")
            print("1. OPENAI_API_KEY установлен в переменных окружения")
            print("2. Файл data/data.csv существует")
            print("\nPlease make sure:")
            print("1. OPENAI_API_KEY is set in environment variables")
            print("2. data/data.csv file exists")


if __name__ == "__main__":
    main()
