import os
import argparse

from doc2text import Document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--language', default='deu')
    parser.add_argument('-i', '--infile', required=True)
    parser.add_argument('-o', '--outfile', default=None)

    args = parser.parse_args()

    doc = Document.get_by_path(args.infile, language=args.language)
    result_text = doc.get_text()

    if args.outfile:
        with open(os.path.abspath(args.outfile), 'w') as outfile:
            outfile.write(result_text)
    else:
        print(result_text)


if __name__ == '__main__':
    main()
