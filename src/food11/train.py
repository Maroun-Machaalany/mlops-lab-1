import argparse
from pathlib import Path
from xml.parsers.expat import model

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


NUM_CLASSES = 11

DATASET_PATHS = {
    "processed": Path("data/food11_processed"),
    "mini": Path("data/food11_processed_mini"),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Train Food-11 with ResNet18")

    parser.add_argument(
        "--dataset",
        choices=["processed", "mini"],
        default="mini",
        help="Dataset to use: processed or mini",
    )
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)

    return parser.parse_args()


def create_dataloaders(dataset_name, batch_size):
    data_dir = DATASET_PATHS[dataset_name]

    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    train_dataset = datasets.ImageFolder(
        data_dir / "training",
        transform=transform,
    )

    val_dataset = datasets.ImageFolder(
        data_dir / "validation",
        transform=transform,
    )

    test_dataset = datasets.ImageFolder(
        data_dir / "evaluation",
        transform=transform,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    return train_loader, val_loader, test_loader


def create_model(device):
    weights = models.ResNet18_Weights.DEFAULT

    model = models.resnet18(weights=weights)

    model.fc = nn.Linear(
        model.fc.in_features,
        NUM_CLASSES,
    )

    model = model.to(device)

    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()

    total_loss = 0.0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        batch_size = images.size(0)
        total_loss += loss.item() * batch_size
        total_samples += batch_size

    return total_loss / total_samples


def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            batch_size = images.size(0)

            total_loss += loss.item() * batch_size
            total_samples += batch_size

            predictions = outputs.argmax(dim=1)
            total_correct += (predictions == labels).sum().item()

    average_loss = total_loss / total_samples
    accuracy = total_correct / total_samples

    return average_loss, accuracy


def main():
    args = parse_args()

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Using device: {device}")
    print(f"Dataset: {args.dataset}")

    train_loader, val_loader, test_loader = create_dataloaders(
        args.dataset,
        args.batch_size,
    )

    model = create_model(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    with mlflow.start_run():
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
            }
        )

        for epoch in range(args.epochs):
            train_loss = train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
            )

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )
            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )
            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_accuracy={val_accuracy:.4f}"
            )

        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        print(f"Test accuracy: {test_accuracy:.4f}")

    mlflow.pytorch.log_model(
    model,
    name="model",
    serialization_format="pickle",
)

if __name__ == "__main__":
    main()