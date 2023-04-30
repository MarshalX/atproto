from codegen import capitalize_first_symbol
from lexicon.parser import lexicon_parse_dir


_PARAMS_SUFFIX = 'Params'
_INPUT_SUFFIX = 'Data'
_OPTIONS_SUFFIX = 'Options'
_OUTPUT_SUFFIX = 'Response'


def get_params_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_PARAMS_SUFFIX}'


def get_data_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_INPUT_SUFFIX}'


def get_options_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_OPTIONS_SUFFIX}'


def get_response_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_OUTPUT_SUFFIX}'


def generate_models():
    lexicons = lexicon_parse_dir()

    # TODO(MarshalX): impl


if __name__ == '__main__':
    generate_models()
