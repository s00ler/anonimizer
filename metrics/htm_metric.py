import re
import ssl

from numpy import mean

from deeppavlov import configs, build_model

from sklearn.metrics import accuracy_score, precision_score, recall_score

full_fio_reg = (
    r'(?P<last_name>[А-ЯЁ][а-яё]{1,})(, | )' +
    r'(?P<name>[А-ЯЁ][а-яё]{1,}) (?P<sur_name>[А-ЯЁ][а-яё]{1,})'
)
short_fio_reg = r'(?P<last_name_1>[А-ЯЁ][а-яё]{1,}) (?P<initials>[А-ЯЁ]\.[А-ЯЁ]\.)'
login_reg = r'(?P<login>\(\w+-\w{1,}\))'

reg = r'({})'.format(r'|'.join([full_fio_reg, short_fio_reg, login_reg]))


def process_file(file, ner):
    text = []
    for line in file.readlines():
        text.append(line)

    joined_text = '\n'.join(text)

    reg_replace_map = {}
    clean_text = ' '.join(map(str.strip, joined_text.split()))
    fio_reg = re.compile(reg)

    for group in fio_reg.finditer(clean_text):
        for value in group.groupdict().values():
            if value and value not in reg_replace_map:
                reg_replace_map[value] = f'# {value}'

    personas = set()

    all_tokens = []
    for line in text:
        if line == '\n':
            continue

        tokens, tags = ner([line.strip()])
        all_tokens.extend(tokens[0])
        if tags and tokens:
            for i, (token, tag) in enumerate(zip(tokens[0], tags[0])):
                if '-PER' in tag:
                    if token not in personas:
                        personas.add(token)

    y_real = [(1 if token in reg_replace_map else 0) for token in all_tokens]
    y_pred = [(1 if token in personas else 0) for token in all_tokens]

    acc = accuracy_score(y_real, y_pred)
    pre = precision_score(y_real, y_pred)
    rec = recall_score(y_real, y_pred)
    print('F: {}, A: {}, P: {}, R: {}'.format(f.name, acc, pre, rec))

    return acc, pre, rec


if __name__ == '__main__':
    metrics = []
    files = [
        './temp/1.htm',
        './temp/2.htm',
        './temp/3.htm',
        './temp/4.htm',
        './temp/5.htm',
    ]

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    ner = build_model(configs.ner.ner_rus, download=True)

    for file in files:
        with open(file, 'r') as f:
            metrics.append(process_file(f, ner))

    print('Mean Accuracy:', mean(list(zip(*metrics))[0]))
    print('Mean Precision:', mean(list(zip(*metrics))[1]))
    print('Mean Recall:', mean(list(zip(*metrics))[2]))
