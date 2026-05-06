class UnionFind:
    def __init__(self):
        self.indices = {}
        self.n = 0
        self.rank = []
        self.parent = []
    
    def union(self, a, b) -> bool:
        a = self.find(a)
        b = self.find(b)

        if a == b:
            return False

        if self.rank[a] < self.rank[b]:
            self.parent[a] = b
        else:
            self.parent[b] = a
            if self.rank[a] == self.rank[b]:
                self.rank[a] += 1
        
        return True

    def find(self, a) -> int:
        a = self.indices[a]

        def _find(x) -> int:
            if x != self.parent[x]:
                self.parent[x] = _find(self.parent[x])
            
            return self.parent[x]

        return _find(a)

    def add(self, a) -> bool:
        if a in self.indices:
            return False
        
        self.indices[a] = self.n
        self.parent.append(self.n)
        self.rank.append(0)

        self.n += 1
        return True