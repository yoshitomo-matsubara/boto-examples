import argparse
import boto3
import yaml
import os


def get_args():
    parser = argparse.ArgumentParser(description='AWS Translate with Boto3')
    parser.add_argument('--config', help='yaml file path')
    parser.add_argument('--src', nargs='+', help='src text file path(s)')
    return parser.parse_args()


def get_client(session_config):
    if session_config is not None and len(session_config) > 0:
        session = boto3.Session()
        return session.client('translate')
    return boto3.client('translate')


def load_config(yaml_file_path):
    with open(os.path.expanduser(yaml_file_path), 'r') as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def load_src_texts(src_file_path):
    with open(os.path.expanduser(src_file_path), 'r', newline='') as fp:
        return [line.strip() for line in fp]


def translate(src_text, client, translate_kwargs):
    if src_text is None:
        src_text = translate_kwargs.pop('Text')

    response = client.translate_text(
        Text=src_text,
        TerminologyNames=[
            'string',
        ],
        SourceLanguageCode='string',
        TargetLanguageCode='string',
        Settings={
            'Formality': 'FORMAL',
            'Profanity': 'MASK'
        },
        **translate_kwargs
    )
    return response


def main(args):
    config = args.config
    translate_config = config['translate']
    client = boto3.client('translate')
    src_file_paths = args.src
    if src_file_paths is None or len(src_file_paths) == 0:
        translate(None, client, translate_config)

    for src_file_path in args.src:
        src_texts = load_src_texts(src_file_path)
        response = translate(src_texts, client, **config['translate'])



if __name__ == '__main__':
    main(get_args())
