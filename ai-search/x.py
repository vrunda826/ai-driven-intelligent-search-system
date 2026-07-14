import numpy as np

emb = np.load("data/embeddings/embeddings.npy")
print("embeddings.npy")
print(emb.shape)
print(emb[0][:10])   # first embedding
print(emb[1][:10])   # second embedding

import pandas as pd
import faiss

index = faiss.read_index("data/indices/faiss.index")
print("faiss.index")
print(index.ntotal)
print(index.d)
df = pd.read_csv("data/embeddings/embedding_metadata.csv")
print("embeddings_metadata.csv")
print(df.iloc[0])
print(df.iloc[1])
print(df.iloc[2])

D, I = index.search(emb[0:1], 1)

print(I)

