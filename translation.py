import argparse
import json
import os
from pathlib import Path

import boto3
import yaml


def get_args():
    parser = argparse.ArgumentParser(description='AWS Translate with Boto3')
    parser.add_argument('--config', help='yaml file path')
    parser.add_argument('--src', nargs='+', help='src text file path(s)')
    parser.add_argument('--dst', help='dst jsonl file path')
    return parser.parse_args()


def get_client(session_config):
    if session_config is not None and len(session_config) > 0:
        session = boto3.Session(**session_config)
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
        **translate_kwargs
    )
    return response


def write_jsonl_file(src_file_paths, client, config, dst_file_path):
    if dst_file_path is None:
        print('`dst_file_path` cannot be None')
        return

    dst_file_path = os.path.expanduser(dst_file_path)
    Path(dst_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(dst_file_path, 'w') as fp:
        for src_file_path in src_file_paths:
            src_texts = load_src_texts(src_file_path)
            for src_text in src_texts:
                response = translate(src_text, client, config['translate'])
                json.dump(response, fp)
                fp.write('\n')


def main(args):
    config = load_config(args.config)
    translate_config = config['translate']
    client = get_client(config.get('session'))
    src_file_paths = args.src
    if src_file_paths is None or len(src_file_paths) == 0:
        response = translate(None, client, translate_config)
        print(response)
    else:
        write_jsonl_file(src_file_paths, client, config, args.dst)


if __name__ == '__main__':
    main(get_args())
