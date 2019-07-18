from typing import NamedTuple, Set

class Example(NamedTuple):
    x: str
    y: str
    z: str

p: Set = {
    Example("a", "b", "c"),
    Example("c", "b", "a")
}

q: Set = {
    Example("c", "b", "a"),
    Example("a", "b", "c")
}

print(p == q)
