import click

from ml.ml_utils import (
    train_application_classification_cnn_model,
    train_traffic_classification_cnn_model,
)

from utils import ID_TO_TRAFFIC, ID_TO_APP


@click.command()
@click.option(
    "-d",
    "--data_path",
    help="training data dir path containing parquet files",
    required=True,
)
@click.option("-m", "--model_path", help="output model path", required=True)
@click.option(
    "-t",
    "--task",
    help='classification task. Option: "app" or "traffic"',
    required=True,
)
def main(data_path, model_path, task):
    if task == "app":
        train_application_classification_cnn_model(data_path, model_path, len(ID_TO_APP))
    elif task == "traffic":
        train_traffic_classification_cnn_model(data_path, model_path, len(ID_TO_TRAFFIC))
    else:
        exit("Not Support")


if __name__ == "__main__":
    main()
