import sys
from pathlib import Path
import json

import click
from loguru import logger

from src.downloader import DataSet, Downloader
from src.database import Child, get_growth_table, build_growth_database
from src.plot import plot_subplot_growth_percentiles
from src.ingest_csv import huckleberry_reader, standardize_reader
from rich.table import Table
from rich.console import Console

@click.group(
        context_settings=dict(
            help_option_names=['-h', '--help'],
            max_content_width=120, 
            show_default=True) 
        )
def cli():
    pass

@cli.command('download')
@click.option('--output', '-o', default='data', help='The directory to save the downloaded WHO table t')
@click.option('--table-json', '-t', default='config/WHO_growth_tables.json', help='The json file containing the WHO growth tables')
def download(output: str = 'data', table_json: str = 'config/WHO_growth_tables.json' ):

    table_json = Path(table_json)
    if not table_json.exists():
        raise FileNotFoundError(f"File {table_json} not found")
    output = Path(output)
    if not output.exists():
        output.mkdir()


    with open(table_json, 'r') as f:
        data = json.load(f)
    datasets = [DataSet(**d) for d in data]
    downloader = Downloader(datasets)
    results = downloader.download_all()
    for dataset, result in results:
        if result.success:
            logger.success(f"Downloaded {dataset.filename}")
        else:
            logger.warning(f"Failed to download {dataset.filename}: {result.error}")

@cli.command('growth')
@click.option('--csv','-i',      required=True,  type=click.Path(exists=True), help='The input huckleburry csv file')
@click.option('--dob', '-d',     required=True, type=click.DateTime(['%Y-%m-%d']), help='The date of birth of the child ' )
@click.option('--gender', '-g',  required=True, type=click.Choice(['M','F']), help='Select gender of the child ["M", "F"]')
@click.option('--name', '-n',     default='child', help='Name of child for the output file')
@click.option('--savepath', '-s', default=Path.cwd(), help='Save path for the output file')
@click.option('--prefix', '-p',   default=None, help='The prefix of the output file')
@click.option('--huckleberry', '-hb', 'is_huckleberry',  is_flag=True, help='The input file is a huckleberry csv file')
@click.option('--verbose', '-v',  is_flag=True, help='Prints the dataframe to the console')
def growth(csv, dob, gender, name, savepath, prefix, verbose, is_huckleberry):
    child = Child(name,gender,  dob)
    growth_tables = build_growth_database()
    # growth_tables = get_growth_table()
    if prefix is None:
        prefix = child.name
    savepath = Path(savepath)
    if not savepath.exists():
        savepath.mkdir()
    if is_huckleberry:
        df = huckleberry_reader(csv, child, growth_tables).round(2)
        df.to_csv(savepath / f"{prefix}_huckleberry.csv", index=False)
    else:
        df = standardize_reader(csv, child, growth_tables).round(2)
        df.to_csv(savepath / f"{prefix}_standardized.csv", index=False)

    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    console = Console()
    table = Table()
    table.add_column("Date")
    table.add_column("Month")
    table.add_column("Weight (Kg)")
    table.add_column("Height (cm)")
    table.add_column("Head Circumference (cm)")
    table.add_column("BMI")
    for idx, row in df.iterrows():
        table.add_row(
            str(row['date'].date()), 
            f"{row['months']:.2f}",
            f"{row['weight_kg']:.2f} ({row['weight_percentile']:.1f}%)", 
            f"{row['height_cm']: .2f} ({row['height_percentile']:.1f}%)", 
            f"{row['hc_cm']: .2f} ({row['hc_percentile']:.1f}%)", 
            f"{row['bmi']: .2f} ({row['bmi_percentile']:.1f}%)"
            )
    console.print(table)

    plot_subplot_growth_percentiles(df, child, growth_tables, savepath/f'{prefix}.html')


if __name__ == "__main__":
    cli()