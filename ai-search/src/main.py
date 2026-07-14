import argparse

from configs.config import Config
from core.device import DeviceManager
from core.logger import get_logger

from embedding.service import EmbeddingService
from embedding.model_loader import OpenCLIPLoader

from search.index_service import IndexService
from search.search_engine import SearchEngine
from search.schemas import (
    SearchRequest,
    FilterConfig,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(

        "mode",

        choices=[
            "embed",
            "build-index",
            "search",
        ],

    )

    parser.add_argument(

        "query",

        nargs="?",

        default=None,

    )

    args = parser.parse_args()

    config = Config()

    logger = get_logger(

        "main",

        config.get("paths","log_dir"),)

    device = DeviceManager.get_device()

    logger.info(
        f"Using Device : {device}"
    )
    if args.mode in ("embed", "search"):
        bundle = OpenCLIPLoader(
            model_name=config.get("model", "name"),
            pretrained=config.get("model", "pretrained"),
            device=device,
        ).load()
        if args.mode == "embed":

            service = EmbeddingService(
                config=config,
                bundle=bundle,
                device=device,
                logger=logger,
            )

            service.run()
        elif args.mode == "search":

            if args.query is None:

                raise ValueError(
                    "Search query missing."
                )

            engine = SearchEngine(
                config=config,
                bundle=bundle,
                device=device,
            )

            request = SearchRequest(
                query=args.query,
                top_k=config.get(
                    "search",
                    "top_k",
                ),
                filters=FilterConfig(class_name="car",),)

            results = engine.search(
                request
            )

            print("\nSearch Results")
            print("=" * 80)

            for i, result in enumerate(results, start=1):

                print(f"\n[{i}]")

                print(
                    f"Track ID   : {result.track_id}"
                )

                print(
                    f"Camera     : {result.camera_id}"
                )

                print(
                    f"Class      : {result.class_name}"
                )

                print(
                    f"Similarity : {result.similarity_score:.4f}"
                )

                print(
                    f"Time       : "
                    f"{result.first_seen_time}"
                    " -> "
                    f"{result.last_seen_time}"
                )

                print(
                    f"Description: {result.description}"
                )

            print("\nTotal Results :", len(results))


    elif args.mode == "build-index":

        service = IndexService(
            config=config,
        )

        service.run()

    

if __name__ == "__main__":

    main()