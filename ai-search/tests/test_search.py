import numpy as np

from src.search.faiss_builder import FAISSBuilder


def test_search():

    embeddings = np.random.rand(
        20,
        512,
    ).astype(np.float32)

    embeddings /= np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    builder = FAISSBuilder(
        512,
    )

    index = builder.build(
        embeddings,
    )

    query = embeddings[0:1]

    scores, indices = index.search(
        query,
        5,
    )

    assert indices.shape == (1, 5)