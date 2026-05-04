import os
print(os.environ.get("CONDA_PREFIX"))

import pathlib

import torch.nn as nn
import numpy as np
import lightning.pytorch as pl

# Force working directory to the script's folder
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
os.chdir(SCRIPT_DIR)

import torch

from torch.utils.data import DataLoader
import torchvision

from monai.networks.nets import UNet, DynUNet
from monai.losses import TverskyLoss

class EyeBVSegm(pl.LightningModule):
    def __init__(self,
                 model,
                 num_classes: int,
                 ):
        super().__init__()

        self.model = model
        self.num_classes = num_classes
        self.val_img_was_vis = False
        self.Twersky = TverskyLoss(include_background=True, sigmoid=True,
                                    alpha=0.3, beta=0.7, reduction="mean",
                                      smooth_nr=1.0, smooth_dr=1.0, batch=True)

    def forward(self, x):
        return self.model(x)

    def _calculate_loss(self, batch):
        img, mask = batch

        out = self(img)

        loss = self.Twersky(out, mask)
        index_out = (torch.sigmoid(out)>0.5).float()

        return loss, index_out, out#, logs, out, index_out # passing model output for visualization


    def training_step(self, batch):
        loss, index_out, out = self._calculate_loss(batch) #, logs, out, index_out

        #self.log_dict(
        #    {f"Train/{k}": v for k, v in logs.items()}, on_step=True, on_epoch=False
        #)
        self.log('train_loss', loss, prog_bar=True)

        return loss

    def validation_step(self, batch):
        loss,index_out,out = self._calculate_loss(batch) #logs, out, index_out

        if not self.val_img_was_vis:
            img, mask = batch
            self.val_img_was_vis = True


        return loss

    def test_step(self, batch):
        loss, logs, out, index_out = self._calculate_loss(batch, mode="test")

        if not self.test_img_was_vis:
            img, mask = batch
            self.test_img_was_vis = True

        return loss

    def on_validation_end(self):
        # set val visualization flag to False so that we will visualize again during the next validation phase
        self.val_img_was_vis = False

    def configure_optimizers(self):
        optim = torch.optim.Adam(self.parameters(), lr=1e-3)

        return  optim



