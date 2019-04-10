import re
import sys
from hashlib import md5

full_fio_reg = (
    r'(?P<last_name>[А-ЯЁ][а-яё]{1,})(, | )' +
    r'(?P<name>[А-ЯЁ][а-яё]{1,}) (?P<sur_name>[А-ЯЁ][а-яё]{1,})'
)
short_fio_reg = r'(?P<last_name_1>[А-ЯЁ][а-яё]{1,}) (?P<initials>[А-ЯЁ]\.[А-ЯЁ]\.)'
login_reg = r'(?P<login>\(\w+-\w{1,}\))'

reg = r'({})'.format(r'|'.join([full_fio_reg, short_fio_reg, login_reg]))

if __name__ == '__main__':
    text = []
    for line in sys.stdin:
        text.append(line)

    text = '\n'.join(text)

    replace_map = {}
    clean_text = ' '.join(map(str.strip, text.split()))
    fio_reg = re.compile(reg)

    for group in fio_reg.finditer(clean_text):
        for value in group.groupdict().values():
            if value and value not in replace_map:
                replace_map[value] = md5(value.encode('utf-8')).hexdigest()

    for line in text.split('\n'):
        for key, value in replace_map.items():
            line = line.replace(key, value)
        sys.stdout.write(line)
