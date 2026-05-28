import hashlib


def hash_leaf(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash_node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(left + right).digest()


def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha256(b"").digest()

    nodes = [hash_leaf(leaf) for leaf in leaves]

    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])

        nodes = [
            hash_node(nodes[i], nodes[i + 1])
            for i in range(0, len(nodes), 2)
        ]

    return nodes[0]


def compute_merkle_root(data):
    if isinstance(data, dict):
        leaves = [str(v).encode() for v in data.values()]
    elif isinstance(data, list):
        leaves = [str(v).encode() for v in data]
    else:
        leaves = [str(data).encode()]

    return merkle_root(leaves).hex()