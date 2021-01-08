from collections import Counter
from pathlib import Path
from nltk import stem

import click
import tqdm
import re


import hunspell
hobj = hunspell.HunSpell('/usr/share/hunspell/de_DE.dic', '/usr/share/hunspell/de_DE.aff')


def export_word_frequency(filepath, word_frequency: Counter):
    """ Export a word frequency

        Args:
            filepath (str):
            word_frequency (Counter):
    """
    with open(filepath, 'w') as f:
        sorted_freqs = sorted(word_frequency.items(), key=(lambda e: e[1]), reverse=True)
        for (word, freq) in sorted_freqs:
            f.write(f"{freq} {word}\n")


def build_word_frequency(filepath: Path, language: str):
    """ Parse the passed in text file (likely from Open Subtitles) into
        a word frequency list and write it out to disk

        Args:
            filepath (Path):
            language (str):
        Returns:
            Counter: The word frequency as parsed from the file
        Note:
            This only removes words that are proper nouns (attempts to...) and
            anything that starts or stops with something that is not in the alphabet.
    """
    try:
        from nltk.tag import pos_tag
        from nltk.tokenize import WhitespaceTokenizer
        from nltk.tokenize.toktok import ToktokTokenizer
    except ImportError as ex:
        raise ImportError("To build a dictioary from scratch, NLTK is required!\n{}".format(ex.message))

    word_frequency = Counter()
    tok = WhitespaceTokenizer()

    with open(filepath, mode="r") as fobj:
        for line in tqdm.tqdm(fobj):
            # tokenize into parts
            parts = tok.tokenize(line)

            # Attempt to remove proper nouns
            # Remove things that have leading or trailing non-alphabetic characters.
            tagged_sent = pos_tag(parts)
            words = [
                word[0].lower() for word in tagged_sent
                if word[0]
                and not word[1] == "NNP"
                and word[0][0].isalpha()
                and word[0][-1].isalpha()
            ]

            if words:
                word_frequency.update(words)

    return word_frequency


def clean_english(word_frequency: Counter, filepath_exclude:Path=None):
    """ Clean an English word frequency list

        Args:
            word_frequency (Counter):
            filepath_exclude (str):
    """
    letters = set("abcdefghijklmnopqrstuvwxyz'")

    # remove words with invalid characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words without a vowel
    no_vowels = list()
    vowels = set("aeiouy")
    for key in word_frequency:
        if vowels.isdisjoint(key):
            no_vowels.append(key)
    for misfit in no_vowels:
        word_frequency.pop(misfit)

    # Remove double punctuations (a-a-a-able) or (a'whoppinganda'whumping)
    double_punc = list()
    for key in word_frequency:
        if key.count("'") > 1 or key.count(".") > 2:
            double_punc.append(key)
    for misfit in double_punc:
        word_frequency.pop(misfit)

    # remove ellipses
    ellipses = list()
    for key in word_frequency:
        if ".." in key:
            ellipses.append(key)
    for misfit in ellipses:
        word_frequency.pop(misfit)

    # leading or trailing doubles a, "a'", "zz", ending y's
    doubles = list()
    for key in word_frequency:
        if key.startswith("aa") and key not in ("aardvark", "aardvarks"):
            doubles.append(key)
        elif  key.startswith("a'"):
            doubles.append(key)
        elif  key.startswith("zz"):
            doubles.append(key)
        elif  key.endswith("yy"):
            doubles.append(key)
        elif  key.endswith("hh"):
            doubles.append(key)
    for misfit in doubles:
        word_frequency.pop(misfit)

    # common missing spaces
    missing_spaces = list()
    for key in word_frequency:
        if key.startswith("about") and key != "about":
            missing_spaces.append(key)
        elif key.startswith("above") and key != "above":
            missing_spaces.append(key)
        elif key.startswith("after") and key != "after":
            missing_spaces.append(key)
        elif key.startswith("against") and key != "against":
            missing_spaces.append(key)
        elif key.startswith("all") and word_frequency[key] < 15:
            missing_spaces.append(key)
        elif key.startswith("almost") and key != "almost":
            missing_spaces.append(key)
        # This one has LOTS of possibilities...
        elif key.startswith("to") and word_frequency[key] < 25:
            missing_spaces.append(key)
        elif key.startswith("can't") and key != "can't":
            missing_spaces.append(key)
        elif key.startswith("i'm") and key != "i'm":
            missing_spaces.append(key)
    for misfit in missing_spaces:
        word_frequency.pop(misfit)


    return word_frequency


def choose_german(word, stem_options):
    if word.endswith("en") or word.endswith("es"):
        if word[:-2] in stem_options:
            return word[:-2]
        elif word in stem_options:
            return word
    if re.match(r'.*(t|e|st)', word):
        for alt in stem_options:
            if alt.endswith("en"):
                return alt
    if (word.endswith("e") or word.endswith("s")) and (word[:-1] in stem_options):
        return word[:-1]
    if word.endswith("ere") and word[:-3] in stem_options:
        return word[:-3]
    if word.endswith("er") and word[:-2] in stem_options:
        return word[:-2]
    if word.endswith("ere") and word[:-1] in stem_options:
        return word[:-1]
    if re.match(r'v[oe]r.*', word):
        start = word[:3]
        filtered_options = [alt for alt in stem_options if alt.startswith(start)]
        if len(filtered_options) == 1:
            return filtered_options[0]
    if re.match(r'[td]e[rn].*', word):
        if word[:-1] in stem_options:
            return word[:-1]

    if word in stem_options:
        return word

    return None

def clean_german(word_frequency:Counter, filepath_exclude:Path=None):
    """ Clean a German word frequency list

        Args:
            word_frequency (Counter):
            filepath_exclude (str):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzäöüß")

    # fix issues with words containing other characters
    invalid_chars = set()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.add(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # singularize nouns, conjugate verbs

    result = Counter()
    for word, freq in word_frequency.items():
        word = str(word)

        # stemming
        stem_options = hobj.stem(word)
        if len(stem_options) > 1:
            correction = choose_german(word, [o.decode() for o in stem_options])
            if correction is None:
                print("not stemmed: ", word, stem_options)
                continue

            word = correction

        result.update({word: freq})
    
    return result


def clean_french(word_frequency: Counter, filepath_exclude:Path=None):
    """ Clean a French word frequency list

        Args:
            word_frequency (Counter):
            filepath_exclude (str):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzéàèùâêîôûëïüÿçœæ")

    # fix issues with words containing other characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    return word_frequency


@click.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option("-l", "--language", type=click.Choice(["de", "en", "fr"]), default="en")
@click.option("-e", "--exclude", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", type=click.Path(dir_okay=False), default="out.txt")
@click.option("-t", "--threshold", type=click.IntRange(min=0), default=0)
def cli(input, language, exclude, output, threshold):
    word_frequency = build_word_frequency(input, language)

    # clean up the dictionary
    if language == "en":
        word_frequency = clean_english(word_frequency, exclude)
    elif language == "de":
        word_frequency = clean_german(word_frequency, exclude)
    elif language == "fr":
        word_frequency = clean_french(word_frequency, exclude)

    # remove flagged misspellings
    if exclude is not None:
        with open(exclude, 'r') as fobj:
            for line in fobj:
                line = line.strip()
                if line in word_frequency:
                    word_frequency.pop(line)


    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= threshold:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # export word frequency
    export_word_frequency(output, word_frequency)

if __name__ == '__main__':
    cli()

