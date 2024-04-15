import torch

from transformers import Swinv2Model

from src.models.base_model import BaseModel
from src.models.unetr.decoder import UNETRDecoder
from src.models.loss.soft_dice_loss import SoftDiceLossV2
from src.models.utils.config import ConfigHandler


class Swin(BaseModel):
    def __init__(
            self, net, mask_head=None, loss_fn=None,
            image_size=(256, 256), device="cpu"
    ):
        super().__init__()

        self.device = device
        self.image_size = image_size
        self.net = net.encoder.to(self.device)

        if mask_head:
            self.mask_head = mask_head.to(self.device)
        else:
            self.mask_head = UNETRDecoder().to(self.device)

        if loss_fn:
            self.loss_fn = loss_fn.to(self.device)
        else:
            self.loss_fn = SoftDiceLossV2().to(self.device)

        self.embeddings = net.get_input_embeddings()

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        emb, input_dim = self.embeddings(image)
        out = self.net(
            hidden_states=emb,
            input_dimensions=input_dim,
            output_hidden_states=True
        )

        out = self.mask_head(
            reshaped_hidden_states=out.reshaped_hidden_states,
            image=image
        )
        return out

    def _calc_loss_fn(self, image: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return self.loss_fn(image, target)

    def train_on_batch(self, image: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        outputs = self.forward(image)
        loss = self._calc_loss_fn(outputs, target)
        return loss

    def val_on_batch(self, image: torch.Tensor, target: torch.Tensor) -> (torch.Tensor, torch.Tensor):
        outputs = self.forward(image)
        loss = self._calc_loss_fn(outputs, target)
        return loss, outputs

    def predict(self, image: torch.Tensor, conf=0.6) -> torch.Tensor:
        out = self.forward(image)
        out = torch.where(out > conf, 1, 0)
        return out

    def __str__(self):
        return "swin"


def build_swin(config_handler: ConfigHandler):
    device = config_handler.read('model', 'device')

    model_name = config_handler.read('model', 'model_name')
    model_type = config_handler.read('model', 'model_type')

    image_size_width = config_handler.read('dataset', 'image_size', 'width')
    image_size_height = config_handler.read('dataset', 'image_size', 'height')
    image_size = (image_size_width, image_size_height)

    net = Swinv2Model.from_pretrained(rf"microsoft/{model_name}-{model_type}")
    loss_fn = SoftDiceLossV2()
    decoder = UNETRDecoder()

    swin = Swin(
        net=net, mask_head=decoder, loss_fn=loss_fn,
        image_size=image_size, device=device
    )

    return swin
