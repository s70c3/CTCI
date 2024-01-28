import os
import matplotlib.pyplot as plt

import torch
from tqdm import tqdm

from transformers import ViTMAEForPreTraining, AutoImageProcessor

from src.vitmae.dataset import init_datasets, init_dataloaders


def save_model(model, path):
    torch.save(model.state_dict(), path)


def train(model, optimizer, train_dataloder, val_dataloader, device, save_dir, num_epochs=5):
    history = {"train": [], "val": []}

    for epoch in range(num_epochs):
        model = model.to(device)

        print(f"Epoch {epoch + 1}:")
        epoch_history = {"train": [], "val": []}

        model.train()
        for inputs in tqdm(train_dataloder):
            optimizer.zero_grad()

            inputs = inputs.to(device)
            batch_size, _, num_channels, height, width = inputs.data["pixel_values"].shape
            inputs.data["pixel_values"] = torch.reshape(inputs.data["pixel_values"],
                                                        (batch_size, num_channels, height, width))
            outputs = model(**inputs)

            loss = outputs.loss
            loss.backward()
            optimizer.step()

            history["train"].append(loss.item())
            epoch_history["train"].append(loss.item())

        epoch_train_loss = sum(epoch_history["train"]) / len(epoch_history["train"])
        print(f"Epoch train loss: {epoch_train_loss}")

        model.eval()
        for inputs in tqdm(val_dataloader):
            inputs = inputs.to(device)
            batch_size, _, num_channels, height, width = inputs.data["pixel_values"].shape
            inputs.data["pixel_values"] = torch.reshape(inputs.data["pixel_values"],
                                                        (batch_size, num_channels, height, width))
            outputs = model(**inputs)

            loss = outputs.loss

            history["val"].append(loss.item())
            epoch_history["val"].append(loss.item())

        epoch_val_loss = sum(epoch_history["val"]) / len(epoch_history["val"])
        print(f"Epoch val loss: {epoch_val_loss}\n")

        save_model(model.to("cpu"), path=os.path.join(save_dir, f"epoch_{epoch + 1}.pt"))

    return history


def draw_plot(history, save_dir=None):
    fig, ax = plt.subplots(nrows=1, ncols=2)
    fig.set_size_inches(18, 6)

    ax[0].plot(range(len(history["train"])), history["train"])
    ax[0].set_title("Train loss")
    ax[1].plot(range(len(history["val"])), history["val"])
    ax[1].set_title("Val loss")

    plt.show()
    if save_dir:
        fig.savefig(os.path.join(save_dir, "output.png"))


if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    image_processor_checkpoint = r"facebook/vit-mae-base"
    image_processor = AutoImageProcessor.from_pretrained(image_processor_checkpoint)

    # TODO: add argparser
    train_images_dir = r"C:\Internship\ITMO_ML\data\ViTMAE\train"
    val_images_dir = r"C:\Internship\ITMO_ML\data\ViTMAE\val"
    save_dir = r"C:\Internship\ITMO_ML\CTCI\checkpoints\vit\vitmae_on_bubbles\run2"

    batch_size_train = 64
    batch_size_val = 32
    pin_memory = True
    num_workers = 4

    train_dataset, val_dataset = init_datasets(
        train_images_dir=train_images_dir,
        val_images_dir=val_images_dir,
        image_processor=image_processor
    )

    train_dataloader, val_dataloader = init_dataloaders(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        batch_size_train=batch_size_train,
        batch_size_val=batch_size_val,
        pin_memory=pin_memory,
        num_workers=num_workers
    )

    model = ViTMAEForPreTraining.from_pretrained("facebook/vit-mae-base")
    optimizer = torch.optim.Adam(model.parameters())

    history = train(
        model=model,
        optimizer=optimizer,
        train_dataloder=train_dataloader,
        val_dataloader=val_dataloader,
        device=device,
        save_dir=save_dir,
        num_epochs=20
    )

    draw_plot(history=history, save_dir=save_dir)
