import json
import socket
from common import send_message, receive_message

# **Input Code:**
# ```cpp
# {{Insert C++ code here}}
# ```
#
def replace_code_in_promt(prompt:str, code:str):
    return prompt.replace("**SOURCE_CODE**",
        f"'**Input Code:**\n```cpp\n {{ {code}\n }}```\n")

def replace_test_in_promt(prompt:str, test:str):
    return prompt.replace("**TESTS**",
        f"'**Test Suite:**\n```cpp\n {{ {test}\n }}```\n")

def build_prompt(data):
    """Упрощенный промпт без Markdown-разметки"""
    if not data or 'src_code' not in data or 'prompt' not in data:
        return None

    prompt = data['prompt']
    code  = data['src_code']
    test_code = data['test_code']

    prompt= replace_test_in_promt(prompt, test_code)
    prompt = replace_code_in_promt(prompt, code)

    return prompt
def preprocess_code(content):
    """Очистка кода перед отправкой"""
    # Удаление комментариев и лишних пробелов
    lines = [
        line.rstrip()
        for line in content.split('\n')
        if not line.strip().startswith('//') and line.strip()
    ]
    return '\n'.join(lines)


def read_files_tag(input_data, tag):
    files = ""
    for filename in input_data.get(tag, []):
        try:
            with open(filename, 'r') as f:

                files = "".join([files,f'\n=== FILE {filename} ===\n'])
                files = "".join([files,f.read()])


        except Exception as e:
            print(f"Error reading {filename}: {e}")
            files = None

    return files
def load_input_json(input_path):
    """Возвращает структуру:
    {
        "source_code_files": {
            "file1.cpp": "код...",
            "prompt": "задание..."
        },
          "test_code_files": {
            "file.cpp": "kode"
        },
        "prompt": "content"
    }
    """
    try:
        with open(input_path, 'r') as f:
            input_data = json.load(f)
    except Exception as e:
        print(f"Error reading input JSON: {e}")
        return None


    src_code = read_files_tag(input_data, "source_code_files")
    test_code = read_files_tag(input_data, "test_code_files")
    prompt_file_name = input_data.get('prompt')
    prompt = ""

    with open(prompt_file_name, 'r') as f:
        prompt = f.read()

    return {'src_code' : src_code, 'test_code' : test_code, 'prompt': prompt}

def format_response(response_text):
    """Добавляет Markdown-форматирование к ответу"""
    formatted = response_text.replace('```', '\n```')  # Отделяем блоки кода
    return formatted.replace('\n- ', '\n* ')  # Заменяем маркеры списков

def save_response_to_md(response_data, filename="response.md"):
    """Сохраняет ответ сервера в markdown-файл с корректной кодировкой"""
    try:
        response_text = response_data.get('response', '')
        formatted_text = format_response(response_text)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Результат анализа\n\n")
            f.write(formatted_text)

        with open("response_raw.md", 'w', encoding='utf-8') as f:
            f.write("# Результат анализа\n\n")
            f.write(response_text)

        print(f"Ответ сохранен в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

def client(input_path, host, port):
    data = load_input_json(input_path)
    if not data:
        return

    # Формируем промпт локально
    full_prompt = build_prompt(data)
    if not full_prompt:
        print("Ошибка: Не удалось сформировать промпт")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            # Отправляем ТОЛЬКО готовый промпт
            print(f"send message with prompt: {full_prompt}")
            send_message(s, full_prompt)
            print("Prompt sent. Waiting for response...")
            response = receive_message(s)
            print("\nServer response:")

            save_response_to_md({'response': response})


    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == '__main__':
    client('input.json', 'localhost', 9999)