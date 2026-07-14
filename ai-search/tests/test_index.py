import numpy as np

from src.search.faiss_builder import FAISSBuilder


def test_index_creation():

    embeddings = np.random.rand(
        100,
        512,
    ).astype(np.float32)

    embeddings /= np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    builder = FAISSBuilder(
        dimension=512,
    )

    index = builder.build(
        embeddings,
    )

    assert index.ntotal == 100