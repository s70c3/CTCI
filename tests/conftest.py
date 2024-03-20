import os.path as osp

import pytest
from torch.utils.data import DataLoader
from transformers import AutoImageProcessor

from src.features.segmentation.transformers_dataset import SegmentationDataset


@pytest.fixture(scope="session", autouse=True)
def train_bubbles_data_path():
    path = r"..\data\weakly_segmented\bubbles_split\train"
    return path


@pytest.fixture(scope="session", autouse=True)
def val_bubbles_data_path():
    path = r"..\data\weakly_segmented\bubbles_split\valid"
    return path


# TODO: датасет может быть не только с пузырями
@pytest.fixture(scope="session", autouse=True)
def train_dataset(train_bubbles_data_path):
    train_dataset = SegmentationDataset(
        images_dir=osp.join(train_bubbles_data_path, "images"),
        masks_dir=osp.join(train_bubbles_data_path, "masks")
    )
    return train_dataset


@pytest.fixture(scope="session", autouse=True)
def val_dataset(val_bubbles_data_path):
    val_dataset = SegmentationDataset(
        images_dir=osp.join(val_bubbles_data_path, "images"),
        masks_dir=osp.join(val_bubbles_data_path, "masks")
    )
    return val_dataset


@pytest.fixture(scope="session", autouse=True)
def train_dataloader(train_dataset):
    train_batch_size = 4
    pin_memory = False
    num_workers = 0
    train_dataloader = DataLoader(
        train_dataset, batch_size=train_batch_size, shuffle=True,
        pin_memory=pin_memory, num_workers=num_workers
    )
    return train_dataloader


@pytest.fixture(scope="session", autouse=True)
def val_dataloader(val_dataset):
    train_batch_size = 4
    pin_memory = False
    num_workers = 0
    val_dataloader = DataLoader(
        val_dataset, batch_size=train_batch_size, shuffle=False,
        pin_memory=pin_memory, num_workers=num_workers
    )
    return val_dataloader
