import logging

import time

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
from optimum.onnxruntime import ORTModelForCausalLM

# from modules.shared import opts

from dart.settings import MODEL_BACKEND_TYPE, parse_options
from dart.utils import escape_special_symbols

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DartGenerator:
    """A class for generating danbooru tags"""

    dart_model: PreTrainedModel | ORTModelForCausalLM | None = None
    dart_tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast | None = None

    def __init__(
        self,
        model_name: str,
        tokenizer_name: str,
        model_backend: str,
        model_device: str = "cpu",
    ):
        self.options = parse_options()

        self.model_name = model_name
        self.tokenizer_name = tokenizer_name

        assert model_backend in list(
            MODEL_BACKEND_TYPE.values()
        ), f"Unknown model type: {model_backend}"
        self.model_backend = model_backend
        self.model_device = model_device

        if self.options["debug_logging"]:
            logger.setLevel(logging.DEBUG)

        if self.options["debug_logging"]:
            logger.setLevel(logging.DEBUG)

    def _load_dart_model(
        self,
    ):
        if self.model_backend == MODEL_BACKEND_TYPE["ORIGINAL"]:
            self.dart_model = AutoModelForCausalLM.from_pretrained(self.model_name)
        else:
            self.dart_model = ORTModelForCausalLM.from_pretrained(
                self.model_name,
                file_name=(
                    "model_quantized.onnx"
                    if self.model_backend == MODEL_BACKEND_TYPE["ONNX_QUANTIZED"]
                    else None
                ),
            )
        logger.info(f"Dart model backend is {self.model_backend }")
        logger.info(f"Dart model backend is {self.model_backend }")

        assert self.dart_model is not None

        self.dart_model.to(self.model_device)  # type: ignore
        self.dart_model.to(self.model_device)  # type: ignore

    def _load_dart_tokenizer(self):
        self.dart_tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_name, trust_remote_code=True
        )

    def _check_model_avaiable(self):
        return self.dart_model is not None

    def _check_tokenizer_avaiable(self):
        return self.dart_tokenizer is not None

    def load_model_if_needed(self):
        if not self._check_model_avaiable():
            self._load_dart_model()

    def load_tokenizer_if_needed(self):
        if not self._check_tokenizer_avaiable():
            self._load_dart_tokenizer()

    def get_vocab_list(self) -> list[str]:
        self.load_tokenizer_if_needed()

        return list(self.dart_tokenizer.vocab.keys())  # type: ignore

    def get_special_vocab_list(self) -> list[str]:
        self.load_tokenizer_if_needed()

        return list(self.dart_tokenizer.get_added_vocab().values())  # type: ignore

    def compose_prompt(
        self, rating: str, copyright: str, character: str, general: str, length: str
    ):
        # self.load_tokenizer_if_needed()
        # assert self.dart_tokenizer is not None

        # sadly webui's transformers version is very old and apply_chat_template method deos not exist
        # return self.dart_tokenizer.apply_chat_template(
        #     {
        #         "rating": rating,
        #         "copyright": copyright,
        #         "character": character,
        #         "general": general,
        #         "length": length,
        #     },
        #     tokenize=True,
        # )

        return f"<|bos|><rating>{rating}</rating><copyright>{copyright}</copyright><character>{character}</character><general>{length}{general}<|input_end|>"

    def get_bad_words_ids(self, tag_text: str) -> list[list[int]] | None:
        if tag_text.strip() == "":
            return None

        self.load_tokenizer_if_needed()
        assert self.dart_tokenizer is not None

        bad_words_ids = self.dart_tokenizer.encode_plus(tag_text).input_ids
        return [[token] for token in bad_words_ids]

    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        min_new_tokens: int = 0,
        do_sample: bool = True,
        temperature: float = 1.0,
        top_p: float = 1,
        top_k: int = 20,
        num_beams: int = 1,
        bad_words_ids: list[list[int]] | None = None,
    ) -> str:
        """Upsamples prompt"""

    ) -> str:
        """Upsamples prompt"""

        start_time = time.time()

        self.load_tokenizer_if_needed()
        self.load_model_if_needed()

        assert self.dart_tokenizer is not None
        assert self.dart_model is not None

        input_ids = self.dart_tokenizer.encode_plus(
            prompt, return_tensors="pt"
        ).input_ids
        input_ids = self.dart_tokenizer.encode_plus(
            prompt, return_tensors="pt"
        ).input_ids

        # output_ids is list[list[int]]
        # output_ids is list[list[int]]
        output_ids = self.dart_model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            do_sample=do_sample,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_beams=num_beams,
            bad_words_ids=bad_words_ids,
            no_repeat_ngram_size=1,
        )

        decoded = self.dart_tokenizer.decode(
            output_ids[0][len(input_ids[0]) :],
            skip_special_tokens=True,
        decoded = self.dart_tokenizer.decode(
            output_ids[0][len(input_ids[0]) :],
            skip_special_tokens=True,
        )
        logger.debug(f"Generated tags: {decoded}")

        escaped = ", ".join(escape_special_symbols(decoded.split(", ")))
        logger.debug(f"Generated tags: {decoded}")

        escaped = ", ".join(escape_special_symbols(decoded.split(", ")))

        end_time = time.time()
        logger.info(f"Upsampling tags has taken {end_time-start_time:.2f} seconds")

        return escaped
        return escaped
