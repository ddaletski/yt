from collections import Counter
from pathlib import Path

import click
import spacy
from rich.progress import track
import re

def export_word_frequency(filepath, word_frequency: Counter):
    with open(filepath, 'w') as f:
        sorted_freqs = sorted(word_frequency.items(), key=(lambda e: e[1]), reverse=True)
        for (word, freq) in sorted_freqs:
            f.write(f"{freq}\t{word}\n")


def calculate_word_frequency(filepath: Path, spacy_module: str):
    nlp = spacy.load(spacy_module)
    word_frequency = Counter()

    with open(filepath, mode="r") as fobj:
        for line in track(fobj):
            # tokenize into parts
            words = [t.lemma_ for t in nlp.tokenizer(line)]
            word_frequency.update(words)

    return word_frequency


@click.command()
@click.argument("text", type=click.Path(exists=True, dir_okay=False))
@click.option("-l", "--language", type=click.Choice(["de", "en", "fr"]), default="en")
@click.option("-o", "--output", type=click.Path(dir_okay=False), default="out.txt")
@click.option("-t", "--threshold", type=click.IntRange(min=0), default=0)
def cli(text, language, exclude, output, threshold):

    spacy_module = ''
    if language == "de":
        spacy_module = 'de_core_news_sm'
    elif language == "en":
        raise Exception("unsupported language")
    elif language == "fr":
        raise Exception("unsupported language")

    word_frequency = calculate_word_frequency(text, spacy_module)

    # remove infrequent words (less than a threshold)
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= threshold:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # export dictionary
    export_word_frequency(output, word_frequency)

if __name__ == '__main__':
    cli()

