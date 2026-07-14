import open_clip
import torch

from embedding.schemas import ModelBundle


class OpenCLIPLoader:

    def __init__(
        self,
        model_name: str,
        pretrained: str,
        device: torch.device,
    ):

        self.model_name = model_name

        self.pretrained = pretrained

        self.device = device

    def load(self) -> ModelBundle:

        model, _, preprocess = (
            open_clip.create_model_and_transforms(
                self.model_name,
                pretrained=self.pretrained,
            )
        )

        tokenizer = open_clip.get_tokenizer(
            self.model_name
        )

        model.to(self.device)

        model.eval()

        return ModelBundle(
            model=model,
            preprocess=preprocess,
            tokenizer=tokenizer,
        )