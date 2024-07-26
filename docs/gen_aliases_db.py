import ast
from pathlib import Path


def main(init_path: Path, output_path: Path) -> None:
    aliases_db = ['ALIASES_DB = {']

    with open(init_path, encoding='UTF-8') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.names:
                name = node.names[0]
                if not name.asname:
                    continue

                aliases_db.append(f"    'models.{name.asname}': '{node.module}.{name.name}',")

    aliases_db.append('}\n')

    with open(output_path, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(aliases_db))


if __name__ == '__main__':
    models_init_path = Path(__file__).absolute().parent.parent.joinpath('packages/atproto_client/models/__init__.py')
    aliases_db_path = Path(__file__).absolute().parent.joinpath('source/aliases_db.py')

    main(models_init_path, aliases_db_path)
