"""Independent binary-STL closure/component checks for exported joint specimens."""

from collections import Counter
from pathlib import Path
import struct
import sys


def check_stl(path):
    data = Path(path).read_bytes()
    if len(data) < 84:
        raise ValueError("STL is truncated")
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84+50*count or count == 0:
        raise ValueError("STL triangle count or length is invalid")
    edges, graph, volume = Counter(), {}, 0.0
    for offset in range(84, len(data), 50):
        values = struct.unpack_from("<12fH", data, offset)
        points = [tuple(values[i:i+3]) for i in (3, 6, 9)]
        a, b, c = points
        if len(set(points)) != 3:
            raise ValueError("STL has a degenerate triangle")
        volume += (a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])
                   +a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for left, right in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((left, right)))] += 1
            graph.setdefault(left, set()).add(right)
            graph.setdefault(right, set()).add(left)
    unseen, components = set(graph), 0
    while unseen:
        components += 1
        pending = [unseen.pop()]
        while pending:
            for point in graph[pending.pop()]:
                if point in unseen:
                    unseen.remove(point)
                    pending.append(point)
    return {"triangles": count, "components": components,
            "nonmanifold_edges": sum(n != 2 for n in edges.values()),
            "signed_volume_mm3": volume}


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    for name, components in (("prototype.stl", 2), ("parent.stl", 1), ("child.stl", 1)):
        report = check_stl(directory / name)
        assert report["components"] == components, (name, report)
        assert report["nonmanifold_edges"] == 0, (name, report)
        assert report["signed_volume_mm3"] > 0, (name, report)
        print(name, report)
