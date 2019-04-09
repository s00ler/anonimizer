import ssl
import random
import argparse
from hashlib import md5

from deeppavlov import configs, build_model

parser = argparse.ArgumentParser(description='Anonimize some text.')
parser.add_argument('-i', '--input', type=str, help='input file path')
parser.add_argument('-o', '--output', type=str, help='output file path')
parser.add_argument('-s', '--seed', type=int, help='random seed', default=0)
parser.add_argument('--use_hash', action='store_true', default=False)
parser.add_argument('--names_path', type=str, help='path to names file', default='./names.csv')


def is_english(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def deal_with_file(input_file, output_file, model, names):
    personas = set()
    lines = []

    with open(input_file, 'r') as f:
        for line in f.readlines():
            if line == '\n':
                continue
            tokens, tags = model([line.strip()])
            if tags and tokens:
                for token, tag in zip(tokens[0], tags[0]):
                    if not is_english(token) and '-PER' in tag:
                        if token not in personas:
                            personas.add(token)
            lines.append(line)

    if names is None:
        replace_map = {p: md5(p.encode('utf-8')).hexdigest() for p in personas}
    else:
        replace_map = names

    with open(output_file, 'w') as f:
        for line in lines:
            for key in personas:
                line = line.replace(key, replace_map.get(key, key))
            f.write(line)


if __name__ == '__main__':
    args = parser.parse_args()

    # Этот колхоз нужен из-за глюков nltk
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    ner = build_model(configs.ner.ner_rus, download=True)

    personas = set()
    lines = []
    random.seed(args.seed)
    names = None
    if not args.use_hash and args.names_path:
        with open(args.names_path, 'r') as f:
            names = f.read().split(',')
        replaces = list(names)
        random.shuffle(replaces)
        names = {n: r for n, r in zip(names, replaces)}

    # Сюда можно прихерачить обход директории и тд и тп
    deal_with_file(args.input, args.output, ner, names)