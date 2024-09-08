import os
from pathlib import Path


def main(path: Path) -> None:
    for root, _, files in os.walk(path):
        for file in files:
            if file.startswith('atproto_client.models.'):
                file_path = os.path.join(root, file)
                with open(file_path, encoding='UTF-8') as f:
                    content = f.read()
                    content = content.replace('atproto\\_client.models.', '')
                with open(file_path, 'w', encoding='UTF-8') as f:
                    f.write(content)


if __name__ == '__main__':
    main(Path(__file__).absolute().parent.joinpath('source'))
