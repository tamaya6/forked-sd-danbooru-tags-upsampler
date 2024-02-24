import random
import os

from transformers import set_seed

from dart.analyzer import DartAnalyzer
from dart.generator import DartGenerator
from dart.settings import parse_options

TOTAL_TAG_LENGTH = {
    "VERY_SHORT": "very short",
    "SHORT": "short",
    "LONG": "long",
    "VERY_LONG": "very long",
}

TOTAL_TAG_LENGTH_TAGS = {
    TOTAL_TAG_LENGTH["VERY_SHORT"]: "<|very_short|>",
    TOTAL_TAG_LENGTH["SHORT"]: "<|short|>",
    TOTAL_TAG_LENGTH["LONG"]: "<|long|>",
    TOTAL_TAG_LENGTH["VERY_LONG"]: "<|very_long|>",
}

PROCESSING_TIMING = {
    "BEFORE": "Before applying styles",
    "AFTER": "After applying styles",
}

SEED_MIN = 0
SEED_MAX = 2**32 - 1

# extension_dir = basedir()

extension_dir = os.path.dirname(os.path.realpath(__file__))

def get_random_seed():
    return random.randint(SEED_MIN, SEED_MAX)

class DanbooruTagUpsampler:
    generator: DartGenerator
    analyzer: DartAnalyzer

    def __init__(self):        

        opts = {}
        self.options = parse_options({})

        self.generator = DartGenerator(
            self.options["model_name"],
            self.options["tokenizer_name"],
            self.options["model_backend_type"],
        )

        self.analyzer = DartAnalyzer(
            extension_dir,
            self.generator.get_vocab_list(),
            self.generator.get_special_vocab_list(),
        )

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True, "multiline": True, "default": ""}),
                "tag_length": (["very short", "short", "long", "very long"], {"default": "long"}),
                "ban_tags": ("STRING", {"default": "official alternate costume, english text, animal focus", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295}),
            },
        }

    
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = "DanbooruTagUpsampler"


    def process(self, prompt, tag_length, ban_tags, seed):

        # prompts = [ x.strip() for x in prompt.split(',') ]
        prompts = [prompt]
        analyzing_results = [self.analyzer.analyze(p) for p in prompts]

        # print(f"""Your input contains:
        #         prompt: {prompts}
        #         seed: {seed}
        #         ban_tags: {ban_tags}
        #     """)

        upsample_prompts = [
            self.generator.compose_prompt(
                rating=f"{result.rating_parent}, {result.rating_child}",
                copyright=result.copyright,
                character=result.character,
                general=result.general,
                length=TOTAL_TAG_LENGTH_TAGS[tag_length],
            )
            for result in analyzing_results
        ]
        bad_words_ids = self.generator.get_bad_words_ids(ban_tags)

        # save the original seed
        # original_seed = seed if seed != -1 else get_random_seed()
        # seed = int(seed_num if seed_num != -1 else get_random_seed())

        set_seed(seed)
        print(upsample_prompts)
        generated_texts = self.generator.generate(
            upsample_prompts, bad_words_ids=bad_words_ids
        )
        # set_seed(original_seed)

        all_prompts = prompts

        all_prompts = [
            ", ".join(
                [part for part in [prompt, generated_texts[i]] if part.strip() != ""]
            )
            for i, prompt in enumerate(all_prompts)
        ]

        return all_prompts

