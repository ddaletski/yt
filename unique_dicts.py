from os import error
import re
import pandas as pd
import click
from matplotlib import pyplot as plt
from pandas.core.reshape.merge import merge


@click.command()
@click.argument("src", type=click.File(mode="r"), nargs=-1, required=True)
@click.option("-o", "--output-dir", "out_dir", type=click.Path(file_okay=False), required=True)
def cli(src, out_dir):
    frames = []
    for f in src:
        d: pd.DataFrame = pd.read_csv(f, delimiter=' ', header=None, names=["freq", "word"])
        d = pd.DataFrame(d.loc[:, "freq"]).set_index(d.word)
        frames.append(d)

    # merge frames adding frequencies
    # result_frame: pd.DataFrame = pd.concat(frames, axis=0).groupby("word").agg("sum")


    # words from intersections of every ordered pair of data frames
    common_parts = []
    for i in range(len(frames)):
        for j in range(1, i):
            # inner merge to get an intersection
            merged = pd.merge(frames[i], frames[j], left_index=True, right_index=True)
            # aggregate frequencies obtained from two dataframes
            merged['freq'] = merged.freq_x + merged.freq_y 
            # drop other columns
            merged.drop(["freq_x", "freq_y"], axis=1, inplace=True)
            # add to the "common" frames
            common_parts.append(merged)

    # sum frequencies and get "common" dictionary with words,
    # that appear at least in two source dictionaries at once 
    common = pd.concat(common_parts).groupby("word").agg("sum")

    print(common)

    # drop common words from source dictionaries
    for frame in frames:
        print(frame)
        frame.drop(common.index, errors='ignore', inplace=True)
        print(frame)

        # merged_two.drop()
        pass
    # result_frame.sort_values("freq", inplace=True, ascending=False)


if __name__ == "__main__":
    cli()