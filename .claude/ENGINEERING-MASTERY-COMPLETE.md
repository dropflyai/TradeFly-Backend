# ENGINEERING MASTERY: The Complete Guide to Scientist-Level Software Engineering

## Table of Contents

1. [Foundational Computer Science](#part-1-foundational-computer-science)
2. [Software Design Principles](#part-2-software-design-principles)
3. [Distributed Systems](#part-3-distributed-systems)
4. [Debugging & Problem Solving](#part-4-debugging--problem-solving)
5. [Testing Methodologies](#part-5-testing-methodologies)
6. [System Architecture](#part-6-system-architecture)
7. [Performance & Scalability](#part-7-performance--scalability)
8. [Security Principles](#part-8-security-principles)
9. [DevOps & Deployment](#part-9-devops--deployment)
10. [Engineering Judgment](#part-10-engineering-judgment)
11. [Web Application Fundamentals](#part-11-web-application-fundamentals)
12. [Database Theory](#part-12-database-theory)
13. [Code Quality](#part-13-code-quality)
14. [Mental Models for Engineers](#part-14-mental-models-for-engineers)
15. [Real-World Application](#part-15-real-world-application)

---

# PART 1: FOUNDATIONAL COMPUTER SCIENCE

## 1.1 Algorithms & Data Structures

### Why This Matters

Understanding algorithms and data structures is the difference between writing code that works and writing code that works efficiently at scale. A poorly chosen data structure can turn an O(1) operation into O(n), causing a 10ms operation to become 10 seconds when data grows. This knowledge allows you to:

- Predict how your code will perform before deployment
- Choose the right tool for the job
- Communicate complexity trade-offs with your team
- Debug performance issues systematically

### Core Data Structures

#### 1.1.1 Arrays

**Definition**: Contiguous memory allocation storing elements of the same type.

**Time Complexity**:
- Access: O(1)
- Search: O(n)
- Insertion: O(n) (requires shifting)
- Deletion: O(n) (requires shifting)
- Append: O(1) amortized

**Space Complexity**: O(n)

**When to Use**:
- When you need constant-time access by index
- When the size is relatively fixed or predictable
- When cache locality matters (arrays are cache-friendly)

**When to Avoid**:
- When frequent insertions/deletions in the middle are needed
- When size is highly dynamic and unpredictable

**Real-World Example**:
```javascript
// Bad: Using array for frequent insertions
const eventLog = [];
for (let i = 0; i < 1000000; i++) {
  eventLog.unshift(newEvent); // O(n) operation each time!
}

// Good: Use appropriate structure for the access pattern
const eventLog = new LinkedList(); // O(1) prepend
// Or use circular buffer if size is bounded
```

**Pitfalls**:
- Forgetting about resize cost (when dynamic arrays grow)
- Not considering memory fragmentation
- Ignoring cache line effects in hot paths

#### 1.1.2 Linked Lists

**Definition**: Nodes connected via pointers, allowing dynamic size.

**Types**:
- Singly Linked: Each node points to next
- Doubly Linked: Each node points to next and previous
- Circular: Last node points back to first

**Time Complexity**:
- Access: O(n)
- Search: O(n)
- Insertion (at head): O(1)
- Insertion (at position): O(n) to find position
- Deletion (with reference): O(1)
- Deletion (by value): O(n)

**Space Complexity**: O(n) + pointer overhead

**When to Use**:
- Frequent insertions/deletions at known positions
- When you don't need random access
- Implementing stacks, queues, or LRU caches

**When to Avoid**:
- When random access is primary operation
- When memory overhead of pointers is significant
- When cache locality is critical

**Real-World Example**:
```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class LRUCache:
    """Using doubly linked list for O(1) removal from middle"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> node
        self.head = Node(0)  # dummy
        self.tail = Node(0)  # dummy
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """O(1) removal because we have prev/next pointers"""
        prev, nxt = node.prev, node.next
        prev.next, nxt.prev = nxt, prev

    def _add_to_head(self, node):
        """O(1) insertion at head"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
```

**Pitfalls**:
- Forgetting to update both pointers in doubly-linked lists
- Memory leaks from circular references (in languages without GC)
- Cache misses due to non-contiguous memory

#### 1.1.3 Hash Tables

**Definition**: Data structure using hash function to map keys to values.

**Time Complexity** (average case):
- Insert: O(1)
- Delete: O(1)
- Search: O(1)

**Time Complexity** (worst case):
- All operations: O(n) when all keys collide

**Space Complexity**: O(n) plus overhead for empty buckets

**Load Factor**: n/m where n = elements, m = buckets
- Typically resize when load factor > 0.75

**Collision Resolution Strategies**:

1. **Chaining**: Each bucket contains a linked list
   - Pros: Simple, no clustering
   - Cons: Extra memory for pointers, cache unfriendly

2. **Open Addressing**: Find next available slot
   - Linear Probing: Check next slot linearly
   - Quadratic Probing: Check slots at quadratic intervals
   - Double Hashing: Use second hash function

**When to Use**:
- Need fast lookups by key
- Keys are hashable and well-distributed
- Set operations (membership testing)

**When to Avoid**:
- Need ordering of keys
- Memory is extremely constrained
- Hash function causes many collisions

**Real-World Example**:
```java
// Database connection pooling using hash table
public class ConnectionPool {
    private Map<String, Connection> activeConnections;
    private Map<String, Long> lastAccessTime;

    public Connection getConnection(String userId) {
        // O(1) lookup instead of O(n) search through array
        Connection conn = activeConnections.get(userId);
        if (conn == null || !conn.isValid()) {
            conn = createNewConnection(userId);
            activeConnections.put(userId, conn);
        }
        lastAccessTime.put(userId, System.currentTimeMillis());
        return conn;
    }

    // Evict stale connections
    public void evictStale() {
        long now = System.currentTimeMillis();
        // O(n) but only done periodically
        activeConnections.keySet().removeIf(key ->
            now - lastAccessTime.get(key) > TIMEOUT
        );
    }
}
```

**Hash Function Properties**:
- Deterministic: Same input always gives same output
- Uniform distribution: Minimize collisions
- Fast to compute: Should be O(1)
- Avalanche effect: Small input change causes large hash change

**Common Pitfalls**:
```javascript
// Bad: Using mutable objects as keys
const map = new Map();
const key = { id: 1 };
map.set(key, "value");
key.id = 2; // Mutated key!
map.get(key); // May not find value due to rehashing

// Good: Use immutable keys
const map = new Map();
const key = "user:1"; // Immutable string
map.set(key, "value");
```

#### 1.1.4 Trees

##### Binary Trees

**Definition**: Each node has at most two children (left and right).

**Properties**:
- Height: Longest path from root to leaf
- Balanced: Height is O(log n)
- Complete: All levels filled except possibly last
- Full: Every node has 0 or 2 children
- Perfect: All interior nodes have 2 children, all leaves at same level

**Time Complexity** (balanced):
- Search: O(log n)
- Insert: O(log n)
- Delete: O(log n)

**Time Complexity** (unbalanced/degenerate):
- All operations: O(n)

##### Binary Search Trees (BST)

**Invariant**: For each node, all left descendants < node < all right descendants

**Implementation**:
```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def insert(root, val):
    """O(log n) average, O(n) worst case"""
    if not root:
        return TreeNode(val)

    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)

    return root

def search(root, val):
    """Binary search on tree"""
    if not root or root.val == val:
        return root

    if val < root.val:
        return search(root.left, val)
    return search(root.right, val)
```

**Traversals**:

1. **In-Order** (Left, Root, Right): Gives sorted order for BST
```python
def inorder(root):
    if not root:
        return
    inorder(root.left)
    print(root.val)
    inorder(root.right)
```

2. **Pre-Order** (Root, Left, Right): Used for tree copying
```python
def preorder(root):
    if not root:
        return
    print(root.val)
    preorder(root.left)
    preorder(root.right)
```

3. **Post-Order** (Left, Right, Root): Used for tree deletion
```python
def postorder(root):
    if not root:
        return
    postorder(root.left)
    postorder(root.right)
    print(root.val)
```

4. **Level-Order** (Breadth-First): Layer by layer
```python
from collections import deque

def levelorder(root):
    if not root:
        return

    queue = deque([root])
    while queue:
        node = queue.popleft()
        print(node.val)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
```

##### AVL Trees

**Definition**: Self-balancing BST where heights of left and right subtrees differ by at most 1.

**Balance Factor**: height(left) - height(right) must be in {-1, 0, 1}

**Rotations**:
```python
def rotate_right(y):
    """Right rotation to fix left-heavy tree
         y                x
        / \              / \
       x   C    -->     A   y
      / \                  / \
     A   B                B   C
    """
    x = y.left
    B = x.right

    # Perform rotation
    x.right = y
    y.left = B

    # Update heights
    y.height = 1 + max(height(y.left), height(y.right))
    x.height = 1 + max(height(x.left), height(x.right))

    return x

def rotate_left(x):
    """Left rotation to fix right-heavy tree"""
    y = x.right
    B = y.left

    y.left = x
    x.right = B

    x.height = 1 + max(height(x.left), height(x.right))
    y.height = 1 + max(height(y.left), height(y.right))

    return y
```

**Time Complexity**: O(log n) guaranteed for all operations

**When to Use**: When you need guaranteed O(log n) performance

##### Red-Black Trees

**Properties**:
1. Every node is red or black
2. Root is black
3. All leaves (NIL) are black
4. Red node has black children (no two reds in a row)
5. All paths from node to descendants have same number of black nodes

**Time Complexity**: O(log n) guaranteed

**Comparison with AVL**:
- AVL: More rigidly balanced, faster lookups, slower insertions
- Red-Black: Less rigidly balanced, faster insertions, slightly slower lookups
- Red-Black used in: Java TreeMap, C++ std::map, Linux kernel

##### B-Trees

**Definition**: Self-balancing tree optimized for systems that read/write large blocks of data (databases, filesystems).

**Properties**:
- Each node can have multiple keys (not just 1 like BST)
- Node has m keys -> m+1 children
- All leaves at same level
- Minimum degree t: Each node has at least t-1 keys (except root)

**Time Complexity**: O(log n) but with different base (higher than 2)

**Why Databases Use B-Trees**:
```
Disk access is expensive (milliseconds)
Memory access is fast (nanoseconds)

B-Tree with degree 1000:
- Each node has up to 999 keys
- Each disk read gets 999 keys instead of 1
- Height is log₁₀₀₀(n) instead of log₂(n)
- For 1 billion records: log₁₀₀₀(10⁹) = 3 disk reads!
```

**Real-World Example**:
```sql
-- PostgreSQL uses B-Tree for indexes
CREATE INDEX idx_user_email ON users(email);

-- When you search:
SELECT * FROM users WHERE email = 'user@example.com';

-- PostgreSQL traverses B-Tree:
-- 1. Read root node (1 disk access)
-- 2. Read intermediate node (1 disk access)
-- 3. Read leaf node (1 disk access)
-- Total: 3 disk accesses for millions of records!
```

##### Tries (Prefix Trees)

**Definition**: Tree where each path from root represents a string, used for prefix matching.

**Structure**:
```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """O(m) where m is word length"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        """O(m) where m is word length"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        """O(m) where m is prefix length"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
```

**Time Complexity**:
- Insert: O(m) where m is string length
- Search: O(m)
- Space: O(ALPHABET_SIZE * m * n) in worst case

**Use Cases**:
- Autocomplete systems
- Spell checkers
- IP routing tables (longest prefix match)
- Dictionary implementations

**Real-World Example**:
```javascript
// Autocomplete system
class Autocomplete {
    constructor() {
        this.trie = new Trie();
    }

    addWord(word) {
        this.trie.insert(word.toLowerCase());
    }

    getSuggestions(prefix, limit = 10) {
        // Find node for prefix - O(m)
        let node = this.trie.root;
        for (let char of prefix.toLowerCase()) {
            if (!node.children[char]) return [];
            node = node.children[char];
        }

        // DFS to collect all words with this prefix
        const results = [];
        this._dfs(node, prefix, results, limit);
        return results;
    }

    _dfs(node, path, results, limit) {
        if (results.length >= limit) return;

        if (node.is_end_of_word) {
            results.push(path);
        }

        for (let [char, childNode] of Object.entries(node.children)) {
            this._dfs(childNode, path + char, results, limit);
        }
    }
}

// Usage in search bar
const autocomplete = new Autocomplete();
autocomplete.addWord("apple");
autocomplete.addWord("application");
autocomplete.addWord("apply");

console.log(autocomplete.getSuggestions("app"));
// ["apple", "application", "apply"]
```

#### 1.1.5 Heaps

**Definition**: Complete binary tree where each node is greater/less than its children.

**Types**:
- Max Heap: Parent >= children
- Min Heap: Parent <= children

**Time Complexity**:
- Insert: O(log n)
- Extract Min/Max: O(log n)
- Peek Min/Max: O(1)
- Build Heap: O(n) (not O(n log n)!)

**Implementation Using Array**:
```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, val):
        """O(log n) - add to end and bubble up"""
        self.heap.append(val)
        self._bubble_up(len(self.heap) - 1)

    def _bubble_up(self, i):
        while i > 0 and self.heap[i] < self.heap[self.parent(i)]:
            self.swap(i, self.parent(i))
            i = self.parent(i)

    def extract_min(self):
        """O(log n) - remove root, replace with last, bubble down"""
        if not self.heap:
            return None

        min_val = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heap.pop()

        if self.heap:
            self._bubble_down(0)

        return min_val

    def _bubble_down(self, i):
        min_index = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < len(self.heap) and self.heap[left] < self.heap[min_index]:
            min_index = left

        if right < len(self.heap) and self.heap[right] < self.heap[min_index]:
            min_index = right

        if min_index != i:
            self.swap(i, min_index)
            self._bubble_down(min_index)

    def peek(self):
        """O(1)"""
        return self.heap[0] if self.heap else None
```

**Use Cases**:
- Priority queues
- Heap sort
- Finding k largest/smallest elements
- Median maintenance

**Real-World Example - Task Scheduler**:
```python
class Task:
    def __init__(self, name, priority, deadline):
        self.name = name
        self.priority = priority
        self.deadline = deadline

    def __lt__(self, other):
        # Higher priority first, then earlier deadline
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.deadline < other.deadline

class TaskScheduler:
    def __init__(self):
        self.tasks = []  # Min heap (using heapq)

    def add_task(self, task):
        """O(log n)"""
        heapq.heappush(self.tasks, task)

    def get_next_task(self):
        """O(log n)"""
        if self.tasks:
            return heapq.heappop(self.tasks)
        return None

    def peek_next_task(self):
        """O(1)"""
        return self.tasks[0] if self.tasks else None

# Usage
scheduler = TaskScheduler()
scheduler.add_task(Task("Fix bug", priority=5, deadline="2025-01-15"))
scheduler.add_task(Task("Review PR", priority=3, deadline="2025-01-14"))
scheduler.add_task(Task("Write docs", priority=2, deadline="2025-01-20"))

next_task = scheduler.get_next_task()  # Gets "Fix bug" (highest priority)
```

#### 1.1.6 Graphs

**Definition**: Set of vertices (nodes) connected by edges.

**Types**:
- Directed vs Undirected
- Weighted vs Unweighted
- Cyclic vs Acyclic (DAG)
- Connected vs Disconnected

**Representations**:

1. **Adjacency Matrix**: 2D array where matrix[i][j] = weight of edge
   - Space: O(V²)
   - Check if edge exists: O(1)
   - Find all neighbors: O(V)
   - Good for dense graphs

2. **Adjacency List**: Array of lists, where list[i] = neighbors of vertex i
   - Space: O(V + E)
   - Check if edge exists: O(degree)
   - Find all neighbors: O(degree)
   - Good for sparse graphs

**Implementation**:
```python
class Graph:
    def __init__(self, directed=False):
        self.graph = {}  # adjacency list
        self.directed = directed

    def add_vertex(self, v):
        if v not in self.graph:
            self.graph[v] = []

    def add_edge(self, u, v, weight=1):
        self.add_vertex(u)
        self.add_vertex(v)

        self.graph[u].append((v, weight))

        if not self.directed:
            self.graph[v].append((u, weight))

    def get_neighbors(self, v):
        return self.graph.get(v, [])
```

**Graph Traversal Algorithms**:

##### Breadth-First Search (BFS)

**Use Cases**:
- Shortest path in unweighted graph
- Level-order traversal
- Finding connected components

**Time Complexity**: O(V + E)
**Space Complexity**: O(V) for queue

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        vertex = queue.popleft()
        print(vertex)

        for neighbor, _ in graph.get_neighbors(vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

def shortest_path_bfs(graph, start, end):
    """Find shortest path in unweighted graph"""
    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        vertex, path = queue.popleft()

        if vertex == end:
            return path

        for neighbor, _ in graph.get_neighbors(vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None  # No path found
```

##### Depth-First Search (DFS)

**Use Cases**:
- Cycle detection
- Topological sort
- Finding strongly connected components
- Maze solving

**Time Complexity**: O(V + E)
**Space Complexity**: O(V) for recursion stack

```python
def dfs_recursive(graph, vertex, visited=None):
    if visited is None:
        visited = set()

    visited.add(vertex)
    print(vertex)

    for neighbor, _ in graph.get_neighbors(vertex):
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)

    return visited

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]

    while stack:
        vertex = stack.pop()

        if vertex not in visited:
            visited.add(vertex)
            print(vertex)

            for neighbor, _ in graph.get_neighbors(vertex):
                if neighbor not in visited:
                    stack.append(neighbor)

    return visited

def has_cycle_directed(graph):
    """Detect cycle in directed graph using DFS"""
    visited = set()
    rec_stack = set()  # Recursion stack for current path

    def dfs(vertex):
        visited.add(vertex)
        rec_stack.add(vertex)

        for neighbor, _ in graph.get_neighbors(vertex):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True  # Back edge found!

        rec_stack.remove(vertex)
        return False

    for vertex in graph.graph:
        if vertex not in visited:
            if dfs(vertex):
                return True

    return False
```

##### Dijkstra's Algorithm

**Use Case**: Shortest path in weighted graph with non-negative weights

**Time Complexity**: O((V + E) log V) with min heap

```python
import heapq

def dijkstra(graph, start):
    """Find shortest paths from start to all vertices"""
    distances = {vertex: float('infinity') for vertex in graph.graph}
    distances[start] = 0

    # Min heap: (distance, vertex)
    pq = [(0, start)]
    visited = set()

    while pq:
        current_distance, current_vertex = heapq.heappop(pq)

        if current_vertex in visited:
            continue

        visited.add(current_vertex)

        for neighbor, weight in graph.get_neighbors(current_vertex):
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))

    return distances

def dijkstra_with_path(graph, start, end):
    """Find shortest path and distance"""
    distances = {vertex: float('infinity') for vertex in graph.graph}
    distances[start] = 0
    previous = {vertex: None for vertex in graph.graph}

    pq = [(0, start)]
    visited = set()

    while pq:
        current_distance, current_vertex = heapq.heappop(pq)

        if current_vertex == end:
            break

        if current_vertex in visited:
            continue

        visited.add(current_vertex)

        for neighbor, weight in graph.get_neighbors(current_vertex):
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))

    # Reconstruct path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return distances[end], path if path[0] == start else None
```

**Real-World Example - Route Planning**:
```python
class RouteMap:
    def __init__(self):
        self.graph = Graph(directed=False)

    def add_road(self, city1, city2, distance_km):
        self.graph.add_edge(city1, city2, distance_km)

    def find_shortest_route(self, start_city, end_city):
        distance, path = dijkstra_with_path(
            self.graph, start_city, end_city
        )
        return {
            'distance_km': distance,
            'route': path,
            'cities': len(path)
        }

# Usage
route_map = RouteMap()
route_map.add_road("New York", "Boston", 215)
route_map.add_road("New York", "Philadelphia", 95)
route_map.add_road("Philadelphia", "Boston", 310)

result = route_map.find_shortest_route("New York", "Boston")
# Returns shortest route through Philadelphia or direct
```

##### Bellman-Ford Algorithm

**Use Case**: Shortest path with negative weights (detects negative cycles)

**Time Complexity**: O(VE)

```python
def bellman_ford(graph, start):
    """Shortest paths with negative weights"""
    distances = {vertex: float('infinity') for vertex in graph.graph}
    distances[start] = 0

    # Relax edges V-1 times
    for _ in range(len(graph.graph) - 1):
        for vertex in graph.graph:
            for neighbor, weight in graph.get_neighbors(vertex):
                if distances[vertex] + weight < distances[neighbor]:
                    distances[neighbor] = distances[vertex] + weight

    # Check for negative cycles
    for vertex in graph.graph:
        for neighbor, weight in graph.get_neighbors(vertex):
            if distances[vertex] + weight < distances[neighbor]:
                raise ValueError("Graph contains negative cycle")

    return distances
```

##### A* Algorithm

**Use Case**: Shortest path with heuristic (game AI, pathfinding)

**Time Complexity**: Depends on heuristic quality

```python
def a_star(graph, start, goal, heuristic):
    """
    heuristic(node, goal) must be admissible (never overestimate)
    Example: Euclidean distance for grid-based pathfinding
    """
    open_set = [(0, start)]  # (f_score, vertex)
    came_from = {}

    g_score = {vertex: float('infinity') for vertex in graph.graph}
    g_score[start] = 0

    f_score = {vertex: float('infinity') for vertex in graph.graph}
    f_score[start] = heuristic(start, goal)

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor, weight in graph.get_neighbors(current):
            tentative_g_score = g_score[current] + weight

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found
```

**Topological Sort**:

**Use Case**: Dependency resolution, task scheduling

**Requirement**: DAG (Directed Acyclic Graph)

```python
def topological_sort_dfs(graph):
    """DFS-based topological sort"""
    visited = set()
    stack = []

    def dfs(vertex):
        visited.add(vertex)
        for neighbor, _ in graph.get_neighbors(vertex):
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(vertex)

    for vertex in graph.graph:
        if vertex not in visited:
            dfs(vertex)

    return stack[::-1]

def topological_sort_kahn(graph):
    """Kahn's algorithm (BFS-based)"""
    # Calculate in-degree
    in_degree = {vertex: 0 for vertex in graph.graph}
    for vertex in graph.graph:
        for neighbor, _ in graph.get_neighbors(vertex):
            in_degree[neighbor] += 1

    # Queue of vertices with no incoming edges
    queue = deque([v for v in graph.graph if in_degree[v] == 0])
    result = []

    while queue:
        vertex = queue.popleft()
        result.append(vertex)

        for neighbor, _ in graph.get_neighbors(vertex):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph.graph):
        raise ValueError("Graph has cycle")

    return result
```

**Real-World Example - Build System**:
```python
class BuildSystem:
    def __init__(self):
        self.dependencies = Graph(directed=True)

    def add_dependency(self, target, dependency):
        """target depends on dependency"""
        self.dependencies.add_edge(dependency, target)

    def get_build_order(self):
        """Returns order to build targets"""
        try:
            return topological_sort_kahn(self.dependencies)
        except ValueError:
            raise ValueError("Circular dependency detected!")

# Usage
build = BuildSystem()
build.add_dependency("app", "core")
build.add_dependency("app", "utils")
build.add_dependency("core", "utils")
build.add_dependency("tests", "app")

order = build.get_build_order()
# ["utils", "core", "app", "tests"]
```

### 1.2 Algorithm Design Techniques

#### 1.2.1 Divide and Conquer

**Pattern**: Split problem into smaller subproblems, solve recursively, combine results.

**Template**:
```python
def divide_and_conquer(problem):
    if is_base_case(problem):
        return solve_directly(problem)

    subproblems = split(problem)
    sub_solutions = [divide_and_conquer(sub) for sub in subproblems]
    return combine(sub_solutions)
```

**Examples**:

##### Merge Sort

**Time Complexity**: O(n log n)
**Space Complexity**: O(n)

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    # Divide
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    # Conquer (merge)
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

##### Quick Sort

**Time Complexity**: O(n log n) average, O(n²) worst case
**Space Complexity**: O(log n) for recursion

```python
def quick_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        # Partition
        pivot_index = partition(arr, low, high)

        # Sort left and right
        quick_sort(arr, low, pivot_index - 1)
        quick_sort(arr, pivot_index + 1, high)

    return arr

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

**When to Use Each**:
- Merge Sort: Stable sort needed, linked lists, external sorting
- Quick Sort: In-place sorting, average case performance critical

#### 1.2.2 Dynamic Programming

**Key Insight**: Store solutions to subproblems to avoid recomputation.

**When to Apply**:
1. Optimal substructure: Optimal solution contains optimal solutions to subproblems
2. Overlapping subproblems: Same subproblems solved multiple times

**Approaches**:
1. **Top-Down (Memoization)**: Start with original problem, cache results
2. **Bottom-Up (Tabulation)**: Solve smallest subproblems first, build up

##### Fibonacci

**Naive Recursion** - O(2ⁿ):
```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n-1) + fib_naive(n-2)
```

**Top-Down DP** - O(n):
```python
def fib_memo(n, memo=None):
    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]
```

**Bottom-Up DP** - O(n):
```python
def fib_dp(n):
    if n <= 1:
        return n

    dp = [0] * (n + 1)
    dp[1] = 1

    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]

    return dp[n]
```

**Space-Optimized** - O(1):
```python
def fib_optimized(n):
    if n <= 1:
        return n

    prev2, prev1 = 0, 1

    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current

    return prev1
```

##### Longest Common Subsequence (LCS)

**Problem**: Find longest subsequence common to two sequences.

**Time Complexity**: O(mn)
**Space Complexity**: O(mn)

```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)

    # dp[i][j] = LCS length of text1[0:i] and text2[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]

def lcs_with_string(text1, text2):
    """Return actual LCS string"""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Backtrack to find string
    result = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i-1] == text2[j-1]:
            result.append(text1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1

    return ''.join(reversed(result))
```

##### Knapsack Problem

**0/1 Knapsack**: Each item can be taken 0 or 1 times

```python
def knapsack_01(weights, values, capacity):
    n = len(weights)

    # dp[i][w] = max value using items 0..i with capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i-1][w]

            # Take item i-1 if it fits
            if weights[i-1] <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )

    return dp[n][capacity]

# Space-optimized version - O(capacity) space
def knapsack_01_optimized(weights, values, capacity):
    dp = [0] * (capacity + 1)

    for i in range(len(weights)):
        # Iterate backwards to avoid using updated values
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])

    return dp[capacity]
```

**Real-World Example - Resource Allocation**:
```python
class ResourceAllocator:
    """Allocate limited resources to projects for maximum value"""

    def __init__(self, budget):
        self.budget = budget

    def allocate(self, projects):
        """
        projects = [{'name': str, 'cost': int, 'value': int}, ...]
        Returns: list of projects to fund
        """
        costs = [p['cost'] for p in projects]
        values = [p['value'] for p in projects]

        n = len(projects)
        dp = [[0] * (self.budget + 1) for _ in range(n + 1)]

        # Fill DP table
        for i in range(1, n + 1):
            for b in range(self.budget + 1):
                dp[i][b] = dp[i-1][b]
                if costs[i-1] <= b:
                    dp[i][b] = max(
                        dp[i][b],
                        dp[i-1][b - costs[i-1]] + values[i-1]
                    )

        # Backtrack to find which projects to fund
        funded = []
        i, b = n, self.budget
        while i > 0 and b > 0:
            if dp[i][b] != dp[i-1][b]:
                funded.append(projects[i-1])
                b -= costs[i-1]
            i -= 1

        return {
            'projects': funded,
            'total_cost': sum(p['cost'] for p in funded),
            'total_value': sum(p['value'] for p in funded)
        }

# Usage
allocator = ResourceAllocator(budget=1000000)
projects = [
    {'name': 'Project A', 'cost': 400000, 'value': 500},
    {'name': 'Project B', 'cost': 300000, 'value': 400},
    {'name': 'Project C', 'cost': 500000, 'value': 600},
    {'name': 'Project D', 'cost': 200000, 'value': 250}
]
result = allocator.allocate(projects)
```

##### Edit Distance (Levenshtein Distance)

**Problem**: Minimum operations to transform one string to another

**Operations**: Insert, delete, replace (each cost = 1)

```python
def edit_distance(word1, word2):
    m, n = len(word1), len(word2)

    # dp[i][j] = edit distance of word1[0:i] and word2[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases
    for i in range(m + 1):
        dp[i][0] = i  # Delete all characters
    for j in range(n + 1):
        dp[0][j] = j  # Insert all characters

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],     # Delete from word1
                    dp[i][j-1],     # Insert to word1
                    dp[i-1][j-1]    # Replace in word1
                )

    return dp[m][n]
```

**Real-World Use**: Spell checking, fuzzy string matching, DNA sequence alignment

#### 1.2.3 Greedy Algorithms

**Pattern**: Make locally optimal choice at each step.

**When It Works**: When local optimum leads to global optimum (greedy choice property).

##### Activity Selection

**Problem**: Select maximum number of non-overlapping activities.

```python
def activity_selection(activities):
    """
    activities = [(start, end), ...]
    Returns: maximum number of non-overlapping activities
    """
    # Sort by end time (greedy choice)
    activities.sort(key=lambda x: x[1])

    selected = [activities[0]]
    last_end = activities[0][1]

    for start, end in activities[1:]:
        if start >= last_end:  # Non-overlapping
            selected.append((start, end))
            last_end = end

    return selected
```

**Proof of Correctness**: By choosing activity that ends earliest, we maximize room for future activities.

##### Huffman Coding

**Problem**: Optimal prefix-free encoding for data compression.

```python
import heapq
from collections import Counter

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def huffman_coding(text):
    """Generate Huffman codes for characters"""
    # Count frequencies
    freq = Counter(text)

    # Create leaf nodes
    heap = [HuffmanNode(char, f) for char, f in freq.items()]
    heapq.heapify(heap)

    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    # Generate codes
    root = heap[0]
    codes = {}

    def generate_codes(node, code=""):
        if node.char is not None:  # Leaf node
            codes[node.char] = code
            return

        generate_codes(node.left, code + "0")
        generate_codes(node.right, code + "1")

    generate_codes(root)
    return codes

# Example
text = "this is an example for huffman encoding"
codes = huffman_coding(text)
# {'t': '1110', 'h': '1010', 'i': '100', 's': '101', ...}

# Calculate compression ratio
original_bits = len(text) * 8  # ASCII = 8 bits per char
encoded_bits = sum(len(codes[c]) for c in text)
compression_ratio = 1 - (encoded_bits / original_bits)
print(f"Compression: {compression_ratio:.1%}")
```

#### 1.2.4 Backtracking

**Pattern**: Incrementally build candidates, abandon when constraints violated.

##### N-Queens Problem

```python
def solve_n_queens(n):
    """Place n queens on n×n board so none attack each other"""
    def is_safe(board, row, col):
        # Check column
        for i in range(row):
            if board[i] == col:
                return False

        # Check diagonal
        for i in range(row):
            if abs(board[i] - col) == abs(i - row):
                return False

        return True

    def backtrack(board, row):
        if row == n:
            solutions.append(board[:])
            return

        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(board, row + 1)
                board[row] = -1  # Backtrack

    solutions = []
    backtrack([-1] * n, 0)
    return solutions

# Visualize solution
def print_board(board):
    n = len(board)
    for row in range(n):
        line = ['Q' if board[row] == col else '.' for col in range(n)]
        print(' '.join(line))
    print()

solutions = solve_n_queens(8)
print(f"Found {len(solutions)} solutions")
print_board(solutions[0])
```

##### Sudoku Solver

```python
def solve_sudoku(board):
    """Solve 9×9 Sudoku puzzle"""
    def is_valid(board, row, col, num):
        # Check row
        if num in board[row]:
            return False

        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False

        # Check 3×3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False

        return True

    def backtrack():
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num

                            if backtrack():
                                return True

                            board[row][col] = 0  # Backtrack

                    return False
        return True

    backtrack()
    return board
```

### 1.3 Complexity Theory

#### 1.3.1 P vs NP

**Class P**: Problems solvable in polynomial time O(n^k).

Examples:
- Sorting: O(n log n)
- Shortest path: O(V log V + E)
- Matrix multiplication: O(n^2.37) (Coppersmith-Winograd)

**Class NP**: Problems where solutions are verifiable in polynomial time.

Examples:
- Boolean satisfiability (SAT)
- Hamiltonian path
- Traveling salesman problem
- Subset sum

**P = NP Question**: Can every problem whose solution is verifiable in polynomial time also be solvable in polynomial time?

**Why It Matters**:
- Most important open problem in computer science
- $1 million Clay Mathematics prize
- Would revolutionize cryptography, optimization, AI

**NP-Complete**: Hardest problems in NP. If one is solvable in P, all NP problems are.

**Cook-Levin Theorem**: SAT is NP-complete.

**NP-Hard**: At least as hard as hardest NP problems (may not be in NP).

**Practical Implications**:
```python
# Recognizing NP-complete problems prevents wasted effort

def has_hamiltonian_path(graph):
    """NP-complete - no known polynomial algorithm"""
    # Don't try to solve optimally for large graphs!
    # Use approximations or heuristics instead
    pass

# Instead, use approximations:
def approximate_tsp(graph):
    """2-approximation for metric TSP"""
    # Use minimum spanning tree heuristic
    mst = minimum_spanning_tree(graph)
    tour = dfs_preorder(mst)
    return tour
```

#### 1.3.2 Big O Analysis

**Notation**:
- O (Big O): Upper bound (worst case)
- Ω (Omega): Lower bound (best case)
- Θ (Theta): Tight bound (average case)

**Growth Rates** (from slowest to fastest):
```
O(1)         < O(log n)    < O(√n)       < O(n)        < O(n log n)
constant       logarithmic   square root   linear        linearithmic

< O(n²)      < O(n³)       < O(2ⁿ)       < O(n!)       < O(nⁿ)
quadratic      cubic         exponential   factorial     exponential
```

**Visualization**:
```
For n = 100:
O(1):        1 operation
O(log n):    ~7 operations
O(n):        100 operations
O(n log n):  ~700 operations
O(n²):       10,000 operations
O(2ⁿ):       1,267,650,600,228,229,401,496,703,205,376 operations (infeasible!)
```

**Rules**:

1. **Drop constants**: O(2n) = O(n)
2. **Drop non-dominant terms**: O(n² + n) = O(n²)
3. **Different inputs use different variables**: O(a + b), O(a * b)

**Common Mistakes**:
```python
# Mistake: Assuming O(n) + O(n) = O(2n) = O(n)
# Correct when operations are sequential

def process(arr):
    for x in arr:  # O(n)
        print(x)

    for x in arr:  # O(n)
        print(x * 2)

    # Total: O(n) + O(n) = O(n)

# Mistake: Not recognizing nested dependencies
def nested_problem(arr):
    for i in range(len(arr)):          # O(n)
        for j in range(i, len(arr)):   # O(n)
            print(arr[i], arr[j])

    # Total: O(n²) not O(n)!

# Mistake: Not accounting for hidden operations
def tricky(arr):
    result = []
    for x in arr:
        result = result + [x]  # List concatenation is O(n)!

    # Total: O(n²) not O(n)

    # Fix: Use append which is O(1)
    for x in arr:
        result.append(x)  # Now O(n)
```

**Amortized Analysis**:

Dynamic array append is O(1) amortized even though resizing is O(n):

```python
class DynamicArray:
    def __init__(self):
        self.array = [None] * 1
        self.size = 0
        self.capacity = 1

    def append(self, val):
        if self.size == self.capacity:
            self._resize()  # O(n) but rare

        self.array[self.size] = val
        self.size += 1

    def _resize(self):
        self.capacity *= 2
        new_array = [None] * self.capacity
        for i in range(self.size):
            new_array[i] = self.array[i]
        self.array = new_array

# Analysis:
# Insertions: 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
# Resizes at: 1, 2, 4, 8, 16, ...
#
# Total cost for n insertions:
# n + (1 + 2 + 4 + 8 + ... + n/2) = n + (2n - 1) = 3n - 1
#
# Amortized cost per insertion: (3n - 1) / n ≈ 3 = O(1)
```

**Space Complexity**:

Don't forget to analyze space usage:

```python
def recursive_sum(arr):
    """
    Time: O(n)
    Space: O(n) due to call stack
    """
    if not arr:
        return 0
    return arr[0] + recursive_sum(arr[1:])

def iterative_sum(arr):
    """
    Time: O(n)
    Space: O(1) - much better!
    """
    total = 0
    for x in arr:
        total += x
    return total
```

### 1.4 Memory Management

#### 1.4.1 Memory Hierarchy

```
                  Speed    Size      Cost/GB
Registers         0.25ns   <1KB      -
L1 Cache          1ns      64KB      -
L2 Cache          4ns      256KB     -
L3 Cache          10ns     8MB       -
RAM               100ns    16GB      $5
SSD               100μs    1TB       $0.10
HDD               10ms     4TB       $0.02
```

**Implications**:
- Cache misses are expensive (100x slower than cache hits)
- Data locality matters
- Sequential access >> Random access

**Cache-Friendly Code**:
```c
// Bad: Column-major access (cache misses)
int sum = 0;
for (int col = 0; col < N; col++) {
    for (int row = 0; row < N; row++) {
        sum += matrix[row][col];  // Jumps around memory
    }
}

// Good: Row-major access (cache friendly)
int sum = 0;
for (int row = 0; row < N; row++) {
    for (int col = 0; col < N; col++) {
        sum += matrix[row][col];  // Sequential memory access
    }
}

// For 10000×10000 matrix:
// Bad: ~30 seconds
// Good: ~0.2 seconds (150x faster!)
```

#### 1.4.2 Stack vs Heap

**Stack**:
- Automatic memory management
- LIFO allocation
- Fast allocation/deallocation (just move stack pointer)
- Limited size (typically 1-8MB)
- Local variables, function call frames

**Heap**:
- Manual/GC memory management
- Unordered allocation
- Slower allocation (search for free block)
- Large size (gigabytes)
- Dynamic data structures, objects

```c
void example() {
    int x = 5;              // Stack - automatic
    int arr[100];           // Stack - fixed size

    int* ptr = malloc(100 * sizeof(int));  // Heap - dynamic
    // Must free!
    free(ptr);
}
```

**Stack Overflow**:
```python
def infinite_recursion(n):
    return infinite_recursion(n + 1)  # Stack overflow!

infinite_recursion(0)
# RecursionError: maximum recursion depth exceeded
```

**Solution**: Convert to iteration or use tail recursion optimization (if supported).

#### 1.4.3 Garbage Collection

**Reference Counting**:
- Track number of references to each object
- Free when count reaches zero
- Problem: Circular references cause memory leaks

```python
# Python uses reference counting + cycle detection

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

# Circular reference
a = Node(1)
b = Node(2)
a.next = b
b.next = a  # Cycle!

# Python's cycle detector will eventually clean this up
# But reference counting alone wouldn't
```

**Mark and Sweep**:
1. Mark phase: Traverse from roots, mark reachable objects
2. Sweep phase: Free unmarked objects

**Generational GC**:
- Observation: Most objects die young
- Separate young and old generations
- Collect young generation frequently
- Collect old generation rarely

```
Generation 0 (Young): Collected every few MB allocated
Generation 1 (Middle): Collected every 10 collections of Gen 0
Generation 2 (Old): Collected every 10 collections of Gen 1
```

**GC Pauses**:
- Stop-the-world: Application paused during GC
- Concurrent: GC runs alongside application
- Incremental: GC work spread over time

**Reducing GC Pressure**:
```javascript
// Bad: Creates many short-lived objects
function processData(items) {
    return items.map(item => ({
        ...item,
        processed: true
    }));  // New object for each item
}

// Better: Reuse objects when possible
function processData(items) {
    for (let item of items) {
        item.processed = true;  // Mutate in place
    }
    return items;
}

// Best: Object pooling for frequently created objects
class ObjectPool {
    constructor(factory, size) {
        this.pool = Array(size).fill(null).map(factory);
        this.available = [...this.pool];
    }

    acquire() {
        return this.available.pop() || factory();
    }

    release(obj) {
        obj.reset();  // Clear state
        this.available.push(obj);
    }
}
```

**Memory Leaks in GC Languages**:

Even with GC, leaks possible:

```javascript
// Leak: Event listeners not removed
class Component {
    constructor() {
        document.addEventListener('click', this.onClick.bind(this));
        // Memory leak: listener holds reference to component forever
    }

    destroy() {
        // Forgot to remove listener!
    }
}

// Fix: Remove listeners
class Component {
    constructor() {
        this.handleClick = this.onClick.bind(this);
        document.addEventListener('click', this.handleClick);
    }

    destroy() {
        document.removeEventListener('click', this.handleClick);
    }
}

// Leak: Closures capturing large objects
function createClosure() {
    const largeArray = new Array(1000000);

    return function() {
        // Only need length, but captures entire array!
        console.log(largeArray.length);
    };
}

// Fix: Only capture what's needed
function createClosure() {
    const length = new Array(1000000).length;

    return function() {
        console.log(length);
    };
}
```

### 1.5 Compilers & Interpreters

#### 1.5.1 Compilation Pipeline

```
Source Code
    ↓
Lexical Analysis (Lexer/Scanner)
    ↓ Tokens
Syntax Analysis (Parser)
    ↓ Abstract Syntax Tree (AST)
Semantic Analysis
    ↓ Annotated AST
Intermediate Representation (IR)
    ↓
Optimization
    ↓ Optimized IR
Code Generation
    ↓
Machine Code
```

**Lexical Analysis**:

Converts source code to tokens.

```python
# Example: Lexer for simple calculator
import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def tokenize(code):
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal
        ('PLUS',     r'\+'),           # Addition
        ('MINUS',    r'-'),            # Subtraction
        ('TIMES',    r'\*'),           # Multiplication
        ('DIVIDE',   r'/'),            # Division
        ('LPAREN',   r'\('),           # Left parenthesis
        ('RPAREN',   r'\)'),           # Right parenthesis
        ('SKIP',     r'[ \t]+'),       # Skip whitespace
        ('MISMATCH', r'.'),            # Any other character
    ]

    tok_regex = '|'.join(f'(?P<{name}>{pattern})'
                         for name, pattern in token_specification)

    tokens = []
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()

        if kind == 'NUMBER':
            value = float(value)
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character: {value}')

        tokens.append(Token(kind, value))

    return tokens

# Example
tokens = tokenize("3 + 4 * (2 - 1)")
# [Token(NUMBER, 3.0), Token(PLUS, '+'), Token(NUMBER, 4.0), ...]
```

**Parsing**:

Builds Abstract Syntax Tree from tokens.

```python
# Recursive descent parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.expr()

    def expr(self):
        """expr: term ((PLUS|MINUS) term)*"""
        node = self.term()

        while self.current() and self.current().type in ['PLUS', 'MINUS']:
            op = self.current()
            self.advance()
            right = self.term()
            node = BinOp(node, op, right)

        return node

    def term(self):
        """term: factor ((TIMES|DIVIDE) factor)*"""
        node = self.factor()

        while self.current() and self.current().type in ['TIMES', 'DIVIDE']:
            op = self.current()
            self.advance()
            right = self.factor()
            node = BinOp(node, op, right)

        return node

    def factor(self):
        """factor: NUMBER | LPAREN expr RPAREN"""
        token = self.current()

        if token.type == 'NUMBER':
            self.advance()
            return Number(token.value)
        elif token.type == 'LPAREN':
            self.advance()
            node = self.expr()
            self.expect('RPAREN')
            return node

        raise SyntaxError(f'Unexpected token: {token}')

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        if not self.current() or self.current().type != token_type:
            raise SyntaxError(f'Expected {token_type}')
        self.advance()

# AST Nodes
class Number:
    def __init__(self, value):
        self.value = value

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
```

**Interpreter** (Tree-Walking):

```python
def evaluate(node):
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)

        if node.op.type == 'PLUS':
            return left + right
        elif node.op.type == 'MINUS':
            return left - right
        elif node.op.type == 'TIMES':
            return left * right
        elif node.op.type == 'DIVIDE':
            return left / right

# Full pipeline
code = "3 + 4 * (2 - 1)"
tokens = tokenize(code)
ast = Parser(tokens).parse()
result = evaluate(ast)
print(result)  # 7.0
```

#### 1.5.2 Optimization Techniques

**Constant Folding**:
```python
# Before: x = 2 + 3 * 4
# After:  x = 14
```

**Dead Code Elimination**:
```python
# Before:
if False:
    x = expensive_function()

# After:
# (removed entirely)
```

**Common Subexpression Elimination**:
```python
# Before:
a = b * c + g
d = b * c * e

# After:
temp = b * c
a = temp + g
d = temp * e
```

**Loop Invariant Code Motion**:
```python
# Before:
for i in range(n):
    x = y * z  # y and z don't change
    arr[i] = x + i

# After:
x = y * z
for i in range(n):
    arr[i] = x + i
```

**Inlining**:
```python
# Before:
def add(a, b):
    return a + b

x = add(3, 4)

# After:
x = 3 + 4  # Function call overhead eliminated
```

#### 1.5.3 JIT Compilation

**Just-In-Time Compilation**: Compile code during execution, not before.

**Advantages**:
- Profile-guided optimization (optimize hot paths)
- Adaptive optimization (recompile with better data)
- Platform-specific optimizations

**Example: V8 (JavaScript Engine)**:

```
Source Code
    ↓
Parser → AST
    ↓
Ignition (Interpreter) ← Executes code, profiles
    ↓
TurboFan (JIT Compiler) ← Compiles hot functions
    ↓
Optimized Machine Code
```

**De-optimization**:

If assumptions fail, fall back to interpreter:

```javascript
function add(a, b) {
    return a + b;
}

// Initially compiled assuming integers
add(1, 2);  // Fast path: integer addition
add(3, 4);
add(5, 6);

// Type assumption violated
add("hello", "world");  // Deoptimize! Back to slow path
```

**Writing JIT-Friendly Code**:

```javascript
// Bad: Type instability
function process(x) {
    if (typeof x === 'number') {
        return x * 2;
    }
    return x.toString();
}

// JIT must generate code for both paths, can't optimize

// Good: Type stability
function processNumber(x) {
    return x * 2;
}

function processString(x) {
    return x.toString();
}

// Each function optimized for its type

// Bad: Polymorphic call site
for (let item of mixedArray) {
    process(item);  // Different types each iteration
}

// Good: Monomorphic call site
for (let num of numbers) {
    processNumber(num);  // Same type always
}
```

---

# PART 2: SOFTWARE DESIGN PRINCIPLES

## 2.1 SOLID Principles

### 2.1.1 Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

**Why It Matters**:
- Reduces coupling
- Improves testability
- Easier to understand and maintain
- Changes are localized

**Violation Example**:
```java
// BAD: Multiple responsibilities
public class Employee {
    private String name;
    private String email;

    // Responsibility 1: Business logic
    public double calculatePay() {
        // Complex payroll calculation
    }

    // Responsibility 2: Database access
    public void save() {
        // SQL queries to save employee
    }

    // Responsibility 3: Report generation
    public String generateReport() {
        // HTML generation
    }
}
```

**Problems**:
- Changes to payroll logic affect database code
- Report format changes affect business logic
- Hard to test in isolation
- Multiple teams stepping on each other's toes

**Fixed Example**:
```java
// GOOD: Single responsibility per class

// Responsibility 1: Business logic
public class Employee {
    private String name;
    private String email;

    public double calculatePay() {
        // Calculation only
    }
}

// Responsibility 2: Database access
public class EmployeeRepository {
    public void save(Employee employee) {
        // Database operations
    }

    public Employee findById(String id) {
        // Query database
    }
}

// Responsibility 3: Report generation
public class EmployeeReportGenerator {
    public String generateReport(Employee employee) {
        // HTML generation
    }
}
```

**Real-World Example**:
```typescript
// BAD: User service doing too much
class UserService {
    async createUser(userData: UserData) {
        // Validation
        if (!userData.email.includes('@')) {
            throw new Error('Invalid email');
        }

        // Password hashing
        const hashedPassword = await bcrypt.hash(userData.password, 10);

        // Database
        const user = await db.users.insert({
            ...userData,
            password: hashedPassword
        });

        // Email
        await sendGrid.send({
            to: userData.email,
            subject: 'Welcome!',
            body: 'Thanks for signing up'
        });

        // Analytics
        await analytics.track('user_created', {
            userId: user.id
        });

        return user;
    }
}

// GOOD: Separated concerns
class UserValidator {
    validate(userData: UserData): ValidationResult {
        if (!userData.email.includes('@')) {
            return { valid: false, errors: ['Invalid email'] };
        }
        return { valid: true };
    }
}

class PasswordHasher {
    async hash(password: string): Promise<string> {
        return bcrypt.hash(password, 10);
    }
}

class UserRepository {
    async create(userData: UserData): Promise<User> {
        return db.users.insert(userData);
    }
}

class WelcomeEmailSender {
    async send(user: User): Promise<void> {
        await sendGrid.send({
            to: user.email,
            subject: 'Welcome!',
            body: 'Thanks for signing up'
        });
    }
}

class UserAnalytics {
    trackCreation(user: User): void {
        analytics.track('user_created', { userId: user.id });
    }
}

// Orchestrator that coordinates
class CreateUserUseCase {
    constructor(
        private validator: UserValidator,
        private hasher: PasswordHasher,
        private repository: UserRepository,
        private emailSender: WelcomeEmailSender,
        private analytics: UserAnalytics
    ) {}

    async execute(userData: UserData): Promise<User> {
        // Validate
        const validation = this.validator.validate(userData);
        if (!validation.valid) {
            throw new ValidationError(validation.errors);
        }

        // Hash password
        const hashedPassword = await this.hasher.hash(userData.password);

        // Create user
        const user = await this.repository.create({
            ...userData,
            password: hashedPassword
        });

        // Send email (don't wait)
        this.emailSender.send(user).catch(err =>
            logger.error('Email failed', err)
        );

        // Track analytics
        this.analytics.trackCreation(user);

        return user;
    }
}
```

**Benefits of Refactoring**:
- Each class easily testable in isolation
- Can swap implementations (e.g., different email provider)
- Changes localized (validation logic changes don't affect database)
- Can run operations in parallel or async easily

### 2.1.2 Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension, closed for modification.

**Translation**: Add new functionality without changing existing code.

**Why It Matters**:
- Reduces risk of breaking existing features
- Supports plugin architectures
- Enables parallel development

**Violation Example**:
```python
# BAD: Must modify class to add new shape
class AreaCalculator:
    def calculate(self, shapes):
        total = 0
        for shape in shapes:
            if shape['type'] == 'circle':
                total += 3.14 * shape['radius'] ** 2
            elif shape['type'] == 'rectangle':
                total += shape['width'] * shape['height']
            # Adding triangle requires modifying this code!
        return total
```

**Fixed Example**:
```python
# GOOD: Extend via polymorphism
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self) -> float:
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Triangle(Shape):  # Adding new shape doesn't modify existing code
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height

class AreaCalculator:
    def calculate(self, shapes: list[Shape]) -> float:
        return sum(shape.area() for shape in shapes)
```

**Real-World Example: Payment Processing**:
```typescript
// BAD: Must modify PaymentProcessor for each payment method
class PaymentProcessor {
    process(amount: number, method: string, details: any) {
        if (method === 'credit_card') {
            // Stripe integration
            stripe.charge({
                amount,
                source: details.token
            });
        } else if (method === 'paypal') {
            // PayPal integration
            paypal.createPayment({
                amount,
                email: details.email
            });
        } else if (method === 'bank_transfer') {
            // Bank API
            // ...
        }
        // Adding cryptocurrency requires modifying this class!
    }
}

// GOOD: Open for extension
interface PaymentMethod {
    charge(amount: number): Promise<PaymentResult>;
}

class CreditCardPayment implements PaymentMethod {
    constructor(private token: string) {}

    async charge(amount: number): Promise<PaymentResult> {
        return stripe.charge({
            amount,
            source: this.token
        });
    }
}

class PayPalPayment implements PaymentMethod {
    constructor(private email: string) {}

    async charge(amount: number): Promise<PaymentResult> {
        return paypal.createPayment({
            amount,
            email: this.email
        });
    }
}

// Add new payment method without modifying existing code
class CryptoPayment implements PaymentMethod {
    constructor(private walletAddress: string) {}

    async charge(amount: number): Promise<PaymentResult> {
        return cryptoGateway.transfer({
            amount,
            to: this.walletAddress
        });
    }
}

class PaymentProcessor {
    async process(amount: number, method: PaymentMethod): Promise<PaymentResult> {
        return method.charge(amount);
    }
}

// Usage
const processor = new PaymentProcessor();
await processor.process(100, new CreditCardPayment('tok_123'));
await processor.process(100, new PayPalPayment('user@example.com'));
await processor.process(100, new CryptoPayment('0x123...'));
```

**Strategy Pattern** (OCP in Action):
```javascript
// Logging example
class Logger {
    constructor(strategy) {
        this.strategy = strategy;
    }

    log(message) {
        this.strategy.write(message);
    }
}

class ConsoleLogStrategy {
    write(message) {
        console.log(message);
    }
}

class FileLogStrategy {
    write(message) {
        fs.appendFileSync('log.txt', message + '\n');
    }
}

class RemoteLogStrategy {
    write(message) {
        fetch('/api/logs', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }
}

// Can add new strategies without modifying Logger
const logger = new Logger(new ConsoleLogStrategy());
logger.log('Hello');

// Switch strategy at runtime
logger.strategy = new FileLogStrategy();
logger.log('World');
```

### 2.1.3 Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without breaking the program.

**Translation**: Derived classes must not break contracts established by base classes.

**Why It Matters**:
- Enables polymorphism
- Prevents subtle bugs from inheritance
- Maintains behavioral consistency

**Violation Example**:
```python
# BAD: Square violates Rectangle's contract
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def set_width(self, width):
        self._width = width

    def set_height(self, height):
        self._height = height

    def area(self):
        return self._width * self._height

class Square(Rectangle):
    def set_width(self, width):
        self._width = width
        self._height = width  # Breaks Rectangle contract!

    def set_height(self, height):
        self._width = height  # Breaks Rectangle contract!
        self._height = height

# This breaks!
def test_rectangle(rect):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20  # Fails for Square!

test_rectangle(Rectangle(0, 0))  # Passes
test_rectangle(Square(0, 0))     # Fails! area() == 16
```

**Problem**: Square changes behavior in unexpected way. Client code expecting Rectangle behavior gets broken.

**Fixed Example**:
```python
# GOOD: Separate hierarchies
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def set_width(self, width):
        self._width = width

    def set_height(self, height):
        self._height = height

    def area(self):
        return self._width * self._height

class Square(Shape):
    def __init__(self, side):
        self._side = side

    def set_side(self, side):
        self._side = side

    def area(self):
        return self._side ** 2

# No inheritance relationship, no broken contracts
```

**Real-World Example: Birds**:
```java
// BAD: Violates LSP
public class Bird {
    public void fly() {
        // Flying logic
    }
}

public class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Penguins can't fly!");
    }
}

// Code expecting any Bird to fly breaks with Penguin
public void makeBirdFly(Bird bird) {
    bird.fly();  // Exception if bird is a Penguin!
}

// GOOD: Separate capabilities
public interface Bird {
    void eat();
    void makeSound();
}

public interface FlyingBird extends Bird {
    void fly();
}

public interface SwimmingBird extends Bird {
    void swim();
}

public class Eagle implements FlyingBird {
    public void fly() { /* ... */ }
    public void eat() { /* ... */ }
    public void makeSound() { /* ... */ }
}

public class Penguin implements SwimmingBird {
    public void swim() { /* ... */ }
    public void eat() { /* ... */ }
    public void makeSound() { /* ... */ }
}

// Type system prevents mistakes
public void makeBirdFly(FlyingBird bird) {
    bird.fly();  // Only accepts birds that can fly
}
```

**Preconditions and Postconditions**:

LSP requires:
- Preconditions cannot be strengthened in subtype
- Postconditions cannot be weakened in subtype
- Invariants must be preserved

```typescript
// BAD: Strengthening precondition
class User {
    // Accepts any string
    setEmail(email: string) {
        this.email = email;
    }
}

class PremiumUser extends User {
    // Requires verified email (stronger precondition)
    setEmail(email: string) {
        if (!this.isVerified(email)) {
            throw new Error('Email must be verified');
        }
        this.email = email;
    }
}

// Code expecting User breaks with PremiumUser
function updateUser(user: User) {
    user.setEmail('any@email.com');  // Works for User, fails for PremiumUser
}

// GOOD: Honor base contract
class User {
    setEmail(email: string) {
        this.email = email;
    }
}

class PremiumUser extends User {
    setEmail(email: string) {
        // Still accepts any email (same precondition)
        this.email = email;

        // Additional behavior is okay
        if (!this.isVerified(email)) {
            this.sendVerificationEmail();
        }
    }
}
```

### 2.1.4 Interface Segregation Principle (ISP)

**Definition**: Clients should not depend on interfaces they don't use.

**Translation**: Many specific interfaces are better than one general-purpose interface.

**Why It Matters**:
- Reduces coupling
- Prevents fat interfaces
- Improves understandability
- Enables precise contracts

**Violation Example**:
```java
// BAD: Fat interface forces unnecessary implementations
public interface Worker {
    void work();
    void eat();
    void sleep();
}

public class HumanWorker implements Worker {
    public void work() { /* ... */ }
    public void eat() { /* ... */ }
    public void sleep() { /* ... */ }
}

public class RobotWorker implements Worker {
    public void work() { /* ... */ }

    // Robots don't eat or sleep!
    public void eat() {
        throw new UnsupportedOperationException();
    }

    public void sleep() {
        throw new UnsupportedOperationException();
    }
}
```

**Fixed Example**:
```java
// GOOD: Segregated interfaces
public interface Workable {
    void work();
}

public interface Eatable {
    void eat();
}

public interface Sleepable {
    void sleep();
}

public class HumanWorker implements Workable, Eatable, Sleepable {
    public void work() { /* ... */ }
    public void eat() { /* ... */ }
    public void sleep() { /* ... */ }
}

public class RobotWorker implements Workable {
    public void work() { /* ... */ }
    // No need to implement eat/sleep
}
```

**Real-World Example: Printer Interface**:
```typescript
// BAD: All-in-one printer interface
interface Printer {
    print(document: Document): void;
    scan(document: Document): Document;
    fax(document: Document, number: string): void;
    staple(document: Document): void;
}

class SimplePrinter implements Printer {
    print(document: Document) { /* ... */ }

    // Simple printer can't do these!
    scan(document: Document) {
        throw new Error('Not supported');
    }

    fax(document: Document, number: string) {
        throw new Error('Not supported');
    }

    staple(document: Document) {
        throw new Error('Not supported');
    }
}

// GOOD: Segregated interfaces
interface Printable {
    print(document: Document): void;
}

interface Scannable {
    scan(document: Document): Document;
}

interface Faxable {
    fax(document: Document, number: string): void;
}

interface Stapleable {
    staple(document: Document): void;
}

class SimplePrinter implements Printable {
    print(document: Document) { /* ... */ }
}

class MultiFunctionPrinter implements Printable, Scannable, Faxable, Stapleable {
    print(document: Document) { /* ... */ }
    scan(document: Document) { /* ... */ }
    fax(document: Document, number: string) { /* ... */ }
    staple(document: Document) { /* ... */ }
}

// Usage: Client depends only on what it needs
class PrintService {
    constructor(private printer: Printable) {}

    printDocument(doc: Document) {
        this.printer.print(doc);
        // Doesn't need scan/fax/staple
    }
}
```

**Database Example**:
```python
# BAD: Fat repository interface
class Repository:
    def find_by_id(self, id): pass
    def find_all(self): pass
    def save(self, entity): pass
    def delete(self, entity): pass
    def find_by_email(self, email): pass
    def find_by_age_range(self, min, max): pass
    def find_active(self): pass
    # ... 20 more methods

class ReadOnlyService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def get_user(self, id):
        # Only uses find_by_id, but forced to depend on entire interface
        return self.repo.find_by_id(id)

# GOOD: Segregated repositories
class ReadableRepository:
    def find_by_id(self, id): pass
    def find_all(self): pass

class WritableRepository:
    def save(self, entity): pass
    def delete(self, entity): pass

class UserSearchRepository:
    def find_by_email(self, email): pass
    def find_by_age_range(self, min, max): pass
    def find_active(self): pass

class ReadOnlyService:
    def __init__(self, repo: ReadableRepository):
        self.repo = repo

    def get_user(self, id):
        return self.repo.find_by_id(id)

class UserCreationService:
    def __init__(self, repo: WritableRepository):
        self.repo = repo

    def create_user(self, user):
        return self.repo.save(user)
```

### 2.1.5 Dependency Inversion Principle (DIP)

**Definition**:
1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

**Translation**: Depend on interfaces, not concrete implementations.

**Why It Matters**:
- Decouples code
- Enables testing (dependency injection)
- Improves flexibility
- Supports multiple implementations

**Violation Example**:
```python
# BAD: High-level depends on low-level concrete classes
class MySQLDatabase:
    def connect(self):
        # MySQL-specific connection
        pass

    def query(self, sql):
        # MySQL-specific query
        pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Hard dependency!

    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

**Problems**:
- Can't switch to PostgreSQL without changing UserService
- Can't test UserService without MySQL database
- UserService tightly coupled to MySQL

**Fixed Example**:
```python
# GOOD: Both depend on abstraction
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def query(self, sql):
        pass

class MySQLDatabase(Database):
    def connect(self):
        # MySQL-specific
        pass

    def query(self, sql):
        # MySQL-specific
        pass

class PostgreSQLDatabase(Database):
    def connect(self):
        # PostgreSQL-specific
        pass

    def query(self, sql):
        # PostgreSQL-specific
        pass

class UserService:
    def __init__(self, db: Database):  # Depends on abstraction
        self.db = db

    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Usage: Inject dependency
db = MySQLDatabase()
user_service = UserService(db)

# Easy to switch
db = PostgreSQLDatabase()
user_service = UserService(db)

# Easy to test
class MockDatabase(Database):
    def connect(self): pass
    def query(self, sql):
        return {'id': 1, 'name': 'Test'}

test_service = UserService(MockDatabase())
```

**Real-World Example: Notification System**:
```typescript
// BAD: Direct dependencies
class EmailService {
    send(to: string, message: string) {
        // SMTP logic
    }
}

class OrderProcessor {
    private emailService = new EmailService();  // Hard dependency

    async processOrder(order: Order) {
        // Process order
        this.emailService.send(order.email, 'Order confirmed');
    }
}

// Problems:
// - Can't add SMS notifications without modifying OrderProcessor
// - Can't test without sending actual emails
// - OrderProcessor depends on concrete EmailService

// GOOD: Dependency inversion
interface NotificationService {
    send(to: string, message: string): Promise<void>;
}

class EmailNotificationService implements NotificationService {
    async send(to: string, message: string) {
        // SMTP logic
    }
}

class SMSNotificationService implements NotificationService {
    async send(to: string, message: string) {
        // Twilio API
    }
}

class PushNotificationService implements NotificationService {
    async send(to: string, message: string) {
        // Firebase Cloud Messaging
    }
}

class OrderProcessor {
    constructor(
        private notificationService: NotificationService  // Abstraction
    ) {}

    async processOrder(order: Order) {
        // Process order
        await this.notificationService.send(order.contact, 'Order confirmed');
    }
}

// Usage: Dependency injection
const emailService = new EmailNotificationService();
const orderProcessor = new OrderProcessor(emailService);

// Easy to switch
const smsService = new SMSNotificationService();
const orderProcessor2 = new OrderProcessor(smsService);

// Easy to test
class MockNotificationService implements NotificationService {
    sentMessages: Array<{to: string, message: string}> = [];

    async send(to: string, message: string) {
        this.sentMessages.push({to, message});
    }
}

describe('OrderProcessor', () => {
    it('sends notification on order', async () => {
        const mockNotification = new MockNotificationService();
        const processor = new OrderProcessor(mockNotification);

        await processor.processOrder(testOrder);

        expect(mockNotification.sentMessages).toHaveLength(1);
    });
});
```

**Dependency Injection Container**:
```typescript
// Dependency injection framework (simplified)
class Container {
    private bindings = new Map<string, any>();

    bind<T>(key: string, factory: () => T) {
        this.bindings.set(key, factory);
    }

    resolve<T>(key: string): T {
        const factory = this.bindings.get(key);
        if (!factory) {
            throw new Error(`No binding for ${key}`);
        }
        return factory();
    }
}

// Setup
const container = new Container();

container.bind('Database', () => new MySQLDatabase(config));
container.bind('NotificationService', () => new EmailNotificationService());
container.bind('UserRepository', () =>
    new UserRepository(container.resolve('Database'))
);
container.bind('UserService', () =>
    new UserService(
        container.resolve('UserRepository'),
        container.resolve('NotificationService')
    )
);

// Usage
const userService = container.resolve('UserService');
```

---

## 2.2 Design Patterns

### 2.2.1 Creational Patterns

#### Singleton

**Purpose**: Ensure class has only one instance and provide global access point.

**When to Use**:
- Logging
- Configuration management
- Database connections
- Cache managers

**When NOT to Use**:
- Creates hidden dependencies (testing nightmare)
- Violates Single Responsibility
- Makes code harder to parallelize
- Often an anti-pattern (use dependency injection instead)

**Implementation**:
```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Usage
s1 = Singleton()
s2 = Singleton()
assert s1 is s2  # Same instance

# Thread-safe version
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Better Alternative: Dependency Injection**:
```typescript
// Instead of singleton
class ConfigManager {
    private static instance: ConfigManager;

    static getInstance() {
        if (!this.instance) {
            this.instance = new ConfigManager();
        }
        return this.instance;
    }
}

// Hidden dependency (bad)
class UserService {
    getConfig() {
        return ConfigManager.getInstance();  // Hidden dependency!
    }
}

// Better: Explicit dependency
class UserService {
    constructor(private config: Config) {}  // Clear dependency

    getConfig() {
        return this.config;
    }
}

// Create single instance in composition root
const config = new Config();
const userService = new UserService(config);
```

#### Factory Method

**Purpose**: Define interface for creating object, but let subclasses decide which class to instantiate.

**When to Use**:
- Don't know exact types/dependencies until runtime
- Want to localize instantiation logic
- Want to provide extension points

```typescript
// Product interface
interface Button {
    render(): void;
    onClick(callback: () => void): void;
}

// Concrete products
class WindowsButton implements Button {
    render() {
        console.log('Rendering Windows button');
    }

    onClick(callback: () => void) {
        // Windows-specific event handling
    }
}

class MacButton implements Button {
    render() {
        console.log('Rendering Mac button');
    }

    onClick(callback: () => void) {
        // Mac-specific event handling
    }
}

// Creator (abstract)
abstract class Dialog {
    abstract createButton(): Button;

    render() {
        const button = this.createButton();
        button.render();
        button.onClick(() => console.log('Clicked'));
    }
}

// Concrete creators
class WindowsDialog extends Dialog {
    createButton(): Button {
        return new WindowsButton();
    }
}

class MacDialog extends Dialog {
    createButton(): Button {
        return new MacButton();
    }
}

// Usage
function clientCode(dialog: Dialog) {
    dialog.render();
}

const os = getOperatingSystem();
if (os === 'Windows') {
    clientCode(new WindowsDialog());
} else {
    clientCode(new MacDialog());
}
```

#### Abstract Factory

**Purpose**: Create families of related objects without specifying concrete classes.

**When to Use**:
- Need to create related objects together
- Want to ensure compatibility between created objects
- Multiple product families

```typescript
// Abstract products
interface Button {
    render(): void;
}

interface Checkbox {
    render(): void;
}

// Abstract factory
interface GUIFactory {
    createButton(): Button;
    createCheckbox(): Checkbox;
}

// Concrete products - Windows
class WindowsButton implements Button {
    render() {
        console.log('Windows button');
    }
}

class WindowsCheckbox implements Checkbox {
    render() {
        console.log('Windows checkbox');
    }
}

// Concrete products - Mac
class MacButton implements Button {
    render() {
        console.log('Mac button');
    }
}

class MacCheckbox implements Checkbox {
    render() {
        console.log('Mac checkbox');
    }
}

// Concrete factories
class WindowsFactory implements GUIFactory {
    createButton(): Button {
        return new WindowsButton();
    }

    createCheckbox(): Checkbox {
        return new WindowsCheckbox();
    }
}

class MacFactory implements GUIFactory {
    createButton(): Button {
        return new MacButton();
    }

    createCheckbox(): Checkbox {
        return new MacCheckbox();
    }
}

// Client code
class Application {
    private button: Button;
    private checkbox: Checkbox;

    constructor(factory: GUIFactory) {
        this.button = factory.createButton();
        this.checkbox = factory.createCheckbox();
    }

    render() {
        this.button.render();
        this.checkbox.render();
    }
}

// Usage
const os = getOperatingSystem();
const factory = os === 'Windows'
    ? new WindowsFactory()
    : new MacFactory();
const app = new Application(factory);
app.render();
```

#### Builder

**Purpose**: Construct complex objects step by step.

**When to Use**:
- Object construction is complex
- Need different representations of object
- Want to avoid telescoping constructors

```typescript
// Product
class Car {
    seats: number;
    engine: string;
    tripComputer: boolean;
    gps: boolean;

    describe() {
        return `Car with ${this.seats} seats, ${this.engine} engine, ` +
               `GPS: ${this.gps}, Trip computer: ${this.tripComputer}`;
    }
}

// Builder interface
interface CarBuilder {
    reset(): void;
    setSeats(number: number): this;
    setEngine(engine: string): this;
    setTripComputer(): this;
    setGPS(): this;
    build(): Car;
}

// Concrete builder
class ConcreteCarBuilder implements CarBuilder {
    private car: Car;

    constructor() {
        this.reset();
    }

    reset() {
        this.car = new Car();
    }

    setSeats(number: number): this {
        this.car.seats = number;
        return this;
    }

    setEngine(engine: string): this {
        this.car.engine = engine;
        return this;
    }

    setTripComputer(): this {
        this.car.tripComputer = true;
        return this;
    }

    setGPS(): this {
        this.car.gps = true;
        return this;
    }

    build(): Car {
        const result = this.car;
        this.reset();
        return result;
    }
}

// Director (optional)
class Director {
    constructor(private builder: CarBuilder) {}

    buildSportsCar() {
        return this.builder
            .setSeats(2)
            .setEngine('V8')
            .setGPS()
            .build();
    }

    buildSUV() {
        return this.builder
            .setSeats(7)
            .setEngine('V6')
            .setGPS()
            .setTripComputer()
            .build();
    }
}

// Usage
const builder = new ConcreteCarBuilder();

// Manual building
const customCar = builder
    .setSeats(4)
    .setEngine('Electric')
    .setGPS()
    .build();

// Using director
const director = new Director(builder);
const sportsCar = director.buildSportsCar();
```

**Real-World Example: Query Builder**:
```typescript
class Query {
    private selectClause: string;
    private fromClause: string;
    private whereClause: string;
    private orderByClause: string;
    private limitClause: string;

    toString(): string {
        return [
            this.selectClause,
            this.fromClause,
            this.whereClause,
            this.orderByClause,
            this.limitClause
        ].filter(Boolean).join(' ');
    }
}

class QueryBuilder {
    private query: Query;

    constructor() {
        this.query = new Query();
    }

    select(...columns: string[]): this {
        this.query.selectClause = `SELECT ${columns.join(', ')}`;
        return this;
    }

    from(table: string): this {
        this.query.fromClause = `FROM ${table}`;
        return this;
    }

    where(condition: string): this {
        this.query.whereClause = `WHERE ${condition}`;
        return this;
    }

    orderBy(column: string, direction = 'ASC'): this {
        this.query.orderByClause = `ORDER BY ${column} ${direction}`;
        return this;
    }

    limit(count: number): this {
        this.query.limitClause = `LIMIT ${count}`;
        return this;
    }

    build(): Query {
        return this.query;
    }
}

// Usage
const query = new QueryBuilder()
    .select('id', 'name', 'email')
    .from('users')
    .where('age > 18')
    .orderBy('name', 'ASC')
    .limit(10)
    .build();

console.log(query.toString());
// SELECT id, name, email FROM users WHERE age > 18 ORDER BY name ASC LIMIT 10
```

#### Prototype

**Purpose**: Create new objects by cloning existing ones.

**When to Use**:
- Object creation is expensive
- Want to avoid complex initialization
- Need to create many similar objects

```typescript
interface Prototype {
    clone(): Prototype;
}

class Shape implements Prototype {
    x: number;
    y: number;
    color: string;

    constructor(source?: Shape) {
        if (source) {
            this.x = source.x;
            this.y = source.y;
            this.color = source.color;
        }
    }

    clone(): Shape {
        return new Shape(this);
    }
}

class Circle extends Shape {
    radius: number;

    constructor(source?: Circle) {
        super(source);
        if (source) {
            this.radius = source.radius;
        }
    }

    clone(): Circle {
        return new Circle(this);
    }
}

// Usage
const circle1 = new Circle();
circle1.x = 10;
circle1.y = 20;
circle1.radius = 15;
circle1.color = 'red';

// Clone instead of reconstructing
const circle2 = circle1.clone();
circle2.x = 30;  // Modify clone independently
```

### 2.2.2 Structural Patterns

#### Adapter

**Purpose**: Convert interface of class into another interface clients expect.

**When to Use**:
- Need to use existing class with incompatible interface
- Want to create reusable class that cooperates with unrelated classes
- Need to use several existing subclasses, but impractical to adapt via subclassing

```typescript
// Target interface (what client expects)
interface MediaPlayer {
    play(filename: string): void;
}

// Adaptee (existing interface)
class AdvancedMediaPlayer {
    playVlc(filename: string) {
        console.log(`Playing VLC file: ${filename}`);
    }

    playMp4(filename: string) {
        console.log(`Playing MP4 file: ${filename}`);
    }
}

// Adapter
class MediaAdapter implements MediaPlayer {
    private advancedPlayer: AdvancedMediaPlayer;

    constructor(private audioType: string) {
        this.advancedPlayer = new AdvancedMediaPlayer();
    }

    play(filename: string): void {
        if (this.audioType === 'vlc') {
            this.advancedPlayer.playVlc(filename);
        } else if (this.audioType === 'mp4') {
            this.advancedPlayer.playMp4(filename);
        }
    }
}

// Client code
class AudioPlayer implements MediaPlayer {
    play(filename: string): void {
        const extension = filename.split('.').pop();

        if (extension === 'mp3') {
            console.log(`Playing MP3 file: ${filename}`);
        } else if (extension === 'vlc' || extension === 'mp4') {
            const adapter = new MediaAdapter(extension);
            adapter.play(filename);
        } else {
            console.log(`Invalid format: ${extension}`);
        }
    }
}

// Usage
const player = new AudioPlayer();
player.play('song.mp3');  // Direct playback
player.play('video.vlc'); // Through adapter
player.play('movie.mp4'); // Through adapter
```

**Real-World Example: Third-Party API**:
```typescript
// Third-party API (can't modify)
class StripeAPI {
    makePayment(cardNumber: string, amount: number) {
        console.log(`Stripe: Charged ${amount} to card ${cardNumber}`);
    }
}

// Our application interface
interface PaymentProcessor {
    processPayment(paymentDetails: PaymentDetails): PaymentResult;
}

interface PaymentDetails {
    cardToken: string;
    amount: number;
    currency: string;
}

interface PaymentResult {
    success: boolean;
    transactionId: string;
}

// Adapter
class StripeAdapter implements PaymentProcessor {
    private stripe: StripeAPI;

    constructor() {
        this.stripe = new StripeAPI();
    }

    processPayment(details: PaymentDetails): PaymentResult {
        // Adapt our interface to Stripe's interface
        this.stripe.makePayment(details.cardToken, details.amount);

        return {
            success: true,
            transactionId: this.generateTransactionId()
        };
    }

    private generateTransactionId(): string {
        return `txn_${Date.now()}`;
    }
}

// Now can easily swap payment providers
class PayPalAdapter implements PaymentProcessor {
    processPayment(details: PaymentDetails): PaymentResult {
        // Adapt to PayPal API
        // ...
    }
}

// Usage
class CheckoutService {
    constructor(private paymentProcessor: PaymentProcessor) {}

    checkout(details: PaymentDetails) {
        return this.paymentProcessor.processPayment(details);
    }
}

const service = new CheckoutService(new StripeAdapter());
```

#### Decorator

**Purpose**: Attach additional responsibilities to object dynamically.

**When to Use**:
- Need to add responsibilities to objects without affecting other objects
- Responsibilities can be withdrawn
- Extension by subclassing is impractical

```typescript
// Component interface
interface Coffee {
    cost(): number;
    description(): string;
}

// Concrete component
class SimpleCoffee implements Coffee {
    cost(): number {
        return 5;
    }

    description(): string {
        return 'Simple coffee';
    }
}

// Base decorator
abstract class CoffeeDecorator implements Coffee {
    constructor(protected coffee: Coffee) {}

    cost(): number {
        return this.coffee.cost();
    }

    description(): string {
        return this.coffee.description();
    }
}

// Concrete decorators
class MilkDecorator extends CoffeeDecorator {
    cost(): number {
        return this.coffee.cost() + 2;
    }

    description(): string {
        return this.coffee.description() + ', milk';
    }
}

class SugarDecorator extends CoffeeDecorator {
    cost(): number {
        return this.coffee.cost() + 1;
    }

    description(): string {
        return this.coffee.description() + ', sugar';
    }
}

class WhipDecorator extends CoffeeDecorator {
    cost(): number {
        return this.coffee.cost() + 3;
    }

    description(): string {
        return this.coffee.description() + ', whip';
    }
}

// Usage
let coffee: Coffee = new SimpleCoffee();
console.log(`${coffee.description()}: $${coffee.cost()}`);
// Simple coffee: $5

coffee = new MilkDecorator(coffee);
console.log(`${coffee.description()}: $${coffee.cost()}`);
// Simple coffee, milk: $7

coffee = new SugarDecorator(coffee);
coffee = new WhipDecorator(coffee);
console.log(`${coffee.description()}: $${coffee.cost()}`);
// Simple coffee, milk, sugar, whip: $11
```

**Real-World Example: HTTP Middleware**:
```typescript
interface HttpHandler {
    handle(request: Request): Response;
}

class BaseHandler implements HttpHandler {
    handle(request: Request): Response {
        return {
            status: 200,
            body: 'Success'
        };
    }
}

// Decorator: Logging
class LoggingDecorator implements HttpHandler {
    constructor(private handler: HttpHandler) {}

    handle(request: Request): Response {
        console.log(`Request: ${request.method} ${request.url}`);
        const response = this.handler.handle(request);
        console.log(`Response: ${response.status}`);
        return response;
    }
}

// Decorator: Authentication
class AuthDecorator implements HttpHandler {
    constructor(private handler: HttpHandler) {}

    handle(request: Request): Response {
        if (!request.headers.authorization) {
            return {
                status: 401,
                body: 'Unauthorized'
            };
        }

        return this.handler.handle(request);
    }
}

// Decorator: Rate limiting
class RateLimitDecorator implements HttpHandler {
    private requests = new Map<string, number[]>();
    private readonly limit = 10;
    private readonly window = 60000; // 1 minute

    constructor(private handler: HttpHandler) {}

    handle(request: Request): Response {
        const ip = request.ip;
        const now = Date.now();

        if (!this.requests.has(ip)) {
            this.requests.set(ip, []);
        }

        const timestamps = this.requests.get(ip)!;
        const recent = timestamps.filter(t => now - t < this.window);

        if (recent.length >= this.limit) {
            return {
                status: 429,
                body: 'Too many requests'
            };
        }

        recent.push(now);
        this.requests.set(ip, recent);

        return this.handler.handle(request);
    }
}

// Usage: Stack decorators
let handler: HttpHandler = new BaseHandler();
handler = new LoggingDecorator(handler);
handler = new AuthDecorator(handler);
handler = new RateLimitDecorator(handler);

const response = handler.handle(request);
```

#### Facade

**Purpose**: Provide unified interface to set of interfaces in subsystem.

**When to Use**:
- Need simple interface to complex subsystem
- Want to layer subsystems
- Reducing coupling between subsystems and clients

```typescript
// Complex subsystems
class CPU {
    freeze() {
        console.log('CPU: Freezing');
    }

    jump(position: number) {
        console.log(`CPU: Jumping to ${position}`);
    }

    execute() {
        console.log('CPU: Executing');
    }
}

class Memory {
    load(position: number, data: string) {
        console.log(`Memory: Loading "${data}" at ${position}`);
    }
}

class HardDrive {
    read(lba: number, size: number): string {
        console.log(`HardDrive: Reading ${size} bytes from ${lba}`);
        return 'boot data';
    }
}

// Facade
class ComputerFacade {
    private cpu: CPU;
    private memory: Memory;
    private hardDrive: HardDrive;

    constructor() {
        this.cpu = new CPU();
        this.memory = new Memory();
        this.hardDrive = new HardDrive();
    }

    start() {
        console.log('Starting computer...');
        this.cpu.freeze();
        const bootData = this.hardDrive.read(0, 1024);
        this.memory.load(0, bootData);
        this.cpu.jump(0);
        this.cpu.execute();
        console.log('Computer started!');
    }
}

// Usage
const computer = new ComputerFacade();
computer.start();  // Simple interface hides complex subsystem interactions
```

**Real-World Example: Video Conversion**:
```typescript
// Complex video processing classes
class VideoFile {
    constructor(public filename: string) {}
}

class OggCompressionCodec {
    compress(buffer: Buffer): Buffer {
        console.log('Compressing with Ogg');
        return buffer;
    }
}

class MPEG4CompressionCodec {
    compress(buffer: Buffer): Buffer {
        console.log('Compressing with MPEG4');
        return buffer;
    }
}

class CodecFactory {
    static extract(file: VideoFile) {
        const type = file.filename.split('.').pop();
        if (type === 'mp4') {
            return new MPEG4CompressionCodec();
        }
        return new OggCompressionCodec();
    }
}

class BitrateReader {
    static read(file: VideoFile, codec: any): Buffer {
        console.log('Reading file bitrate');
        return Buffer.from('video data');
    }

    static convert(buffer: Buffer, codec: any): Buffer {
        console.log('Converting bitrate');
        return buffer;
    }
}

class AudioMixer {
    static fix(result: Buffer): Buffer {
        console.log('Fixing audio');
        return result;
    }
}

// Facade
class VideoConverter {
    convert(filename: string, format: string): Buffer {
        console.log(`Converting ${filename} to ${format}`);

        const file = new VideoFile(filename);
        const sourceCodec = CodecFactory.extract(file);

        let buffer: Buffer;
        if (format === 'mp4') {
            const destinationCodec = new MPEG4CompressionCodec();
            buffer = BitrateReader.read(file, sourceCodec);
            buffer = BitrateReader.convert(buffer, destinationCodec);
            buffer = destinationCodec.compress(buffer);
        } else {
            const destinationCodec = new OggCompressionCodec();
            buffer = BitrateReader.read(file, sourceCodec);
            buffer = BitrateReader.convert(buffer, destinationCodec);
            buffer = destinationCodec.compress(buffer);
            buffer = AudioMixer.fix(buffer);
        }

        console.log('Conversion complete');
        return buffer;
    }
}

// Usage: Simple interface for complex operation
const converter = new VideoConverter();
converter.convert('video.avi', 'mp4');
```

Due to the length limit, I'll continue in the next response to complete all 15 sections...


#### Proxy

**Purpose**: Provide surrogate or placeholder for another object to control access.

**Types**:
1. **Remote Proxy**: Represents object in different address space
2. **Virtual Proxy**: Delays creation of expensive object until needed
3. **Protection Proxy**: Controls access to object
4. **Smart Proxy**: Adds additional logic when accessing object

**When to Use**:
- Lazy initialization (virtual proxy)
- Access control (protection proxy)
- Local representation of remote object (remote proxy)
- Logging, caching, reference counting

```typescript
// Subject interface
interface Image {
    display(): void;
}

// Real subject
class RealImage implements Image {
    constructor(private filename: string) {
        this.loadFromDisk();
    }

    private loadFromDisk() {
        console.log(`Loading image from disk: ${this.filename}`);
        // Expensive operation
    }

    display() {
        console.log(`Displaying ${this.filename}`);
    }
}

// Proxy (Virtual Proxy for lazy loading)
class ProxyImage implements Image {
    private realImage: RealImage | null = null;

    constructor(private filename: string) {}

    display() {
        // Load real image only when needed
        if (this.realImage === null) {
            this.realImage = new RealImage(this.filename);
        }
        this.realImage.display();
    }
}

// Usage
const image = new ProxyImage('large_photo.jpg');
// Image not loaded yet

console.log('Image created, but not loaded');

image.display();  // NOW image is loaded
// Loading image from disk: large_photo.jpg
// Displaying large_photo.jpg

image.display();  // Uses cached image
// Displaying large_photo.jpg (no loading message)
```

**Real-World Example: API Rate Limiting Proxy**:
```typescript
interface APIService {
    fetchData(url: string): Promise<any>;
}

class RealAPIService implements APIService {
    async fetchData(url: string): Promise<any> {
        const response = await fetch(url);
        return response.json();
    }
}

class RateLimitingProxy implements APIService {
    private service: RealAPIService;
    private requestLog: number[] = [];
    private readonly limit = 10;
    private readonly windowMs = 60000; // 1 minute

    constructor() {
        this.service = new RealAPIService();
    }

    async fetchData(url: string): Promise<any> {
        const now = Date.now();

        // Remove old requests outside window
        this.requestLog = this.requestLog.filter(
            time => now - time < this.windowMs
        );

        if (this.requestLog.length >= this.limit) {
            throw new Error('Rate limit exceeded. Try again later.');
        }

        this.requestLog.push(now);
        return this.service.fetchData(url);
    }
}

// Caching Proxy
class CachingProxy implements APIService {
    private service: RealAPIService;
    private cache = new Map<string, {data: any, timestamp: number}>();
    private readonly cacheDuration = 300000; // 5 minutes

    constructor() {
        this.service = new RealAPIService();
    }

    async fetchData(url: string): Promise<any> {
        const cached = this.cache.get(url);
        const now = Date.now();

        if (cached && now - cached.timestamp < this.cacheDuration) {
            console.log('Returning cached data');
            return cached.data;
        }

        console.log('Fetching fresh data');
        const data = await this.service.fetchData(url);
        this.cache.set(url, {data, timestamp: now});
        return data;
    }
}

// Usage: Stack proxies
let api: APIService = new RealAPIService();
api = new CachingProxy();  // Add caching
api = new RateLimitingProxy();  // Add rate limiting
```

### 2.2.3 Behavioral Patterns

#### Observer

**Purpose**: Define one-to-many dependency where when one object changes state, all dependents are notified.

**When to Use**:
- State changes in one object need to trigger updates in other objects
- Object should notify other objects without making assumptions about them
- Event handling systems

```typescript
// Subject interface
interface Subject {
    attach(observer: Observer): void;
    detach(observer: Observer): void;
    notify(): void;
}

// Observer interface
interface Observer {
    update(subject: Subject): void;
}

// Concrete subject
class NewsAgency implements Subject {
    private observers: Observer[] = [];
    private news: string = '';

    attach(observer: Observer): void {
        const index = this.observers.indexOf(observer);
        if (index === -1) {
            this.observers.push(observer);
            console.log('Observer attached');
        }
    }

    detach(observer: Observer): void {
        const index = this.observers.indexOf(observer);
        if (index !== -1) {
            this.observers.splice(index, 1);
            console.log('Observer detached');
        }
    }

    notify(): void {
        for (const observer of this.observers) {
            observer.update(this);
        }
    }

    setNews(news: string): void {
        this.news = news;
        this.notify();
    }

    getNews(): string {
        return this.news;
    }
}

// Concrete observers
class EmailSubscriber implements Observer {
    constructor(private email: string) {}

    update(subject: Subject): void {
        if (subject instanceof NewsAgency) {
            console.log(`Email to ${this.email}: ${subject.getNews()}`);
        }
    }
}

class SMSSubscriber implements Observer {
    constructor(private phone: string) {}

    update(subject: Subject): void {
        if (subject instanceof NewsAgency) {
            console.log(`SMS to ${this.phone}: ${subject.getNews()}`);
        }
    }
}

// Usage
const agency = new NewsAgency();
const emailSub = new EmailSubscriber('user@example.com');
const smsSub = new SMSSubscriber('+1234567890');

agency.attach(emailSub);
agency.attach(smsSub);

agency.setNews('Breaking: New pattern discovered!');
// Email to user@example.com: Breaking: New pattern discovered!
// SMS to +1234567890: Breaking: New pattern discovered!
```

**Real-World Example: Event System**:
```typescript
type EventHandler<T = any> = (data: T) => void;

class EventEmitter {
    private events = new Map<string, EventHandler[]>();

    on(event: string, handler: EventHandler): void {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event)!.push(handler);
    }

    off(event: string, handler: EventHandler): void {
        const handlers = this.events.get(event);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(event: string, data?: any): void {
        const handlers = this.events.get(event);
        if (handlers) {
            for (const handler of handlers) {
                handler(data);
            }
        }
    }

    once(event: string, handler: EventHandler): void {
        const wrapper = (data: any) => {
            handler(data);
            this.off(event, wrapper);
        };
        this.on(event, wrapper);
    }
}

// Usage
class UserService extends EventEmitter {
    createUser(userData: any) {
        // Create user
        const user = {id: 1, ...userData};

        // Emit event
        this.emit('user:created', user);

        return user;
    }
}

const userService = new UserService();

// Subscribe to events
userService.on('user:created', (user) => {
    console.log('Send welcome email to', user.email);
});

userService.on('user:created', (user) => {
    console.log('Track analytics for user', user.id);
});

userService.on('user:created', (user) => {
    console.log('Create user profile for', user.name);
});

userService.createUser({name: 'John', email: 'john@example.com'});
// Send welcome email to john@example.com
// Track analytics for user 1
// Create user profile for John
```

#### Strategy

**Purpose**: Define family of algorithms, encapsulate each one, and make them interchangeable.

**When to Use**:
- Many related classes differ only in behavior
- Need different variants of an algorithm
- Algorithm uses data that clients shouldn't know about
- Class defines many behaviors as conditional statements

```typescript
// Strategy interface
interface PaymentStrategy {
    pay(amount: number): void;
}

// Concrete strategies
class CreditCardStrategy implements PaymentStrategy {
    constructor(
        private cardNumber: string,
        private cvv: string,
        private expiryDate: string
    ) {}

    pay(amount: number): void {
        console.log(`Paid ${amount} using Credit Card ${this.cardNumber}`);
    }
}

class PayPalStrategy implements PaymentStrategy {
    constructor(private email: string) {}

    pay(amount: number): void {
        console.log(`Paid ${amount} using PayPal account ${this.email}`);
    }
}

class CryptoStrategy implements PaymentStrategy {
    constructor(private walletAddress: string) {}

    pay(amount: number): void {
        console.log(`Paid ${amount} using Crypto wallet ${this.walletAddress}`);
    }
}

// Context
class ShoppingCart {
    private items: {name: string, price: number}[] = [];
    private paymentStrategy?: PaymentStrategy;

    addItem(name: string, price: number): void {
        this.items.push({name, price});
    }

    setPaymentStrategy(strategy: PaymentStrategy): void {
        this.paymentStrategy = strategy;
    }

    checkout(): void {
        if (!this.paymentStrategy) {
            throw new Error('Payment strategy not set');
        }

        const total = this.items.reduce((sum, item) => sum + item.price, 0);
        this.paymentStrategy.pay(total);
    }
}

// Usage
const cart = new ShoppingCart();
cart.addItem('Book', 20);
cart.addItem('Pen', 5);

// Pay with credit card
cart.setPaymentStrategy(new CreditCardStrategy('1234-5678', '123', '12/25'));
cart.checkout();  // Paid 25 using Credit Card 1234-5678

// Change strategy and pay again
cart.setPaymentStrategy(new PayPalStrategy('user@example.com'));
cart.checkout();  // Paid 25 using PayPal account user@example.com
```

**Real-World Example: Sorting Strategy**:
```typescript
interface SortStrategy<T> {
    sort(data: T[]): T[];
}

class QuickSort<T> implements SortStrategy<T> {
    sort(data: T[]): T[] {
        console.log('Sorting using QuickSort');
        // QuickSort implementation
        return data.sort();
    }
}

class MergeSort<T> implements SortStrategy<T> {
    sort(data: T[]): T[] {
        console.log('Sorting using MergeSort');
        // MergeSort implementation
        return data.sort();
    }
}

class HeapSort<T> implements SortStrategy<T> {
    sort(data: T[]): T[] {
        console.log('Sorting using HeapSort');
        // HeapSort implementation
        return data.sort();
    }
}

class DataProcessor<T> {
    private strategy: SortStrategy<T>;

    constructor(strategy: SortStrategy<T>) {
        this.strategy = strategy;
    }

    setStrategy(strategy: SortStrategy<T>): void {
        this.strategy = strategy;
    }

    processData(data: T[]): T[] {
        // Choose strategy based on data size
        if (data.length < 10) {
            this.setStrategy(new QuickSort());
        } else if (data.length < 1000) {
            this.setStrategy(new MergeSort());
        } else {
            this.setStrategy(new HeapSort());
        }

        return this.strategy.sort(data);
    }
}
```

#### Command

**Purpose**: Encapsulate request as object, allowing parameterization and queuing.

**When to Use**:
- Parameterize objects with operations
- Specify, queue, and execute requests at different times
- Support undo/redo
- Log changes for crash recovery

```typescript
// Command interface
interface Command {
    execute(): void;
    undo(): void;
}

// Receiver
class TextEditor {
    private text: string = '';

    appendText(newText: string): void {
        this.text += newText;
    }

    deleteText(length: number): void {
        this.text = this.text.slice(0, -length);
    }

    getText(): string {
        return this.text;
    }
}

// Concrete commands
class AppendTextCommand implements Command {
    constructor(
        private editor: TextEditor,
        private text: string
    ) {}

    execute(): void {
        this.editor.appendText(this.text);
    }

    undo(): void {
        this.editor.deleteText(this.text.length);
    }
}

class DeleteTextCommand implements Command {
    private deletedText: string = '';

    constructor(
        private editor: TextEditor,
        private length: number
    ) {}

    execute(): void {
        const currentText = this.editor.getText();
        this.deletedText = currentText.slice(-this.length);
        this.editor.deleteText(this.length);
    }

    undo(): void {
        this.editor.appendText(this.deletedText);
    }
}

// Invoker
class CommandManager {
    private history: Command[] = [];
    private current: number = -1;

    executeCommand(command: Command): void {
        // Remove any commands after current position
        this.history = this.history.slice(0, this.current + 1);

        command.execute();
        this.history.push(command);
        this.current++;
    }

    undo(): void {
        if (this.current >= 0) {
            this.history[this.current].undo();
            this.current--;
        }
    }

    redo(): void {
        if (this.current < this.history.length - 1) {
            this.current++;
            this.history[this.current].execute();
        }
    }
}

// Usage
const editor = new TextEditor();
const manager = new CommandManager();

manager.executeCommand(new AppendTextCommand(editor, 'Hello '));
console.log(editor.getText());  // "Hello "

manager.executeCommand(new AppendTextCommand(editor, 'World'));
console.log(editor.getText());  // "Hello World"

manager.undo();
console.log(editor.getText());  // "Hello "

manager.redo();
console.log(editor.getText());  // "Hello World"

manager.executeCommand(new DeleteTextCommand(editor, 6));
console.log(editor.getText());  // "Hello"
```

**Real-World Example: Task Queue**:
```typescript
interface Task {
    execute(): Promise<void>;
    retry?(): boolean;
}

class EmailTask implements Task {
    private attempts = 0;
    private maxAttempts = 3;

    constructor(
        private to: string,
        private subject: string,
        private body: string
    ) {}

    async execute(): Promise<void> {
        this.attempts++;
        console.log(`Sending email to ${this.to} (attempt ${this.attempts})`);

        // Simulate email sending
        if (Math.random() > 0.7) {
            throw new Error('Email failed');
        }

        console.log('Email sent successfully');
    }

    retry(): boolean {
        return this.attempts < this.maxAttempts;
    }
}

class TaskQueue {
    private queue: Task[] = [];
    private processing = false;

    addTask(task: Task): void {
        this.queue.push(task);
        this.process();
    }

    private async process(): Promise<void> {
        if (this.processing) return;

        this.processing = true;

        while (this.queue.length > 0) {
            const task = this.queue.shift()!;

            try {
                await task.execute();
            } catch (error) {
                console.error('Task failed:', error);

                if (task.retry && task.retry()) {
                    console.log('Retrying task...');
                    this.queue.unshift(task);  // Add back to front
                }
            }
        }

        this.processing = false;
    }
}

// Usage
const queue = new TaskQueue();
queue.addTask(new EmailTask('user1@example.com', 'Hello', 'Test email 1'));
queue.addTask(new EmailTask('user2@example.com', 'Hello', 'Test email 2'));
```

#### Template Method

**Purpose**: Define skeleton of algorithm in base class, letting subclasses override specific steps.

**When to Use**:
- Implement invariant parts of algorithm once, let subclasses implement variant behavior
- Control subclass extensions
- Factor out common behavior among subclasses

```typescript
abstract class DataProcessor {
    // Template method
    process(): void {
        this.readData();
        this.processData();
        this.writeData();
        this.cleanup();
    }

    abstract readData(): void;
    abstract processData(): void;
    abstract writeData(): void;

    // Hook method (optional override)
    cleanup(): void {
        console.log('Default cleanup');
    }
}

class CSVProcessor extends DataProcessor {
    private data: any[];

    readData(): void {
        console.log('Reading CSV file');
        this.data = [/* CSV data */];
    }

    processData(): void {
        console.log('Processing CSV data');
        this.data = this.data.map(row => {/* transform */});
    }

    writeData(): void {
        console.log('Writing CSV file');
        // Write transformed data
    }
}

class JSONProcessor extends DataProcessor {
    private data: any;

    readData(): void {
        console.log('Reading JSON file');
        this.data = {/* JSON data */};
    }

    processData(): void {
        console.log('Processing JSON data');
        // Transform JSON
    }

    writeData(): void {
        console.log('Writing JSON file');
        // Write transformed data
    }

    // Override hook
    cleanup(): void {
        console.log('JSON-specific cleanup');
    }
}

// Usage
const csvProcessor = new CSVProcessor();
csvProcessor.process();
// Reading CSV file
// Processing CSV data
// Writing CSV file
// Default cleanup

const jsonProcessor = new JSONProcessor();
jsonProcessor.process();
// Reading JSON file
// Processing JSON data
// Writing JSON file
// JSON-specific cleanup
```

#### State

**Purpose**: Allow object to alter behavior when internal state changes.

**When to Use**:
- Object behavior depends on state
- Large conditionals depend on object state
- State-specific behavior should be defined independently

```typescript
// State interface
interface State {
    insertCoin(): void;
    ejectCoin(): void;
    selectProduct(): void;
    dispense(): void;
}

// Context
class VendingMachine {
    private state: State;
    private noCoinState: State;
    private hasCoinState: State;
    private soldState: State;
    private soldOutState: State;
    private count: number;

    constructor(count: number) {
        this.count = count;

        this.noCoinState = new NoCoinState(this);
        this.hasCoinState = new HasCoinState(this);
        this.soldState = new SoldState(this);
        this.soldOutState = new SoldOutState(this);

        this.state = count > 0 ? this.noCoinState : this.soldOutState;
    }

    insertCoin(): void {
        this.state.insertCoin();
    }

    ejectCoin(): void {
        this.state.ejectCoin();
    }

    selectProduct(): void {
        this.state.selectProduct();
        this.state.dispense();
    }

    setState(state: State): void {
        this.state = state;
    }

    releaseProduct(): void {
        if (this.count > 0) {
            console.log('Product dispensed');
            this.count--;
        }
    }

    getCount(): number {
        return this.count;
    }

    getNoCoinState(): State { return this.noCoinState; }
    getHasCoinState(): State { return this.hasCoinState; }
    getSoldState(): State { return this.soldState; }
    getSoldOutState(): State { return this.soldOutState; }
}

// Concrete states
class NoCoinState implements State {
    constructor(private machine: VendingMachine) {}

    insertCoin(): void {
        console.log('Coin inserted');
        this.machine.setState(this.machine.getHasCoinState());
    }

    ejectCoin(): void {
        console.log('No coin to eject');
    }

    selectProduct(): void {
        console.log('Insert coin first');
    }

    dispense(): void {
        console.log('Pay first');
    }
}

class HasCoinState implements State {
    constructor(private machine: VendingMachine) {}

    insertCoin(): void {
        console.log('Coin already inserted');
    }

    ejectCoin(): void {
        console.log('Coin ejected');
        this.machine.setState(this.machine.getNoCoinState());
    }

    selectProduct(): void {
        console.log('Product selected');
        this.machine.setState(this.machine.getSoldState());
    }

    dispense(): void {
        console.log('Select product first');
    }
}

class SoldState implements State {
    constructor(private machine: VendingMachine) {}

    insertCoin(): void {
        console.log('Wait, dispensing product');
    }

    ejectCoin(): void {
        console.log('Already dispensing');
    }

    selectProduct(): void {
        console.log('Already dispensing');
    }

    dispense(): void {
        this.machine.releaseProduct();

        if (this.machine.getCount() > 0) {
            this.machine.setState(this.machine.getNoCoinState());
        } else {
            console.log('Machine sold out');
            this.machine.setState(this.machine.getSoldOutState());
        }
    }
}

class SoldOutState implements State {
    constructor(private machine: VendingMachine) {}

    insertCoin(): void {
        console.log('Machine sold out');
    }

    ejectCoin(): void {
        console.log('No coin inserted');
    }

    selectProduct(): void {
        console.log('Machine sold out');
    }

    dispense(): void {
        console.log('Machine sold out');
    }
}

// Usage
const machine = new VendingMachine(2);

machine.insertCoin();      // Coin inserted
machine.selectProduct();   // Product selected
                           // Product dispensed

machine.insertCoin();      // Coin inserted
machine.selectProduct();   // Product selected
                           // Product dispensed
                           // Machine sold out

machine.insertCoin();      // Machine sold out
```

---

## 2.3 Domain-Driven Design (DDD)

### 2.3.1 Core Concepts

**Ubiquitous Language**: Common language shared by developers and domain experts.

**Bounded Context**: Explicit boundary within which a domain model applies.

**Entities**: Objects with identity that persists over time.

**Value Objects**: Objects defined by their attributes, not identity.

**Aggregates**: Cluster of entities and value objects treated as a unit.

**Domain Events**: Something that happened in the domain that domain experts care about.

### 2.3.2 Strategic Design

**Context Mapping**: Define relationships between bounded contexts.

Types of relationships:
- **Shared Kernel**: Shared subset of domain model
- **Customer-Supplier**: Downstream depends on upstream
- **Conformist**: Downstream conforms to upstream model
- **Anti-Corruption Layer**: Translation layer to protect from external models
- **Separate Ways**: No connection between contexts
- **Open Host Service**: Protocol for accessing subsystem
- **Published Language**: Well-documented shared language

### 2.3.3 Tactical Design Patterns

```typescript
// Value Object
class Money {
    constructor(
        private readonly amount: number,
        private readonly currency: string
    ) {
        if (amount < 0) {
            throw new Error('Amount cannot be negative');
        }
    }

    add(other: Money): Money {
        if (this.currency !== other.currency) {
            throw new Error('Cannot add different currencies');
        }
        return new Money(this.amount + other.amount, this.currency);
    }

    equals(other: Money): boolean {
        return this.amount === other.amount && this.currency === other.currency;
    }
}

// Entity
class Order {
    private items: OrderItem[] = [];

    constructor(
        private readonly id: string,
        private customerId: string
    ) {}

    addItem(product: Product, quantity: number): void {
        const item = new OrderItem(product, quantity);
        this.items.push(item);
    }

    calculateTotal(): Money {
        return this.items.reduce(
            (total, item) => total.add(item.getPrice()),
            new Money(0, 'USD')
        );
    }

    // Entities are equal if IDs match
    equals(other: Order): boolean {
        return this.id === other.id;
    }
}

// Aggregate Root
class Customer {
    private orders: Order[] = [];

    constructor(
        private readonly id: string,
        private name: string,
        private email: string
    ) {}

    placeOrder(order: Order): void {
        // Business logic
        if (this.hasUnpaidOrders()) {
            throw new Error('Cannot place order with unpaid orders');
        }

        this.orders.push(order);

        // Emit domain event
        DomainEvents.raise(new OrderPlacedEvent(this.id, order));
    }

    private hasUnpaidOrders(): boolean {
        return this.orders.some(o => !o.isPaid());
    }
}

// Domain Event
class OrderPlacedEvent {
    constructor(
        public readonly customerId: string,
        public readonly order: Order,
        public readonly occurredAt: Date = new Date()
    ) {}
}

// Repository (interface)
interface CustomerRepository {
    findById(id: string): Promise<Customer | null>;
    save(customer: Customer): Promise<void>;
}

// Domain Service
class PricingService {
    calculateDiscount(customer: Customer, order: Order): Money {
        // Complex business logic that doesn't belong to any entity
        if (customer.isVIP()) {
            return order.getTotal().multiply(0.1);
        }
        return new Money(0, 'USD');
    }
}
```

### 2.3.4 Domain Events

```typescript
type EventHandler = (event: any) => void;

class DomainEvents {
    private static handlers = new Map<string, EventHandler[]>();

    static register(eventType: string, handler: EventHandler): void {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, []);
        }
        this.handlers.get(eventType)!.push(handler);
    }

    static raise(event: any): void {
        const eventType = event.constructor.name;
        const handlers = this.handlers.get(eventType);

        if (handlers) {
            for (const handler of handlers) {
                handler(event);
            }
        }
    }
}

// Register handlers
DomainEvents.register('OrderPlacedEvent', (event: OrderPlacedEvent) => {
    // Send confirmation email
    emailService.sendOrderConfirmation(event.customerId, event.order);
});

DomainEvents.register('OrderPlacedEvent', (event: OrderPlacedEvent) => {
    // Update inventory
    inventoryService.reserveItems(event.order);
});

DomainEvents.register('OrderPlacedEvent', (event: OrderPlacedEvent) => {
    // Track analytics
    analytics.track('order_placed', {
        customerId: event.customerId,
        orderId: event.order.id,
        total: event.order.getTotal()
    });
});
```

---

# PART 3: DISTRIBUTED SYSTEMS

## 3.1 CAP Theorem

**Statement**: A distributed system can provide at most two of three guarantees:

1. **Consistency (C)**: All nodes see same data at same time
2. **Availability (A)**: Every request receives a response (success or failure)
3. **Partition Tolerance (P)**: System continues operating despite network partitions

**Reality**: Network partitions WILL happen, so must choose between C and A.

### 3.1.1 CP Systems (Consistency + Partition Tolerance)

**Choose C when**: Data accuracy is critical, brief unavailability is acceptable.

**Examples**:
- Banking systems
- Inventory management
- HBase
- MongoDB (with strong consistency)
- Redis (when configured for strong consistency)

**Behavior During Partition**:
```
[Node A] ←✗→ [Node B]  (network partition)

Write to Node A:
- Node A: Cannot confirm write reached majority
- Returns error to client
- System unavailable but consistent
```

**MongoDB Example**:
```javascript
// MongoDB with majority write concern (CP)
await collection.insertOne(
    { name: 'Alice', balance: 1000 },
    { writeConcern: { w: 'majority' } }
);

// During partition:
// - Write blocked until majority confirms
// - If can't reach majority: write fails
// - System remains consistent but unavailable
```

### 3.1.2 AP Systems (Availability + Partition Tolerance)

**Choose A when**: System must stay operational, eventual consistency is acceptable.

**Examples**:
- Social media feeds
- Shopping carts
- DNS
- Cassandra
- DynamoDB (default)
- CouchDB

**Behavior During Partition**:
```
[Node A] ←✗→ [Node B]  (network partition)

Write to Node A:
- Node A: Accepts write immediately
- Returns success to client
- Node B has stale data
- Eventually consistent when partition heals
```

**DynamoDB Example**:
```javascript
// DynamoDB with eventual consistency (AP)
await dynamodb.putItem({
    TableName: 'Users',
    Item: { id: '123', name: 'Alice' }
});

// Read might return stale data
const result = await dynamodb.getItem({
    TableName: 'Users',
    Key: { id: '123' },
    ConsistentRead: false  // Eventual consistency
});

// During partition:
// - Writes accepted by available nodes
// - Reads may return old values
// - System available but inconsistent
```

### 3.1.3 Real-World Trade-offs

**Banking Transfer** (CP):
```python
def transfer(from_account, to_account, amount):
    # Must be consistent - can't have both accounts
    # showing different balances
    with transaction():
        from_balance = get_balance(from_account)

        if from_balance < amount:
            raise InsufficientFunds()

        # This must be atomic across all nodes
        debit(from_account, amount)
        credit(to_account, amount)

    # If network partition occurs:
    # - Transaction fails
    # - User sees error
    # - Money is NOT in inconsistent state
```

**Shopping Cart** (AP):
```python
def add_to_cart(user_id, item_id):
    # Accept write even during partition
    cart = get_cart(user_id)  # May be stale
    cart.add(item_id)
    save_cart(cart)

    # If network partition occurs:
    # - Write succeeds locally
    # - Other nodes may have different cart state
    # - Eventually syncs when partition heals

    # Conflict resolution: Last-write-wins or merge
```

## 3.2 Consistency Models

### 3.2.1 Strong Consistency

**Guarantee**: All reads see most recent write.

**Implementation**: Synchronous replication, quorum reads/writes.

**Example**:
```
Time    Client1         Node A          Node B
t0                      x = 1           x = 1
t1      Write x = 2     x = 2 ✓
t2                                      x = 2 ✓ (must wait)
t3      Read x          Returns 2       Returns 2
```

**Use Case**: Financial transactions, inventory management.

### 3.2.2 Eventual Consistency

**Guarantee**: If no new updates, eventually all reads return same value.

**Implementation**: Asynchronous replication.

**Example**:
```
Time    Client1         Node A          Node B
t0                      x = 1           x = 1
t1      Write x = 2     x = 2 ✓
t2      Read x                          Returns 1 (stale!)
t3                                      x = 2 ✓ (async)
t4      Read x                          Returns 2
```

**Use Case**: Social media, caching, DNS.

**Conflict Resolution**:
```typescript
// Last-Write-Wins (LWW)
interface Record {
    value: any;
    timestamp: number;
}

function merge(local: Record, remote: Record): Record {
    return local.timestamp > remote.timestamp ? local : remote;
}

// Vector Clocks (detects concurrent updates)
type VectorClock = Map<string, number>;

function compareVectorClocks(v1: VectorClock, v2: VectorClock) {
    let v1Greater = false;
    let v2Greater = false;

    const allKeys = new Set([...v1.keys(), ...v2.keys()]);

    for (const key of allKeys) {
        const t1 = v1.get(key) || 0;
        const t2 = v2.get(key) || 0;

        if (t1 > t2) v1Greater = true;
        if (t2 > t1) v2Greater = true;
    }

    if (v1Greater && !v2Greater) return 'v1_newer';
    if (v2Greater && !v1Greater) return 'v2_newer';
    if (v1Greater && v2Greater) return 'concurrent';
    return 'equal';
}
```

### 3.2.3 Causal Consistency

**Guarantee**: Causally related operations seen in order, concurrent operations may be seen differently.

**Example**:
```
Process 1: Write A → Write B (B depends on A)
Process 2: Reads must see A before B
Process 2: May see C before or after B if C is concurrent with B
```

**Implementation**:
```typescript
class CausalConsistencyStore {
    private store = new Map<string, any>();
    private vectorClock = new Map<string, number>();
    private readonly nodeId: string;

    constructor(nodeId: string) {
        this.nodeId = nodeId;
        this.vectorClock.set(nodeId, 0);
    }

    write(key: string, value: any, dependencies: VectorClock) {
        // Increment own clock
        const currentTime = (this.vectorClock.get(this.nodeId) || 0) + 1;
        this.vectorClock.set(this.nodeId, currentTime);

        // Merge dependency clocks
        for (const [node, time] of dependencies) {
            const existingTime = this.vectorClock.get(node) || 0;
            this.vectorClock.set(node, Math.max(existingTime, time));
        }

        this.store.set(key, {
            value,
            vectorClock: new Map(this.vectorClock)
        });
    }

    read(key: string): {value: any, vectorClock: VectorClock} | null {
        return this.store.get(key) || null;
    }
}
```

## 3.3 Consensus Algorithms

### 3.3.1 Paxos

**Purpose**: Achieve consensus among distributed nodes.

**Phases**:
1. **Prepare**: Proposer sends prepare(n) to acceptors
2. **Promise**: Acceptors promise not to accept proposals < n
3. **Accept**: Proposer sends accept(n, value) to acceptors
4. **Accepted**: Acceptors accept if they haven't promised higher n

**Problem**: Complex to implement correctly, difficult to understand.

### 3.3.2 Raft

**Purpose**: Understandable consensus algorithm (alternative to Paxos).

**Key Concepts**:
- **Leader Election**: One node elected as leader
- **Log Replication**: Leader replicates log to followers
- **Safety**: If server applied log entry, all servers will apply same entry at same index

**States**:
- **Follower**: Passive, responds to RPCs
- **Candidate**: Requests votes during election
- **Leader**: Handles client requests, replicates log

**Leader Election**:
```typescript
enum NodeState {
    Follower,
    Candidate,
    Leader
}

class RaftNode {
    private state: NodeState = NodeState.Follower;
    private currentTerm: number = 0;
    private votedFor: string | null = null;
    private log: LogEntry[] = [];
    private electionTimeout: number;

    private resetElectionTimeout() {
        this.electionTimeout = Date.now() +
            150 + Math.random() * 150; // 150-300ms
    }

    private startElection() {
        this.state = NodeState.Candidate;
        this.currentTerm++;
        this.votedFor = this.nodeId;

        let votesReceived = 1; // Vote for self

        // Request votes from other nodes
        for (const node of this.otherNodes) {
            const response = node.requestVote({
                term: this.currentTerm,
                candidateId: this.nodeId,
                lastLogIndex: this.log.length - 1,
                lastLogTerm: this.log[this.log.length - 1]?.term || 0
            });

            if (response.voteGranted) {
                votesReceived++;

                if (votesReceived > this.otherNodes.length / 2) {
                    this.becomeLeader();
                    return;
                }
            }
        }
    }

    private becomeLeader() {
        this.state = NodeState.Leader;
        console.log(`${this.nodeId} became leader for term ${this.currentTerm}`);

        // Send heartbeats to maintain leadership
        this.sendHeartbeats();
    }

    requestVote(request: VoteRequest): VoteResponse {
        if (request.term < this.currentTerm) {
            return { term: this.currentTerm, voteGranted: false };
        }

        if (request.term > this.currentTerm) {
            this.currentTerm = request.term;
            this.votedFor = null;
            this.state = NodeState.Follower;
        }

        if (this.votedFor === null || this.votedFor === request.candidateId) {
            // Check if candidate's log is at least as up-to-date
            if (this.isLogUpToDate(request)) {
                this.votedFor = request.candidateId;
                this.resetElectionTimeout();
                return { term: this.currentTerm, voteGranted: true };
            }
        }

        return { term: this.currentTerm, voteGranted: false };
    }
}
```

**Log Replication**:
```typescript
interface LogEntry {
    term: number;
    command: any;
}

class RaftNode {
    private log: LogEntry[] = [];
    private commitIndex: number = 0;
    private lastApplied: number = 0;

    // Leader only
    private nextIndex: Map<string, number> = new Map();
    private matchIndex: Map<string, number> = new Map();

    appendEntries(request: AppendEntriesRequest): AppendEntriesResponse {
        if (request.term < this.currentTerm) {
            return { term: this.currentTerm, success: false };
        }

        this.resetElectionTimeout();

        // Find conflicting entry
        if (request.prevLogIndex >= 0) {
            if (this.log.length <= request.prevLogIndex ||
                this.log[request.prevLogIndex].term !== request.prevLogTerm) {
                return { term: this.currentTerm, success: false };
            }
        }

        // Append new entries
        for (let i = 0; i < request.entries.length; i++) {
            const index = request.prevLogIndex + 1 + i;

            if (this.log.length <= index) {
                this.log.push(request.entries[i]);
            } else if (this.log[index].term !== request.entries[i].term) {
                // Conflict: remove conflicting entries and append
                this.log = this.log.slice(0, index);
                this.log.push(request.entries[i]);
            }
        }

        // Update commit index
        if (request.leaderCommit > this.commitIndex) {
            this.commitIndex = Math.min(
                request.leaderCommit,
                this.log.length - 1
            );
        }

        return { term: this.currentTerm, success: true };
    }

    // Leader sends entries to followers
    replicateLog() {
        for (const follower of this.otherNodes) {
            const nextIdx = this.nextIndex.get(follower.id) || 0;
            const prevLogIndex = nextIdx - 1;
            const prevLogTerm = prevLogIndex >= 0
                ? this.log[prevLogIndex].term
                : 0;

            const entries = this.log.slice(nextIdx);

            const response = follower.appendEntries({
                term: this.currentTerm,
                leaderId: this.nodeId,
                prevLogIndex,
                prevLogTerm,
                entries,
                leaderCommit: this.commitIndex
            });

            if (response.success) {
                this.nextIndex.set(follower.id, nextIdx + entries.length);
                this.matchIndex.set(follower.id, nextIdx + entries.length - 1);

                // Update commit index if majority replicated
                this.updateCommitIndex();
            } else {
                // Decrement nextIndex and retry
                this.nextIndex.set(follower.id, nextIdx - 1);
            }
        }
    }

    private updateCommitIndex() {
        // Find N such that majority of matchIndex[i] >= N
        for (let n = this.log.length - 1; n > this.commitIndex; n--) {
            if (this.log[n].term !== this.currentTerm) {
                continue;
            }

            let count = 1; // Count self
            for (const [_, matchIdx] of this.matchIndex) {
                if (matchIdx >= n) {
                    count++;
                }
            }

            if (count > (this.otherNodes.length + 1) / 2) {
                this.commitIndex = n;
                break;
            }
        }
    }
}
```

## 3.4 Distributed Transactions

### 3.4.1 Two-Phase Commit (2PC)

**Purpose**: Atomic commitment across distributed resources.

**Phases**:
1. **Prepare Phase**: Coordinator asks all participants to prepare
2. **Commit Phase**: If all prepared, commit; otherwise abort

**Problems**:
- Blocking: If coordinator fails, participants blocked
- Not partition-tolerant

```typescript
enum TransactionState {
    Init,
    Preparing,
    Prepared,
    Committed,
    Aborted
}

class TwoPhaseCommitCoordinator {
    private state: TransactionState = TransactionState.Init;

    async commit(participants: Participant[]): Promise<boolean> {
        // Phase 1: Prepare
        this.state = TransactionState.Preparing;

        const preparePromises = participants.map(p => p.prepare());
        const prepareResults = await Promise.all(preparePromises);

        if (prepareResults.every(r => r === true)) {
            // All prepared, commit
            this.state = TransactionState.Prepared;

            // Phase 2: Commit
            const commitPromises = participants.map(p => p.commit());
            await Promise.all(commitPromises);

            this.state = TransactionState.Committed;
            return true;
        } else {
            // Some failed, abort
            const abortPromises = participants.map(p => p.abort());
            await Promise.all(abortPromises);

            this.state = TransactionState.Aborted;
            return false;
        }
    }
}

class Participant {
    private transaction: any = null;

    async prepare(): Promise<boolean> {
        try {
            // Begin transaction
            this.transaction = await db.beginTransaction();

            // Perform operations
            await this.transaction.execute();

            // Write to WAL (Write-Ahead Log)
            await this.writeToWAL('prepared');

            return true;
        } catch (error) {
            return false;
        }
    }

    async commit(): Promise<void> {
        await this.transaction.commit();
        await this.writeToWAL('committed');
    }

    async abort(): Promise<void> {
        await this.transaction.rollback();
        await this.writeToWAL('aborted');
    }
}
```

### 3.4.2 Saga Pattern

**Purpose**: Manage distributed transactions using sequence of local transactions.

**Types**:
- **Choreography**: Each service produces events that trigger next step
- **Orchestration**: Central coordinator directs saga

**Compensation**: Each step has compensating transaction to undo.

```typescript
// Choreography-based Saga
class OrderService {
    async createOrder(orderData: any) {
        const order = await db.orders.create(orderData);

        // Emit event
        eventBus.publish('OrderCreated', {
            orderId: order.id,
            items: order.items,
            customerId: order.customerId
        });

        return order;
    }
}

class InventoryService {
    constructor() {
        // Listen for OrderCreated event
        eventBus.subscribe('OrderCreated', this.reserveInventory.bind(this));
    }

    async reserveInventory(event: OrderCreatedEvent) {
        try {
            await db.inventory.reserve(event.items);

            // Success: emit event
            eventBus.publish('InventoryReserved', {
                orderId: event.orderId
            });
        } catch (error) {
            // Failure: emit compensation event
            eventBus.publish('InventoryReservationFailed', {
                orderId: event.orderId,
                reason: error.message
            });
        }
    }
}

class PaymentService {
    constructor() {
        eventBus.subscribe('InventoryReserved', this.processPayment.bind(this));
    }

    async processPayment(event: InventoryReservedEvent) {
        try {
            await stripeAPI.charge(event.orderId);

            eventBus.publish('PaymentProcessed', {
                orderId: event.orderId
            });
        } catch (error) {
            // Failure: trigger compensation
            eventBus.publish('PaymentFailed', {
                orderId: event.orderId
            });
        }
    }
}

// Compensation handlers
class OrderService {
    constructor() {
        eventBus.subscribe('PaymentFailed', this.cancelOrder.bind(this));
    }

    async cancelOrder(event: PaymentFailedEvent) {
        await db.orders.update(event.orderId, { status: 'cancelled' });
        eventBus.publish('OrderCancelled', { orderId: event.orderId });
    }
}

class InventoryService {
    constructor() {
        eventBus.subscribe('OrderCancelled', this.releaseInventory.bind(this));
    }

    async releaseInventory(event: OrderCancelledEvent) {
        await db.inventory.release(event.orderId);
    }
}
```

**Orchestration-based Saga**:
```typescript
class OrderSagaOrchestrator {
    async executeOrderSaga(orderData: any) {
        const sagaState = {
            orderId: null,
            inventoryReserved: false,
            paymentProcessed: false
        };

        try {
            // Step 1: Create order
            const order = await orderService.createOrder(orderData);
            sagaState.orderId = order.id;

            // Step 2: Reserve inventory
            await inventoryService.reserve(order.items);
            sagaState.inventoryReserved = true;

            // Step 3: Process payment
            await paymentService.charge(order);
            sagaState.paymentProcessed = true;

            // Step 4: Complete order
            await orderService.complete(order.id);

            return { success: true, orderId: order.id };

        } catch (error) {
            // Compensation in reverse order
            if (sagaState.paymentProcessed) {
                await paymentService.refund(sagaState.orderId);
            }

            if (sagaState.inventoryReserved) {
                await inventoryService.release(sagaState.orderId);
            }

            if (sagaState.orderId) {
                await orderService.cancel(sagaState.orderId);
            }

            return { success: false, error: error.message };
        }
    }
}
```

## 3.5 Microservices Patterns

### 3.5.1 Service Discovery

**Problem**: Services need to find each other in dynamic environment.

**Solutions**:

**Client-Side Discovery**:
```typescript
class ServiceRegistry {
    private services = new Map<string, ServiceInstance[]>();

    register(name: string, instance: ServiceInstance): void {
        if (!this.services.has(name)) {
            this.services.set(name, []);
        }
        this.services.get(name)!.push(instance);
    }

    deregister(name: string, instanceId: string): void {
        const instances = this.services.get(name);
        if (instances) {
            this.services.set(
                name,
                instances.filter(i => i.id !== instanceId)
            );
        }
    }

    getInstances(name: string): ServiceInstance[] {
        return this.services.get(name) || [];
    }
}

class LoadBalancer {
    private currentIndex = 0;

    // Round-robin
    selectInstance(instances: ServiceInstance[]): ServiceInstance {
        if (instances.length === 0) {
            throw new Error('No instances available');
        }

        const instance = instances[this.currentIndex];
        this.currentIndex = (this.currentIndex + 1) % instances.length;
        return instance;
    }
}

class ServiceClient {
    constructor(
        private registry: ServiceRegistry,
        private loadBalancer: LoadBalancer
    ) {}

    async call(serviceName: string, method: string, params: any) {
        const instances = this.registry.getInstances(serviceName);
        const instance = this.loadBalancer.selectInstance(instances);

        return fetch(`${instance.url}/${method}`, {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
}
```

**Server-Side Discovery** (using API Gateway):
```typescript
class APIGateway {
    private routes = new Map<string, ServiceInfo>();

    registerRoute(path: string, service: ServiceInfo): void {
        this.routes.set(path, service);
    }

    async handleRequest(req: Request): Promise<Response> {
        const path = this.extractPath(req.url);
        const service = this.routes.get(path);

        if (!service) {
            return new Response('Not Found', { status: 404 });
        }

        // Forward to service
        const response = await fetch(service.url, {
            method: req.method,
            headers: req.headers,
            body: req.body
        });

        return response;
    }
}
```

### 3.5.2 Circuit Breaker

**Purpose**: Prevent cascading failures by stopping calls to failing service.

**States**:
- **Closed**: Normal operation, requests pass through
- **Open**: Too many failures, requests fail immediately
- **Half-Open**: Test if service recovered

```typescript
enum CircuitState {
    Closed,
    Open,
    HalfOpen
}

class CircuitBreaker {
    private state: CircuitState = CircuitState.Closed;
    private failureCount: number = 0;
    private successCount: number = 0;
    private lastFailureTime: number = 0;

    constructor(
        private failureThreshold: number = 5,
        private timeout: number = 60000,  // 1 minute
        private retryTimePeriod: number = 30000  // 30 seconds
    ) {}

    async call<T>(fn: () => Promise<T>): Promise<T> {
        if (this.state === CircuitState.Open) {
            // Check if should try half-open
            if (Date.now() - this.lastFailureTime > this.retryTimePeriod) {
                this.state = CircuitState.HalfOpen;
                console.log('Circuit breaker: Half-Open');
            } else {
                throw new Error('Circuit breaker: Open');
            }
        }

        try {
            const result = await this.executeWithTimeout(fn);

            // Success
            this.onSuccess();
            return result;

        } catch (error) {
            // Failure
            this.onFailure();
            throw error;
        }
    }

    private async executeWithTimeout<T>(fn: () => Promise<T>): Promise<T> {
        return Promise.race([
            fn(),
            new Promise<never>((_, reject) =>
                setTimeout(() => reject(new Error('Timeout')), this.timeout)
            )
        ]);
    }

    private onSuccess(): void {
        this.failureCount = 0;

        if (this.state === CircuitState.HalfOpen) {
            this.successCount++;

            if (this.successCount >= 2) {
                this.state = CircuitState.Closed;
                this.successCount = 0;
                console.log('Circuit breaker: Closed');
            }
        }
    }

    private onFailure(): void {
        this.failureCount++;
        this.lastFailureTime = Date.now();

        if (this.failureCount >= this.failureThreshold) {
            this.state = CircuitState.Open;
            console.log('Circuit breaker: Open');
        }
    }
}

// Usage
const breaker = new CircuitBreaker();

async function callExternalService() {
    return breaker.call(async () => {
        const response = await fetch('https://api.example.com/data');
        return response.json();
    });
}
```

### 3.5.3 API Gateway Pattern

**Purpose**: Single entry point for all clients.

**Responsibilities**:
- Routing
- Authentication/Authorization
- Rate limiting
- Request/Response transformation
- Load balancing
- Caching

```typescript
class APIGateway {
    private rateLimiter: RateLimiter;
    private cache: Cache;
    private authService: AuthService;

    async handleRequest(req: Request): Promise<Response> {
        try {
            // 1. Authentication
            const user = await this.authService.authenticate(req);
            if (!user) {
                return new Response('Unauthorized', { status: 401 });
            }

            // 2. Rate limiting
            if (!await this.rateLimiter.allow(user.id)) {
                return new Response('Too Many Requests', { status: 429 });
            }

            // 3. Check cache
            const cacheKey = this.getCacheKey(req);
            const cached = await this.cache.get(cacheKey);
            if (cached) {
                return new Response(cached, { status: 200 });
            }

            // 4. Route to service
            const service = this.routeRequest(req);
            const response = await this.forwardRequest(service, req);

            // 5. Cache response
            if (response.ok) {
                await this.cache.set(cacheKey, await response.text());
            }

            return response;

        } catch (error) {
            console.error('Gateway error:', error);
            return new Response('Internal Server Error', { status: 500 });
        }
    }

    private routeRequest(req: Request): ServiceInfo {
        const path = new URL(req.url).pathname;

        if (path.startsWith('/users')) {
            return { name: 'user-service', url: 'http://users:3000' };
        } else if (path.startsWith('/orders')) {
            return { name: 'order-service', url: 'http://orders:3000' };
        } else {
            throw new Error('No route found');
        }
    }
}
```


---

# PART 4: DEBUGGING & PROBLEM SOLVING

## 4.1 Scientific Method for Debugging

### 4.1.1 The Process

**1. Observe**: Gather symptoms and data
**2. Hypothesize**: Form theories about causes
**3. Experiment**: Test hypotheses systematically
**4. Analyze**: Evaluate results
**5. Conclude**: Identify root cause
**6. Fix**: Implement solution
**7. Verify**: Ensure fix works

### 4.1.2 Systematic Observation

```typescript
class BugReport {
    // WHAT is happening?
    symptom: string;

    // WHEN does it happen?
    frequency: 'always' | 'sometimes' | 'rarely';
    trigger: string;
    firstOccurrence: Date;

    // WHERE does it happen?
    environment: 'production' | 'staging' | 'development';
    affectedUsers: string[];
    affectedComponents: string[];

    // HOW severe?
    impact: 'critical' | 'major' | 'minor';
    workaround: string | null;

    // Supporting data
    logs: string[];
    screenshots: string[];
    steps: string[];
    expectedBehavior: string;
    actualBehavior: string;
}
```

**Example Investigation**:
```
SYMPTOM: Users report checkout failing with "Payment error"

OBSERVE:
- Error happens for 30% of users
- Started yesterday at 3 PM
- Only affects credit card payments
- PayPal works fine
- Error message: "Payment gateway timeout"
- Happens more frequently during peak hours

HYPOTHESIZE:
1. Payment gateway is overloaded
2. Network issues between server and gateway
3. Recent code deployment broke something
4. Rate limiting from payment provider

EXPERIMENT:
Test 1: Check payment gateway status page
Result: No reported issues

Test 2: Review recent deployments
Result: Code deployed yesterday at 2:45 PM

Test 3: Check timeout configuration
Result: Timeout set to 5 seconds

Test 4: Monitor payment gateway response times
Result: Average response time is 7 seconds during peak hours

ANALYZE:
- Problem started after deployment
- Timeout (5s) is less than gateway response time (7s)
- Previous timeout was 10 seconds
- Recent "optimization" reduced timeout

CONCLUDE:
Deployment reduced timeout too aggressively.
Gateway response times are legitimate, not errors.

FIX:
Increase timeout to 15 seconds with circuit breaker.

VERIFY:
- Monitor error rate: Dropped to 0%
- Monitor response times: All payments succeed
- Add alerting for slow gateway responses
```

## 4.2 Debugging Techniques

### 4.2.1 Binary Search Debugging

**Principle**: Divide search space in half repeatedly.

**Git Bisect**:
```bash
# Find commit that introduced bug
git bisect start
git bisect bad HEAD  # Current version is broken
git bisect good v1.0  # v1.0 worked

# Git checks out commit in middle
# Test it
# If broken:
git bisect bad

# If works:
git bisect good

# Git narrows down automatically
# Eventually finds first bad commit
```

**Binary Search in Code**:
```python
def find_bug_in_range(start, end):
    """
    When bug occurs somewhere in processing range [start, end],
    use binary search to find where.
    """
    if start == end:
        print(f"Bug at index {start}")
        return start

    mid = (start + end) // 2

    # Process first half
    result1 = process_data(data[start:mid])
    if has_bug(result1):
        return find_bug_in_range(start, mid)

    # Bug must be in second half
    return find_bug_in_range(mid + 1, end)
```

### 4.2.2 Rubber Duck Debugging

**Method**: Explain code line-by-line to inanimate object.

**Why It Works**: Forces you to:
- Articulate assumptions
- Notice inconsistencies
- Simplify complex logic
- Question "obvious" things

**Example**:
```
"So this function calculates the discount...
It takes the order total...
Then it multiplies by the discount percentage...
Oh wait, the discount is stored as 0.15 not 15...
So I'm applying 0.15% instead of 15%...
I need to multiply by 100... no wait, the discount is ALREADY a decimal...
The bug is elsewhere... let me check where discount comes from..."
```

### 4.2.3 Print Debugging

**Effective Logging**:
```typescript
// BAD: Uninformative logging
console.log('here');
console.log('x:', x);

// GOOD: Contextual logging
console.log('[calculateDiscount] Input:', {
    orderTotal: order.total,
    customerTier: customer.tier,
    promoCode: order.promoCode
});

const discount = this.getDiscount(customer);
console.log('[calculateDiscount] Discount calculated:', discount);

const finalPrice = order.total - discount;
console.log('[calculateDiscount] Output:', {
    originalPrice: order.total,
    discount: discount,
    finalPrice: finalPrice
});

// BETTER: Structured logging
this.logger.debug('calculateDiscount', {
    input: {
        orderTotal: order.total,
        customerTier: customer.tier
    },
    calculated: {
        discount: discount,
        finalPrice: finalPrice
    },
    timestamp: Date.now()
});
```

**Strategic Logging**:
```python
def complex_algorithm(data):
    logger.info(f"Starting complex_algorithm with {len(data)} items")

    # Log entry to each major section
    logger.debug("Step 1: Preprocessing")
    preprocessed = preprocess(data)
    logger.debug(f"Preprocessed: {len(preprocessed)} items")

    logger.debug("Step 2: Main processing")
    for i, item in enumerate(preprocessed):
        result = process(item)

        # Log interesting data points
        if result.is_anomaly():
            logger.warning(f"Anomaly at index {i}: {result}")

        # Log every N iterations for large datasets
        if i % 1000 == 0:
            logger.info(f"Processed {i}/{len(preprocessed)} items")

    logger.debug("Step 3: Postprocessing")
    final = postprocess(result)

    logger.info(f"Completed complex_algorithm: {final.summary()}")
    return final
```

### 4.2.4 Debugger Usage

**Breakpoint Strategies**:
```python
# Conditional breakpoint: Only pause when condition true
# Example in Python debugger
import pdb

def process_orders(orders):
    for order in orders:
        # Only break for large orders
        if order.total > 10000:
            pdb.set_trace()  # Debugger pauses here

        process(order)
```

**Watch Expressions**:
```javascript
// In Chrome DevTools or VS Code:
// Set watch expressions to monitor values

// Instead of setting breakpoints everywhere, watch:
// - user.isAuthenticated
// - cart.items.length
// - response.status

// Breakpoint only triggers when watch expression changes
```

**Call Stack Analysis**:
```
When debugger pauses, examine call stack:

1. process_payment()      <- Current function (where error occurred)
2. checkout()             <- Caller
3. handle_submit()        <- Called by
4. event_handler()        <- Event source

Working backwards through stack often reveals issue.
```

## 4.3 Root Cause Analysis

### 4.3.1 Five Whys Technique

**Method**: Ask "why" five times to find root cause.

**Example**:
```
PROBLEM: Production server crashed

Why? - Out of memory error

Why? - Memory leak in user session management

Why? - Sessions not being cleaned up

Why? - Cleanup job not running

Why? - Cleanup job not scheduled in production

Why? - Missing configuration in production deployment

ROOT CAUSE: Deployment checklist incomplete
```

### 4.3.2 Fault Tree Analysis

**Method**: Work backwards from failure to identify all possible causes.

```
                    Server Crashed
                          |
         +----------------+----------------+
         |                |                |
    Out of Memory    CPU Overload    Disk Full
         |                |                |
    +-----------+    +----------+     +--------+
    |           |    |          |     |        |
Memory Leak  Large   Attack   Bug   Logs   Uploads
             Dataset
```

### 4.3.3 Differential Diagnosis

**Method**: Compare working vs broken states.

```python
class DifferentialDebugger:
    def compare_states(self, working, broken):
        """Compare working and broken system states"""
        differences = {
            'environment': self.compare_env(working.env, broken.env),
            'configuration': self.compare_config(working.config, broken.config),
            'dependencies': self.compare_deps(working.deps, broken.deps),
            'data': self.compare_data(working.data, broken.data),
            'code': self.compare_code(working.version, broken.version)
        }

        for category, diff in differences.items():
            if diff:
                print(f"\n{category.upper()} DIFFERENCES:")
                for item in diff:
                    print(f"  - {item}")

        return differences

    def compare_env(self, env1, env2):
        """Compare environment variables"""
        diff = []
        all_keys = set(env1.keys()) | set(env2.keys())

        for key in all_keys:
            val1 = env1.get(key, 'MISSING')
            val2 = env2.get(key, 'MISSING')

            if val1 != val2:
                diff.append(f"{key}: '{val1}' vs '{val2}'")

        return diff
```

**Example**:
```
WORKING (Staging):
- Node version: 18.17.0
- Database: PostgreSQL 14.2
- Redis: 7.0.11
- Environment: PRODUCTION=false

BROKEN (Production):
- Node version: 18.17.0
- Database: PostgreSQL 14.2
- Redis: 7.0.11
- Environment: PRODUCTION=true

KEY DIFFERENCE: PRODUCTION flag
Investigation: Code behaves differently when PRODUCTION=true
Bug: Production mode disables detailed error messages, hiding real error
```

## 4.4 Performance Debugging

### 4.4.1 Profiling

**CPU Profiling**:
```javascript
// Node.js profiling
console.profile('myFunction');
myFunction();
console.profileEnd();

// Chrome DevTools profiling
// 1. Open DevTools > Performance
// 2. Click Record
// 3. Perform action
// 4. Stop recording
// 5. Analyze flame graph
```

**Flame Graph Analysis**:
```
     main()                                 [100%]
       |
       +-- processData()                    [80%]  <-- HOTSPOT
       |     |
       |     +-- validateInput()            [10%]
       |     +-- transform()                [60%]  <-- REAL PROBLEM
       |     +-- save()                     [10%]
       |
       +-- sendNotification()               [20%]
```

**Memory Profiling**:
```javascript
// Node.js memory usage
const before = process.memoryUsage();

performOperation();

const after = process.memoryUsage();

console.log({
    heapUsed: (after.heapUsed - before.heapUsed) / 1024 / 1024 + ' MB',
    external: (after.external - before.external) / 1024 / 1024 + ' MB'
});

// Chrome DevTools memory profiling
// 1. Open DevTools > Memory
// 2. Take heap snapshot before operation
// 3. Perform operation
// 4. Take heap snapshot after
// 5. Compare snapshots to find leaks
```

### 4.4.2 Performance Metrics

```typescript
class PerformanceMonitor {
    private metrics = new Map<string, number[]>();

    measure<T>(name: string, fn: () => T): T {
        const start = performance.now();

        try {
            return fn();
        } finally {
            const duration = performance.now() - start;

            if (!this.metrics.has(name)) {
                this.metrics.set(name, []);
            }

            this.metrics.get(name)!.push(duration);
        }
    }

    async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
        const start = performance.now();

        try {
            return await fn();
        } finally {
            const duration = performance.now() - start;

            if (!this.metrics.has(name)) {
                this.metrics.set(name, []);
            }

            this.metrics.get(name)!.push(duration);
        }
    }

    getStats(name: string) {
        const measurements = this.metrics.get(name) || [];

        if (measurements.length === 0) {
            return null;
        }

        const sorted = measurements.slice().sort((a, b) => a - b);
        const sum = sorted.reduce((a, b) => a + b, 0);

        return {
            count: measurements.length,
            mean: sum / measurements.length,
            median: sorted[Math.floor(sorted.length / 2)],
            p95: sorted[Math.floor(sorted.length * 0.95)],
            p99: sorted[Math.floor(sorted.length * 0.99)],
            min: sorted[0],
            max: sorted[sorted.length - 1]
        };
    }

    report() {
        console.log('\n=== Performance Report ===\n');

        for (const [name, _] of this.metrics) {
            const stats = this.getStats(name)!;

            console.log(`${name}:`);
            console.log(`  Calls: ${stats.count}`);
            console.log(`  Mean:  ${stats.mean.toFixed(2)}ms`);
            console.log(`  P50:   ${stats.median.toFixed(2)}ms`);
            console.log(`  P95:   ${stats.p95.toFixed(2)}ms`);
            console.log(`  P99:   ${stats.p99.toFixed(2)}ms`);
            console.log(`  Range: ${stats.min.toFixed(2)}ms - ${stats.max.toFixed(2)}ms\n`);
        }
    }
}

// Usage
const monitor = new PerformanceMonitor();

// Measure synchronous function
const result = monitor.measure('database-query', () => {
    return db.query('SELECT * FROM users');
});

// Measure async function
const users = await monitor.measureAsync('api-call', async () => {
    return fetch('/api/users').then(r => r.json());
});

// Print report
monitor.report();
```

### 4.4.3 N+1 Query Problem

**Problem**: One query followed by N queries in a loop.

```typescript
// BAD: N+1 queries
async function getBlogPostsWithAuthors() {
    const posts = await db.posts.findAll();  // 1 query

    for (const post of posts) {
        post.author = await db.users.findById(post.authorId);  // N queries!
    }

    return posts;
}

// Total queries: 1 + N (if N=100, that's 101 queries!)

// GOOD: Eager loading
async function getBlogPostsWithAuthors() {
    const posts = await db.posts.findAll({
        include: [{ model: db.users, as: 'author' }]
    });

    return posts;
}

// Total queries: 1 (joins in database)

// GOOD: Manual batching
async function getBlogPostsWithAuthors() {
    const posts = await db.posts.findAll();  // 1 query

    const authorIds = [...new Set(posts.map(p => p.authorId))];
    const authors = await db.users.findByIds(authorIds);  // 1 query

    const authorMap = new Map(authors.map(a => [a.id, a]));

    for (const post of posts) {
        post.author = authorMap.get(post.authorId);
    }

    return posts;
}

// Total queries: 2 (regardless of N)
```

**DataLoader Pattern** (batching and caching):
```typescript
class DataLoader<K, V> {
    private batchLoadFn: (keys: K[]) => Promise<V[]>;
    private cache = new Map<K, Promise<V>>();
    private batch: {keys: K[], resolve: (value: V) => void, reject: (error: any) => void}[] = [];
    private batchScheduled = false;

    constructor(batchLoadFn: (keys: K[]) => Promise<V[]>) {
        this.batchLoadFn = batchLoadFn;
    }

    load(key: K): Promise<V> {
        // Check cache
        if (this.cache.has(key)) {
            return this.cache.get(key)!;
        }

        // Create promise and add to batch
        const promise = new Promise<V>((resolve, reject) => {
            this.batch.push({keys: [key], resolve, reject});

            if (!this.batchScheduled) {
                this.batchScheduled = true;
                process.nextTick(() => this.dispatchBatch());
            }
        });

        this.cache.set(key, promise);
        return promise;
    }

    private async dispatchBatch() {
        this.batchScheduled = false;

        const batch = this.batch;
        this.batch = [];

        const keys = batch.flatMap(b => b.keys);

        try {
            const values = await this.batchLoadFn(keys);

            batch.forEach((item, index) => {
                item.resolve(values[index]);
            });
        } catch (error) {
            batch.forEach(item => {
                item.reject(error);
            });
        }
    }

    clear(key: K): void {
        this.cache.delete(key);
    }

    clearAll(): void {
        this.cache.clear();
    }
}

// Usage
const userLoader = new DataLoader(async (ids: string[]) => {
    console.log('Batch loading users:', ids);
    return db.users.findByIds(ids);
});

async function getBlogPostsWithAuthors() {
    const posts = await db.posts.findAll();

    // These calls are automatically batched!
    for (const post of posts) {
        post.author = await userLoader.load(post.authorId);
    }

    return posts;
}

// Output: "Batch loading users: ['1', '2', '3', ...]"
// Only 2 queries total, but code looks like individual loads!
```

---

# PART 5: TESTING METHODOLOGIES

## 5.1 Test-Driven Development (TDD)

### 5.1.1 The TDD Cycle

**Red-Green-Refactor**:
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code without changing behavior

### 5.1.2 TDD Example

```typescript
// Step 1: RED - Write failing test
describe('calculateShippingCost', () => {
    it('should calculate cost for domestic shipping', () => {
        const order = {
            items: [{weight: 1.5, quantity: 2}],
            destination: 'domestic'
        };

        const cost = calculateShippingCost(order);

        expect(cost).toBe(15); // $5 per kg * 3kg
    });
});

// Test fails: calculateShippingCost is not defined

// Step 2: GREEN - Minimal code to pass
function calculateShippingCost(order) {
    return 15; // Hardcoded to pass test
}

// Test passes, but implementation is wrong

// Step 3: Write more tests (RED again)
describe('calculateShippingCost', () => {
    it('should calculate cost for domestic shipping', () => {
        const order = {
            items: [{weight: 1.5, quantity: 2}],
            destination: 'domestic'
        };

        expect(calculateShippingCost(order)).toBe(15);
    });

    it('should calculate cost for international shipping', () => {
        const order = {
            items: [{weight: 1.5, quantity: 2}],
            destination: 'international'
        };

        expect(calculateShippingCost(order)).toBe(30); // $10 per kg
    });
});

// Second test fails

// Step 4: GREEN - Real implementation
function calculateShippingCost(order) {
    const totalWeight = order.items.reduce(
        (sum, item) => sum + item.weight * item.quantity,
        0
    );

    const ratePerKg = order.destination === 'international' ? 10 : 5;

    return totalWeight * ratePerKg;
}

// Both tests pass

// Step 5: REFACTOR - Improve code
const SHIPPING_RATES = {
    domestic: 5,
    international: 10
};

function calculateShippingCost(order) {
    const totalWeight = order.items.reduce(
        (sum, item) => sum + item.weight * item.quantity,
        0
    );

    return totalWeight * SHIPPING_RATES[order.destination];
}

// Tests still pass, code is cleaner

// Step 6: Add edge cases
describe('calculateShippingCost', () => {
    // ... existing tests ...

    it('should handle empty order', () => {
        const order = {items: [], destination: 'domestic'};
        expect(calculateShippingCost(order)).toBe(0);
    });

    it('should throw error for invalid destination', () => {
        const order = {
            items: [{weight: 1, quantity: 1}],
            destination: 'mars'
        };
        expect(() => calculateShippingCost(order)).toThrow();
    });
});

// Add error handling
function calculateShippingCost(order) {
    const rate = SHIPPING_RATES[order.destination];

    if (rate === undefined) {
        throw new Error(`Invalid destination: ${order.destination}`);
    }

    const totalWeight = order.items.reduce(
        (sum, item) => sum + item.weight * item.quantity,
        0
    );

    return totalWeight * rate;
}
```

### 5.1.3 Benefits of TDD

1. **Better Design**: Writing tests first forces good design
2. **Confidence**: Know code works before shipping
3. **Documentation**: Tests document expected behavior
4. **Regression Prevention**: Catch bugs early
5. **Refactoring Safety**: Can refactor without fear

### 5.1.4 TDD Anti-Patterns

**Testing Implementation Details**:
```typescript
// BAD: Testing internal implementation
it('should call validateEmail method', () => {
    const spy = jest.spyOn(userService, 'validateEmail');
    userService.createUser({email: 'test@example.com'});
    expect(spy).toHaveBeenCalled();
});

// GOOD: Testing behavior
it('should reject invalid email', () => {
    expect(() => userService.createUser({email: 'invalid'}))
        .toThrow('Invalid email');
});
```

**Over-Mocking**:
```typescript
// BAD: Mock everything
it('should create user', () => {
    const mockValidator = jest.fn().mockReturnValue(true);
    const mockHasher = jest.fn().mockReturnValue('hashed');
    const mockRepo = {save: jest.fn().mockResolvedValue({id: 1})};
    const mockEmailer = {send: jest.fn()};

    const service = new UserService(
        mockValidator,
        mockHasher,
        mockRepo,
        mockEmailer
    );

    // Test tells us nothing about real behavior!
});

// GOOD: Mock only external dependencies
it('should create user', () => {
    const mockRepo = {save: jest.fn().mockResolvedValue({id: 1})};
    const mockEmailer = {send: jest.fn()};

    // Use real validator and hasher
    const service = new UserService(
        new RealValidator(),
        new RealHasher(),
        mockRepo,
        mockEmailer
    );

    // Tests real validation and hashing logic
});
```

## 5.2 Behavior-Driven Development (BDD)

### 5.2.1 Given-When-Then

**Format**:
- **Given**: Initial context
- **When**: Action occurs
- **Then**: Expected outcome

```typescript
describe('Shopping Cart', () => {
    describe('Adding items', () => {
        it('should add item to empty cart', () => {
            // GIVEN an empty cart
            const cart = new ShoppingCart();

            // WHEN adding an item
            cart.addItem({id: '1', name: 'Book', price: 10});

            // THEN cart should contain item
            expect(cart.getItems()).toHaveLength(1);
            expect(cart.getTotal()).toBe(10);
        });

        it('should increase quantity for duplicate items', () => {
            // GIVEN cart with one book
            const cart = new ShoppingCart();
            cart.addItem({id: '1', name: 'Book', price: 10});

            // WHEN adding same book again
            cart.addItem({id: '1', name: 'Book', price: 10});

            // THEN quantity should increase
            expect(cart.getItems()).toHaveLength(1);
            expect(cart.getItems()[0].quantity).toBe(2);
            expect(cart.getTotal()).toBe(20);
        });
    });

    describe('Applying discounts', () => {
        it('should apply percentage discount to cart total', () => {
            // GIVEN cart with $100 of items
            const cart = new ShoppingCart();
            cart.addItem({id: '1', name: 'Book', price: 50});
            cart.addItem({id: '2', name: 'Pen', price: 50});

            // WHEN applying 10% discount
            cart.applyDiscount({type: 'percentage', value: 10});

            // THEN total should be $90
            expect(cart.getTotal()).toBe(90);
        });
    });
});
```

### 5.2.2 Cucumber/Gherkin

**Feature Files**:
```gherkin
Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access my dashboard

  Scenario: Successful login with valid credentials
    Given I am on the login page
    And I am not logged in
    When I enter "user@example.com" in the email field
    And I enter "password123" in the password field
    And I click the "Login" button
    Then I should be redirected to the dashboard
    And I should see "Welcome back!" message

  Scenario: Failed login with invalid password
    Given I am on the login page
    When I enter "user@example.com" in the email field
    And I enter "wrongpassword" in the password field
    And I click the "Login" button
    Then I should see "Invalid credentials" error message
    And I should remain on the login page

  Scenario Outline: Failed login with invalid inputs
    Given I am on the login page
    When I enter "<email>" in the email field
    And I enter "<password>" in the password field
    And I click the "Login" button
    Then I should see "<error>" error message

    Examples:
      | email              | password    | error                    |
      | invalid-email      | password123 | Invalid email format     |
      | user@example.com   |             | Password required        |
      |                    | password123 | Email required           |
```

**Step Definitions**:
```typescript
import { Given, When, Then } from '@cucumber/cucumber';

Given('I am on the login page', async function() {
    await this.page.goto('http://localhost:3000/login');
});

Given('I am not logged in', async function() {
    await this.page.context().clearCookies();
});

When('I enter {string} in the email field', async function(email: string) {
    await this.page.fill('input[name="email"]', email);
});

When('I enter {string} in the password field', async function(password: string) {
    await this.page.fill('input[name="password"]', password);
});

When('I click the {string} button', async function(buttonText: string) {
    await this.page.click(`button:text("${buttonText}")`);
});

Then('I should be redirected to the dashboard', async function() {
    await this.page.waitForURL('**/dashboard');
    expect(this.page.url()).toContain('/dashboard');
});

Then('I should see {string} message', async function(message: string) {
    const text = await this.page.textContent('body');
    expect(text).toContain(message);
});
```

## 5.3 Testing Pyramid

```
         /\
        /  \       E2E Tests (Few)
       /    \      - Full system tests
      /------\     - Slow, brittle, expensive
     /        \
    /          \   Integration Tests (Some)
   /            \  - Multiple components
  /              \ - Database, APIs, services
 /                \
/------------------\
  Unit Tests (Many)
  - Individual functions/classes
  - Fast, isolated, cheap
```

### 5.3.1 Unit Tests

**Characteristics**:
- Test single unit in isolation
- Fast (<1ms per test)
- No I/O (database, network, file system)
- Deterministic

```typescript
// Unit test: Pure function
describe('calculateTax', () => {
    it('should calculate 10% tax', () => {
        expect(calculateTax(100, 0.1)).toBe(10);
    });

    it('should handle zero amount', () => {
        expect(calculateTax(0, 0.1)).toBe(0);
    });

    it('should handle zero rate', () => {
        expect(calculateTax(100, 0)).toBe(0);
    });
});

// Unit test: Class with dependencies (mocked)
describe('OrderService', () => {
    let orderService: OrderService;
    let mockRepository: jest.Mocked<OrderRepository>;
    let mockEmailService: jest.Mocked<EmailService>;

    beforeEach(() => {
        mockRepository = {
            save: jest.fn(),
            findById: jest.fn()
        } as any;

        mockEmailService = {
            send: jest.fn()
        } as any;

        orderService = new OrderService(mockRepository, mockEmailService);
    });

    it('should create order and send confirmation', async () => {
        const orderData = {customerId: '1', items: []};
        mockRepository.save.mockResolvedValue({id: '123', ...orderData});

        const order = await orderService.createOrder(orderData);

        expect(mockRepository.save).toHaveBeenCalledWith(orderData);
        expect(mockEmailService.send).toHaveBeenCalledWith({
            to: expect.any(String),
            subject: 'Order Confirmation',
            body: expect.stringContaining('123')
        });
        expect(order.id).toBe('123');
    });
});
```

### 5.3.2 Integration Tests

**Characteristics**:
- Test multiple components together
- Slower (10ms-1s per test)
- May involve I/O
- Test real interactions

```typescript
describe('UserService Integration', () => {
    let database: Database;
    let userService: UserService;

    beforeAll(async () => {
        // Setup real test database
        database = await createTestDatabase();
    });

    beforeEach(async () => {
        // Clean database before each test
        await database.clean();

        userService = new UserService(
            new UserRepository(database),
            new RealPasswordHasher(),
            new RealEmailValidator()
        );
    });

    afterAll(async () => {
        await database.close();
    });

    it('should create user with hashed password', async () => {
        const userData = {
            email: 'test@example.com',
            password: 'password123',
            name: 'Test User'
        };

        const user = await userService.createUser(userData);

        // Verify user saved to database
        const savedUser = await database.users.findById(user.id);
        expect(savedUser).toBeDefined();
        expect(savedUser.email).toBe('test@example.com');

        // Verify password is hashed
        expect(savedUser.password).not.toBe('password123');
        expect(savedUser.password).toMatch(/^\$2[aby]\$/); // bcrypt hash pattern
    });

    it('should prevent duplicate emails', async () => {
        await userService.createUser({
            email: 'test@example.com',
            password: 'pass1',
            name: 'User 1'
        });

        await expect(
            userService.createUser({
                email: 'test@example.com',
                password: 'pass2',
                name: 'User 2'
            })
        ).rejects.toThrow('Email already exists');
    });
});
```

### 5.3.3 End-to-End Tests

**Characteristics**:
- Test entire system from user perspective
- Slowest (1s-30s per test)
- Involves all components, external services
- Brittle, expensive to maintain

```typescript
import { chromium, Browser, Page } from 'playwright';

describe('E2E: Checkout Flow', () => {
    let browser: Browser;
    let page: Page;

    beforeAll(async () => {
        browser = await chromium.launch();
    });

    beforeEach(async () => {
        page = await browser.newPage();
    });

    afterEach(async () => {
        await page.close();
    });

    afterAll(async () => {
        await browser.close();
    });

    it('should complete full checkout process', async () => {
        // 1. Browse products
        await page.goto('http://localhost:3000');
        await page.click('text=Products');

        // 2. Add item to cart
        await page.click('[data-testid="product-1"] button:text("Add to Cart")');

        // Verify cart badge updated
        await expect(page.locator('[data-testid="cart-badge"]'))
            .toHaveText('1');

        // 3. Go to cart
        await page.click('[data-testid="cart-icon"]');
        await expect(page).toHaveURL(/.*\/cart/);

        // Verify item in cart
        await expect(page.locator('[data-testid="cart-item"]'))
            .toBeVisible();

        // 4. Proceed to checkout
        await page.click('button:text("Checkout")');
        await expect(page).toHaveURL(/.*\/checkout/);

        // 5. Fill shipping info
        await page.fill('[name="fullName"]', 'John Doe');
        await page.fill('[name="address"]', '123 Main St');
        await page.fill('[name="city"]', 'San Francisco');
        await page.fill('[name="zipCode"]', '94102');

        // 6. Fill payment info
        await page.fill('[name="cardNumber"]', '4242424242424242');
        await page.fill('[name="expiry"]', '12/25');
        await page.fill('[name="cvc"]', '123');

        // 7. Complete order
        await page.click('button:text("Place Order")');

        // 8. Verify confirmation
        await expect(page).toHaveURL(/.*\/confirmation/);
        await expect(page.locator('text=Order Confirmed')).toBeVisible();

        // Verify order number displayed
        const orderNumber = await page.locator('[data-testid="order-number"]')
            .textContent();
        expect(orderNumber).toMatch(/^ORD-\d+$/);
    });
});
```

## 5.4 Mocking Strategies

### 5.4.1 Test Doubles

**Types**:
1. **Dummy**: Passed but never used
2. **Stub**: Returns predetermined responses
3. **Spy**: Records information about calls
4. **Mock**: Pre-programmed with expectations
5. **Fake**: Working implementation (simplified)

```typescript
// Dummy: Just satisfies interface
class DummyEmailService implements EmailService {
    async send(email: Email): Promise<void> {
        // Do nothing
    }
}

// Stub: Returns fixed values
class StubUserRepository implements UserRepository {
    async findById(id: string): Promise<User> {
        return {
            id: '1',
            name: 'Test User',
            email: 'test@example.com'
        };
    }
}

// Spy: Records calls
class SpyEmailService implements EmailService {
    public calls: Email[] = [];

    async send(email: Email): Promise<void> {
        this.calls.push(email);
    }

    wasCalled(): boolean {
        return this.calls.length > 0;
    }

    wasCalledWith(email: Email): boolean {
        return this.calls.some(call =>
            call.to === email.to &&
            call.subject === email.subject
        );
    }
}

// Mock: Verifies expectations
const mockRepository = {
    save: jest.fn()
        .mockResolvedValue({id: '1'})
        .mockName('mockRepository.save')
};

// Later...
expect(mockRepository.save).toHaveBeenCalledTimes(1);
expect(mockRepository.save).toHaveBeenCalledWith({
    name: 'John',
    email: 'john@example.com'
});

// Fake: Simplified working implementation
class FakeDatabase implements Database {
    private store = new Map<string, any>();

    async save(id: string, data: any): Promise<void> {
        this.store.set(id, data);
    }

    async find(id: string): Promise<any> {
        return this.store.get(id);
    }

    async delete(id: string): Promise<void> {
        this.store.delete(id);
    }

    clear(): void {
        this.store.clear();
    }
}
```

### 5.4.2 When to Mock

**Mock**:
- External APIs (HTTP, third-party services)
- Databases (for unit tests)
- File system
- Time-dependent code
- Random number generators

**Don't Mock**:
- Value objects
- Simple data structures
- Pure functions
- Library code you trust

```typescript
// GOOD: Mock external API
it('should fetch user data', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
        json: async () => ({id: '1', name: 'John'})
    });

    global.fetch = mockFetch as any;

    const user = await fetchUser('1');

    expect(mockFetch).toHaveBeenCalledWith('/api/users/1');
    expect(user.name).toBe('John');
});

// BAD: Mocking too much
it('should calculate total', () => {
    const mockAdd = jest.fn((a, b) => a + b); // Why mock addition?!

    const total = [1, 2, 3].reduce(mockAdd, 0);

    expect(total).toBe(6);
    expect(mockAdd).toHaveBeenCalledTimes(3);
});

// GOOD: Test actual logic
it('should calculate total', () => {
    const total = [1, 2, 3].reduce((sum, n) => sum + n, 0);
    expect(total).toBe(6);
});
```

### 5.4.3 Mocking Time

```typescript
// Mock Date.now()
describe('TimeService', () => {
    let originalDateNow: typeof Date.now;

    beforeEach(() => {
        originalDateNow = Date.now;
        // Mock Date.now to return fixed timestamp
        Date.now = jest.fn(() => 1609459200000); // 2021-01-01 00:00:00
    });

    afterEach(() => {
        Date.now = originalDateNow;
    });

    it('should check if timestamp is recent', () => {
        const service = new TimeService();

        // Timestamp from 5 minutes ago
        const timestamp = Date.now() - 5 * 60 * 1000;

        expect(service.isRecent(timestamp, 10 * 60 * 1000)).toBe(true);
    });
});

// Mock setTimeout/setInterval
jest.useFakeTimers();

it('should call callback after delay', () => {
    const callback = jest.fn();

    setTimeout(callback, 1000);

    expect(callback).not.toHaveBeenCalled();

    // Fast-forward time
    jest.advanceTimersByTime(1000);

    expect(callback).toHaveBeenCalledTimes(1);
});
```


---

# PART 6: SYSTEM ARCHITECTURE

## 6.1 Layered Architecture

### 6.1.1 Classic Layers

```
┌─────────────────────────────────┐
│     Presentation Layer          │  UI, Controllers, Views
├─────────────────────────────────┤
│     Business Logic Layer        │  Domain models, Services
├─────────────────────────────────┤
│     Data Access Layer           │  Repositories, DAOs
├─────────────────────────────────┤
│     Database                    │  Persistence
└─────────────────────────────────┘
```

**Rules**:
- Each layer only depends on layer below
- No skipping layers
- Data flows down, responses flow up

```typescript
// Presentation Layer
class UserController {
    constructor(private userService: UserService) {}

    async createUser(req: Request, res: Response) {
        try {
            const user = await this.userService.create(req.body);
            res.status(201).json(user);
        } catch (error) {
            res.status(400).json({error: error.message});
        }
    }
}

// Business Logic Layer
class UserService {
    constructor(private userRepository: UserRepository) {}

    async create(userData: CreateUserDTO): Promise<User> {
        // Business logic
        this.validateUserData(userData);

        const hashedPassword = await this.hashPassword(userData.password);

        const user = new User({
            ...userData,
            password: hashedPassword
        });

        return this.userRepository.save(user);
    }

    private validateUserData(data: CreateUserDTO): void {
        if (!data.email.includes('@')) {
            throw new Error('Invalid email');
        }
        // More validation...
    }
}

// Data Access Layer
class UserRepository {
    constructor(private db: Database) {}

    async save(user: User): Promise<User> {
        const result = await this.db.query(
            'INSERT INTO users (email, password, name) VALUES ($1, $2, $3) RETURNING *',
            [user.email, user.password, user.name]
        );

        return this.mapToUser(result.rows[0]);
    }

    async findById(id: string): Promise<User | null> {
        const result = await this.db.query(
            'SELECT * FROM users WHERE id = $1',
            [id]
        );

        return result.rows[0] ? this.mapToUser(result.rows[0]) : null;
    }

    private mapToUser(row: any): User {
        return new User({
            id: row.id,
            email: row.email,
            password: row.password,
            name: row.name,
            createdAt: row.created_at
        });
    }
}
```

## 6.2 Clean Architecture (Hexagonal Architecture)

### 6.2.1 The Dependency Rule

**Core Principle**: Dependencies point inward. Inner layers know nothing about outer layers.

```
┌───────────────────────────────────────────┐
│  Frameworks & Drivers (UI, DB, External) │  Outer
├───────────────────────────────────────────┤
│  Interface Adapters (Controllers, Gateway)│
├───────────────────────────────────────────┤
│  Use Cases (Application Business Rules)   │
├───────────────────────────────────────────┤
│  Entities (Enterprise Business Rules)     │  Inner
└───────────────────────────────────────────┘
```

### 6.2.2 Implementation

```typescript
// INNER: Entities (domain objects)
class User {
    constructor(
        public readonly id: string,
        public email: string,
        private password: string,
        public name: string
    ) {
        this.validateEmail(email);
    }

    private validateEmail(email: string): void {
        if (!email.includes('@')) {
            throw new Error('Invalid email');
        }
    }

    changeEmail(newEmail: string): void {
        this.validateEmail(newEmail);
        this.email = newEmail;
    }

    verifyPassword(password: string, hasher: PasswordHasher): boolean {
        return hasher.verify(password, this.password);
    }
}

// INNER: Use Cases (application-specific business rules)
interface UserRepository {
    save(user: User): Promise<User>;
    findById(id: string): Promise<User | null>;
    findByEmail(email: string): Promise<User | null>;
}

interface PasswordHasher {
    hash(password: string): Promise<string>;
    verify(password: string, hash: string): boolean;
}

class CreateUserUseCase {
    constructor(
        private userRepository: UserRepository,
        private passwordHasher: PasswordHasher
    ) {}

    async execute(request: CreateUserRequest): Promise<CreateUserResponse> {
        // Check if user already exists
        const existingUser = await this.userRepository.findByEmail(request.email);
        if (existingUser) {
            throw new Error('User already exists');
        }

        // Hash password
        const hashedPassword = await this.passwordHasher.hash(request.password);

        // Create user entity
        const user = new User(
            this.generateId(),
            request.email,
            hashedPassword,
            request.name
        );

        // Save user
        await this.userRepository.save(user);

        return {
            id: user.id,
            email: user.email,
            name: user.name
        };
    }

    private generateId(): string {
        return crypto.randomUUID();
    }
}

// OUTER: Interface Adapters
class UserController {
    constructor(private createUserUseCase: CreateUserUseCase) {}

    async create(req: Request, res: Response) {
        try {
            const response = await this.createUserUseCase.execute({
                email: req.body.email,
                password: req.body.password,
                name: req.body.name
            });

            res.status(201).json(response);
        } catch (error) {
            res.status(400).json({error: error.message});
        }
    }
}

// OUTER: Frameworks & Drivers
class PostgresUserRepository implements UserRepository {
    constructor(private db: Database) {}

    async save(user: User): Promise<User> {
        await this.db.query(
            'INSERT INTO users (id, email, password, name) VALUES ($1, $2, $3, $4)',
            [user.id, user.email, (user as any).password, user.name]
        );

        return user;
    }

    async findById(id: string): Promise<User | null> {
        const result = await this.db.query(
            'SELECT * FROM users WHERE id = $1',
            [id]
        );

        if (result.rows.length === 0) {
            return null;
        }

        const row = result.rows[0];
        return new User(row.id, row.email, row.password, row.name);
    }

    async findByEmail(email: string): Promise<User | null> {
        const result = await this.db.query(
            'SELECT * FROM users WHERE email = $1',
            [email]
        );

        if (result.rows.length === 0) {
            return null;
        }

        const row = result.rows[0];
        return new User(row.id, row.email, row.password, row.name);
    }
}

class BcryptPasswordHasher implements PasswordHasher {
    async hash(password: string): Promise<string> {
        return bcrypt.hash(password, 10);
    }

    verify(password: string, hash: string): boolean {
        return bcrypt.compareSync(password, hash);
    }
}

// Composition Root (wiring everything together)
function createApp() {
    const db = new Database(process.env.DATABASE_URL);
    const userRepository = new PostgresUserRepository(db);
    const passwordHasher = new BcryptPasswordHasher();
    const createUserUseCase = new CreateUserUseCase(userRepository, passwordHasher);
    const userController = new UserController(createUserUseCase);

    return {userController};
}
```

**Benefits**:
- Business logic independent of UI, database, frameworks
- Easy to test (mock interfaces)
- Easy to swap implementations
- Changes in outer layers don't affect inner layers

## 6.3 Event-Driven Architecture

### 6.3.1 Event Bus Pattern

```typescript
type EventHandler<T = any> = (event: T) => void | Promise<void>;

class EventBus {
    private handlers = new Map<string, EventHandler[]>();

    subscribe(eventType: string, handler: EventHandler): void {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, []);
        }

        this.handlers.get(eventType)!.push(handler);
    }

    async publish(eventType: string, event: any): Promise<void> {
        const handlers = this.handlers.get(eventType) || [];

        // Execute handlers in parallel
        await Promise.all(
            handlers.map(handler =>
                Promise.resolve(handler(event))
                    .catch(error => {
                        console.error(`Error in handler for ${eventType}:`, error);
                    })
            )
        );
    }

    unsubscribe(eventType: string, handler: EventHandler): void {
        const handlers = this.handlers.get(eventType);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
            }
        }
    }
}

// Domain Events
interface OrderPlacedEvent {
    orderId: string;
    customerId: string;
    items: OrderItem[];
    total: number;
    placedAt: Date;
}

interface PaymentProcessedEvent {
    orderId: string;
    amount: number;
    paymentMethod: string;
    processedAt: Date;
}

// Event Handlers
class InventoryEventHandler {
    constructor(private inventoryService: InventoryService) {}

    async handleOrderPlaced(event: OrderPlacedEvent): Promise<void> {
        console.log(`Reserving inventory for order ${event.orderId}`);
        await this.inventoryService.reserveItems(event.items);
    }
}

class NotificationEventHandler {
    constructor(private emailService: EmailService) {}

    async handleOrderPlaced(event: OrderPlacedEvent): Promise<void> {
        console.log(`Sending confirmation email for order ${event.orderId}`);
        await this.emailService.sendOrderConfirmation(
            event.customerId,
            event.orderId
        );
    }

    async handlePaymentProcessed(event: PaymentProcessedEvent): Promise<void> {
        console.log(`Sending payment receipt for order ${event.orderId}`);
        await this.emailService.sendPaymentReceipt(
            event.orderId,
            event.amount
        );
    }
}

class AnalyticsEventHandler {
    async handleOrderPlaced(event: OrderPlacedEvent): Promise<void> {
        console.log(`Tracking order placed event`);
        await analytics.track('order_placed', {
            orderId: event.orderId,
            total: event.total,
            itemCount: event.items.length
        });
    }
}

// Setup
const eventBus = new EventBus();

const inventoryHandler = new InventoryEventHandler(inventoryService);
const notificationHandler = new NotificationEventHandler(emailService);
const analyticsHandler = new AnalyticsEventHandler();

eventBus.subscribe('OrderPlaced', (e) => inventoryHandler.handleOrderPlaced(e));
eventBus.subscribe('OrderPlaced', (e) => notificationHandler.handleOrderPlaced(e));
eventBus.subscribe('OrderPlaced', (e) => analyticsHandler.handleOrderPlaced(e));
eventBus.subscribe('PaymentProcessed', (e) => notificationHandler.handlePaymentProcessed(e));

// Usage
class OrderService {
    constructor(private eventBus: EventBus) {}

    async placeOrder(orderData: CreateOrderDTO): Promise<Order> {
        // Create order
        const order = await this.createOrder(orderData);

        // Publish event
        await this.eventBus.publish('OrderPlaced', {
            orderId: order.id,
            customerId: order.customerId,
            items: order.items,
            total: order.total,
            placedAt: new Date()
        });

        return order;
    }
}
```

### 6.3.2 CQRS (Command Query Responsibility Segregation)

**Principle**: Separate read and write operations.

```typescript
// Commands (writes)
interface Command {
    execute(): Promise<void>;
}

class CreateUserCommand implements Command {
    constructor(
        private userRepository: UserRepository,
        private userData: CreateUserDTO
    ) {}

    async execute(): Promise<void> {
        const user = new User(this.userData);
        await this.userRepository.save(user);

        // Publish event
        await eventBus.publish('UserCreated', {
            userId: user.id,
            email: user.email
        });
    }
}

class UpdateUserCommand implements Command {
    constructor(
        private userRepository: UserRepository,
        private userId: string,
        private updates: UpdateUserDTO
    ) {}

    async execute(): Promise<void> {
        const user = await this.userRepository.findById(this.userId);
        if (!user) {
            throw new Error('User not found');
        }

        user.update(this.updates);
        await this.userRepository.save(user);

        await eventBus.publish('UserUpdated', {
            userId: user.id,
            changes: this.updates
        });
    }
}

// Queries (reads)
interface Query<T> {
    execute(): Promise<T>;
}

class GetUserQuery implements Query<UserDTO> {
    constructor(
        private userReadModel: UserReadModel,
        private userId: string
    ) {}

    async execute(): Promise<UserDTO> {
        return this.userReadModel.findById(this.userId);
    }
}

class SearchUsersQuery implements Query<UserDTO[]> {
    constructor(
        private userReadModel: UserReadModel,
        private criteria: SearchCriteria
    ) {}

    async execute(): Promise<UserDTO[]> {
        return this.userReadModel.search(this.criteria);
    }
}

// Separate read and write models
class UserRepository {
    // Optimized for writes
    async save(user: User): Promise<void> {
        await db.users.insert(user.toJSON());
    }
}

class UserReadModel {
    // Optimized for reads
    async findById(id: string): Promise<UserDTO> {
        // Could read from cache, denormalized table, etc.
        return cache.get(`user:${id}`) || await db.userViews.findById(id);
    }

    async search(criteria: SearchCriteria): Promise<UserDTO[]> {
        // Could use Elasticsearch for complex queries
        return elasticsearch.search({
            index: 'users',
            body: {
                query: this.buildQuery(criteria)
            }
        });
    }
}

// Command/Query Bus
class CommandBus {
    async execute(command: Command): Promise<void> {
        try {
            await command.execute();
        } catch (error) {
            console.error('Command failed:', error);
            throw error;
        }
    }
}

class QueryBus {
    async execute<T>(query: Query<T>): Promise<T> {
        return query.execute();
    }
}

// Usage
const commandBus = new CommandBus();
const queryBus = new QueryBus();

// Write
await commandBus.execute(
    new CreateUserCommand(userRepository, {
        email: 'user@example.com',
        name: 'John Doe'
    })
);

// Read
const user = await queryBus.execute(
    new GetUserQuery(userReadModel, '123')
);
```

### 6.3.3 Event Sourcing

**Principle**: Store sequence of events rather than current state.

```typescript
// Events
interface Event {
    eventId: string;
    aggregateId: string;
    eventType: string;
    data: any;
    timestamp: Date;
    version: number;
}

class UserCreatedEvent implements Event {
    eventId: string;
    aggregateId: string;
    eventType = 'UserCreated';
    timestamp: Date;
    version: number;

    constructor(
        public userId: string,
        public email: string,
        public name: string
    ) {
        this.eventId = crypto.randomUUID();
        this.aggregateId = userId;
        this.timestamp = new Date();
        this.version = 1;
    }

    get data() {
        return {
            email: this.email,
            name: this.name
        };
    }
}

class UserEmailChangedEvent implements Event {
    eventId: string;
    aggregateId: string;
    eventType = 'UserEmailChanged';
    timestamp: Date;
    version: number;

    constructor(
        public userId: string,
        public oldEmail: string,
        public newEmail: string,
        version: number
    ) {
        this.eventId = crypto.randomUUID();
        this.aggregateId = userId;
        this.timestamp = new Date();
        this.version = version;
    }

    get data() {
        return {
            oldEmail: this.oldEmail,
            newEmail: this.newEmail
        };
    }
}

// Event Store
class EventStore {
    private events: Event[] = [];

    async append(event: Event): Promise<void> {
        // In real implementation, this would write to database
        this.events.push(event);
    }

    async getEvents(aggregateId: string): Promise<Event[]> {
        return this.events
            .filter(e => e.aggregateId === aggregateId)
            .sort((a, b) => a.version - b.version);
    }

    async getEventsSince(aggregateId: string, version: number): Promise<Event[]> {
        return this.events
            .filter(e => e.aggregateId === aggregateId && e.version > version)
            .sort((a, b) => a.version - b.version);
    }
}

// Aggregate (rebuilds state from events)
class User {
    private version: number = 0;

    constructor(
        public id: string,
        public email: string,
        public name: string
    ) {}

    static fromEvents(events: Event[]): User {
        if (events.length === 0) {
            throw new Error('No events to rebuild user from');
        }

        const firstEvent = events[0];
        if (firstEvent.eventType !== 'UserCreated') {
            throw new Error('First event must be UserCreated');
        }

        const user = new User(
            firstEvent.aggregateId,
            firstEvent.data.email,
            firstEvent.data.name
        );

        // Apply subsequent events
        for (let i = 1; i < events.length; i++) {
            user.applyEvent(events[i]);
        }

        user.version = events[events.length - 1].version;
        return user;
    }

    changeEmail(newEmail: string): UserEmailChangedEvent {
        const event = new UserEmailChangedEvent(
            this.id,
            this.email,
            newEmail,
            this.version + 1
        );

        this.applyEvent(event);
        return event;
    }

    private applyEvent(event: Event): void {
        switch (event.eventType) {
            case 'UserEmailChanged':
                this.email = event.data.newEmail;
                break;
            // Handle other event types...
        }

        this.version = event.version;
    }
}

// Repository
class UserEventSourcedRepository {
    constructor(private eventStore: EventStore) {}

    async save(user: User, events: Event[]): Promise<void> {
        for (const event of events) {
            await this.eventStore.append(event);
        }
    }

    async findById(id: string): Promise<User | null> {
        const events = await this.eventStore.getEvents(id);

        if (events.length === 0) {
            return null;
        }

        return User.fromEvents(events);
    }
}

// Usage
const eventStore = new EventStore();
const repository = new UserEventSourcedRepository(eventStore);

// Create user
const createEvent = new UserCreatedEvent(
    '123',
    'user@example.com',
    'John Doe'
);
await eventStore.append(createEvent);

// Later... rebuild from events
const user = await repository.findById('123');

// Change email
const changeEvent = user!.changeEmail('newemail@example.com');
await eventStore.append(changeEvent);

// Even later... rebuild again
const updatedUser = await repository.findById('123');
console.log(updatedUser!.email); // 'newemail@example.com'

// Can rebuild state at any point in time!
const eventsUntilV1 = await eventStore.getEvents('123');
const userAtV1 = User.fromEvents(eventsUntilV1.slice(0, 1));
console.log(userAtV1.email); // 'user@example.com' (original email)
```

**Benefits of Event Sourcing**:
- Complete audit log
- Can rebuild state at any point in time
- Temporal queries ("What was X on date Y?")
- Event replay for debugging
- Multiple read models from same events

## 6.4 API Design

### 6.4.1 REST API Best Practices

**Resource Naming**:
```
# Good
GET    /users              # Get all users
GET    /users/123          # Get specific user
POST   /users              # Create user
PUT    /users/123          # Update user (full replace)
PATCH  /users/123          # Update user (partial)
DELETE /users/123          # Delete user

GET    /users/123/orders   # Get user's orders
POST   /users/123/orders   # Create order for user

# Bad
GET    /getUsers           # Verb in URL
POST   /createUser         # Verb in URL
GET    /user/123           # Inconsistent singular/plural
```

**HTTP Status Codes**:
```typescript
class UserController {
    async create(req: Request, res: Response) {
        try {
            const user = await this.userService.create(req.body);
            res.status(201)  // Created
                .location(`/users/${user.id}`)
                .json(user);
        } catch (error) {
            if (error instanceof ValidationError) {
                res.status(400).json({  // Bad Request
                    error: 'Validation failed',
                    details: error.errors
                });
            } else if (error instanceof DuplicateEmailError) {
                res.status(409).json({  // Conflict
                    error: 'Email already exists'
                });
            } else {
                res.status(500).json({  // Internal Server Error
                    error: 'Internal server error'
                });
            }
        }
    }

    async get(req: Request, res: Response) {
        const user = await this.userService.findById(req.params.id);

        if (!user) {
            return res.status(404).json({  // Not Found
                error: 'User not found'
            });
        }

        res.status(200).json(user);  // OK
    }

    async update(req: Request, res: Response) {
        if (!req.headers.authorization) {
            return res.status(401).json({  // Unauthorized
                error: 'Authentication required'
            });
        }

        const userId = req.params.id;
        const currentUser = await this.getCurrentUser(req);

        if (currentUser.id !== userId && !currentUser.isAdmin) {
            return res.status(403).json({  // Forbidden
                error: 'You do not have permission to update this user'
            });
        }

        const user = await this.userService.update(userId, req.body);
        res.status(200).json(user);
    }

    async delete(req: Request, res: Response) {
        await this.userService.delete(req.params.id);
        res.status(204).send();  // No Content
    }
}
```

**Pagination**:
```typescript
interface PaginatedResponse<T> {
    data: T[];
    pagination: {
        page: number;
        pageSize: number;
        totalPages: number;
        totalItems: number;
    };
    links: {
        first: string;
        prev: string | null;
        next: string | null;
        last: string;
    };
}

class UserController {
    async list(req: Request, res: Response) {
        const page = parseInt(req.query.page as string) || 1;
        const pageSize = parseInt(req.query.pageSize as string) || 20;

        const result = await this.userService.list({
            page,
            pageSize
        });

        const response: PaginatedResponse<User> = {
            data: result.users,
            pagination: {
                page,
                pageSize,
                totalPages: Math.ceil(result.total / pageSize),
                totalItems: result.total
            },
            links: {
                first: `/users?page=1&pageSize=${pageSize}`,
                prev: page > 1
                    ? `/users?page=${page - 1}&pageSize=${pageSize}`
                    : null,
                next: page < Math.ceil(result.total / pageSize)
                    ? `/users?page=${page + 1}&pageSize=${pageSize}`
                    : null,
                last: `/users?page=${Math.ceil(result.total / pageSize)}&pageSize=${pageSize}`
            }
        };

        res.json(response);
    }
}
```

**Filtering & Sorting**:
```
GET /users?role=admin&status=active&sort=-createdAt&limit=50

role=admin       -> Filter by role
status=active    -> Filter by status
sort=-createdAt  -> Sort by createdAt descending (- prefix)
limit=50         -> Limit results
```

```typescript
class UserController {
    async list(req: Request, res: Response) {
        const filters = {
            role: req.query.role,
            status: req.query.status,
            search: req.query.search
        };

        const sort = this.parseSort(req.query.sort as string);
        const limit = parseInt(req.query.limit as string) || 20;
        const offset = parseInt(req.query.offset as string) || 0;

        const result = await this.userService.list({
            filters,
            sort,
            limit,
            offset
        });

        res.json(result);
    }

    private parseSort(sortParam: string): {field: string, order: 'ASC' | 'DESC'}[] {
        if (!sortParam) return [];

        return sortParam.split(',').map(field => {
            if (field.startsWith('-')) {
                return {field: field.substring(1), order: 'DESC'};
            }
            return {field, order: 'ASC'};
        });
    }
}
```

### 6.4.2 GraphQL

**Schema**:
```graphql
type User {
  id: ID!
  email: String!
  name: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

type Query {
  user(id: ID!): User
  users(
    page: Int = 1
    pageSize: Int = 20
    filter: UserFilter
  ): UserConnection!

  post(id: ID!): Post
  posts(
    page: Int = 1
    pageSize: Int = 20
  ): PostConnection!
}

input UserFilter {
  role: String
  status: String
  search: String
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!

  createPost(input: CreatePostInput!): Post!
  addComment(postId: ID!, content: String!): Comment!
}

input CreateUserInput {
  email: String!
  password: String!
  name: String!
}

input UpdateUserInput {
  email: String
  name: String
}

input CreatePostInput {
  title: String!
  content: String!
}
```

**Resolvers**:
```typescript
const resolvers = {
    Query: {
        user: async (_: any, {id}: {id: string}, context: Context) => {
            return context.dataSources.userAPI.findById(id);
        },

        users: async (
            _: any,
            {page, pageSize, filter}: {page: number, pageSize: number, filter: any},
            context: Context
        ) => {
            const result = await context.dataSources.userAPI.list({
                page,
                pageSize,
                filter
            });

            return {
                edges: result.users.map(user => ({
                    node: user,
                    cursor: Buffer.from(user.id).toString('base64')
                })),
                pageInfo: {
                    hasNextPage: page * pageSize < result.total,
                    hasPreviousPage: page > 1,
                    startCursor: result.users[0]?.id,
                    endCursor: result.users[result.users.length - 1]?.id
                },
                totalCount: result.total
            };
        }
    },

    User: {
        // Field resolver for posts
        posts: async (user: User, _: any, context: Context) => {
            return context.dataSources.postAPI.findByAuthorId(user.id);
        }
    },

    Post: {
        // Field resolver for author
        author: async (post: Post, _: any, context: Context) => {
            // DataLoader automatically batches these calls
            return context.loaders.userLoader.load(post.authorId);
        },

        // Field resolver for comments
        comments: async (post: Post, _: any, context: Context) => {
            return context.dataSources.commentAPI.findByPostId(post.id);
        }
    },

    Mutation: {
        createUser: async (
            _: any,
            {input}: {input: CreateUserInput},
            context: Context
        ) => {
            return context.dataSources.userAPI.create(input);
        },

        updateUser: async (
            _: any,
            {id, input}: {id: string, input: UpdateUserInput},
            context: Context
        ) => {
            return context.dataSources.userAPI.update(id, input);
        }
    }
};
```

**DataLoader** (solves N+1 problem):
```typescript
import DataLoader from 'dataloader';

class UserAPI {
    private db: Database;
    private userLoader: DataLoader<string, User>;

    constructor(db: Database) {
        this.db = db;
        this.userLoader = new DataLoader(async (ids: readonly string[]) => {
            console.log('Batch loading users:', ids);

            const users = await this.db.users.findByIds([...ids]);
            const userMap = new Map(users.map(u => [u.id, u]));

            // Return users in same order as ids
            return ids.map(id => userMap.get(id) || null);
        });
    }

    async findById(id: string): Promise<User | null> {
        return this.userLoader.load(id);
    }
}

// Query that would cause N+1 in REST:
query {
  posts {
    id
    title
    author {      # Separate request for each post's author
      id
      name
    }
  }
}

// With DataLoader:
// 1 query for posts
// 1 batched query for all authors
// Total: 2 queries instead of 1 + N
```

### 6.4.3 gRPC

**Protocol Buffer Definition**:
```protobuf
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser (CreateUserRequest) returns (User);
  rpc UpdateUser (UpdateUserRequest) returns (User);
  rpc DeleteUser (DeleteUserRequest) returns (DeleteUserResponse);

  // Streaming
  rpc StreamUsers (StreamUsersRequest) returns (stream User);
  rpc UploadUsers (stream User) returns (UploadUsersResponse);
  rpc ChatWithSupport (stream ChatMessage) returns (stream ChatMessage);
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  string role = 4;
  int64 created_at = 5;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
  string role = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total = 2;
}

message CreateUserRequest {
  string email = 1;
  string password = 2;
  string name = 3;
}

message UpdateUserRequest {
  string id = 1;
  string email = 2;
  string name = 3;
}

message DeleteUserRequest {
  string id = 1;
}

message DeleteUserResponse {
  bool success = 1;
}

message StreamUsersRequest {
  string role = 1;
}

message UploadUsersResponse {
  int32 count = 1;
}

message ChatMessage {
  string user_id = 1;
  string content = 2;
  int64 timestamp = 3;
}
```

**Server Implementation**:
```typescript
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const packageDefinition = protoLoader.loadSync('user.proto');
const proto = grpc.loadPackageDefinition(packageDefinition) as any;

class UserServiceImpl {
    async getUser(
        call: grpc.ServerUnaryCall<any, any>,
        callback: grpc.sendUnaryData<any>
    ) {
        try {
            const user = await userRepository.findById(call.request.id);

            if (!user) {
                callback({
                    code: grpc.status.NOT_FOUND,
                    message: 'User not found'
                });
                return;
            }

            callback(null, user);
        } catch (error) {
            callback({
                code: grpc.status.INTERNAL,
                message: error.message
            });
        }
    }

    async listUsers(
        call: grpc.ServerUnaryCall<any, any>,
        callback: grpc.sendUnaryData<any>
    ) {
        const {page, page_size, role} = call.request;

        const result = await userRepository.list({
            page,
            pageSize: page_size,
            filter: {role}
        });

        callback(null, {
            users: result.users,
            total: result.total
        });
    }

    // Server streaming
    streamUsers(call: grpc.ServerWritableStream<any, any>) {
        const {role} = call.request;

        // Stream users as they're found
        const stream = userRepository.streamByRole(role);

        stream.on('data', (user: User) => {
            call.write(user);
        });

        stream.on('end', () => {
            call.end();
        });

        stream.on('error', (error: Error) => {
            call.destroy(error);
        });
    }

    // Client streaming
    uploadUsers(
        call: grpc.ServerReadableStream<any, any>,
        callback: grpc.sendUnaryData<any>
    ) {
        let count = 0;

        call.on('data', async (user: User) => {
            await userRepository.save(user);
            count++;
        });

        call.on('end', () => {
            callback(null, {count});
        });

        call.on('error', (error: Error) => {
            callback(error);
        });
    }

    // Bidirectional streaming
    chatWithSupport(call: grpc.ServerDuplexStream<any, any>) {
        call.on('data', (message: ChatMessage) => {
            console.log('Received:', message.content);

            // Process message and send response
            const response = processMessage(message);
            call.write(response);
        });

        call.on('end', () => {
            call.end();
        });
    }
}

const server = new grpc.Server();
server.addService(proto.user.UserService.service, new UserServiceImpl());
server.bindAsync(
    '0.0.0.0:50051',
    grpc.ServerCredentials.createInsecure(),
    () => {
        console.log('gRPC server running on port 50051');
        server.start();
    }
);
```

**Client Usage**:
```typescript
const client = new proto.user.UserService(
    'localhost:50051',
    grpc.credentials.createInsecure()
);

// Unary call
client.getUser({id: '123'}, (error: Error, user: User) => {
    if (error) {
        console.error('Error:', error);
        return;
    }

    console.log('User:', user);
});

// Server streaming
const stream = client.streamUsers({role: 'admin'});

stream.on('data', (user: User) => {
    console.log('Received user:', user);
});

stream.on('end', () => {
    console.log('Stream ended');
});

// Client streaming
const uploadStream = client.uploadUsers((error: Error, response: any) => {
    if (error) {
        console.error('Error:', error);
        return;
    }

    console.log('Uploaded count:', response.count);
});

users.forEach(user => {
    uploadStream.write(user);
});

uploadStream.end();
```

**gRPC vs REST**:
- gRPC: Binary protocol (Protocol Buffers), faster, smaller payload
- gRPC: Strong typing from .proto files
- gRPC: Built-in streaming
- gRPC: Better for service-to-service communication
- REST: Human-readable (JSON), easier debugging
- REST: Better browser support
- REST: More tooling and ecosystem


---

# PART 7: PERFORMANCE & SCALABILITY

## 7.1 Load Balancing

### 7.1.1 Load Balancing Algorithms

**Round Robin**: Distribute requests evenly across servers.
```typescript
class RoundRobinLoadBalancer {
    private servers: Server[];
    private currentIndex = 0;

    constructor(servers: Server[]) {
        this.servers = servers;
    }

    getNextServer(): Server {
        const server = this.servers[this.currentIndex];
        this.currentIndex = (this.currentIndex + 1) % this.servers.length;
        return server;
    }
}
```

**Weighted Round Robin**: Distribute based on server capacity.
```typescript
class WeightedRoundRobinLoadBalancer {
    private servers: {server: Server, weight: number}[];
    private currentIndex = 0;
    private currentWeight = 0;

    constructor(servers: {server: Server, weight: number}[]) {
        this.servers = servers;
    }

    getNextServer(): Server {
        while (true) {
            this.currentIndex = (this.currentIndex + 1) % this.servers.length;

            if (this.currentIndex === 0) {
                this.currentWeight -= this.gcd();
                if (this.currentWeight <= 0) {
                    this.currentWeight = this.maxWeight();
                }
            }

            if (this.servers[this.currentIndex].weight >= this.currentWeight) {
                return this.servers[this.currentIndex].server;
            }
        }
    }

    private maxWeight(): number {
        return Math.max(...this.servers.map(s => s.weight));
    }

    private gcd(): number {
        const weights = this.servers.map(s => s.weight);
        return weights.reduce((a, b) => this.gcdTwo(a, b));
    }

    private gcdTwo(a: number, b: number): number {
        return b === 0 ? a : this.gcdTwo(b, a % b);
    }
}
```

**Least Connections**: Route to server with fewest active connections.
```typescript
class LeastConnectionsLoadBalancer {
    private servers: Map<Server, number> = new Map();

    constructor(servers: Server[]) {
        servers.forEach(server => this.servers.set(server, 0));
    }

    getNextServer(): Server {
        let minConnections = Infinity;
        let selectedServer: Server | null = null;

        for (const [server, connections] of this.servers) {
            if (connections < minConnections) {
                minConnections = connections;
                selectedServer = server;
            }
        }

        if (selectedServer) {
            this.servers.set(
                selectedServer,
                this.servers.get(selectedServer)! + 1
            );
        }

        return selectedServer!;
    }

    releaseConnection(server: Server): void {
        const connections = this.servers.get(server);
        if (connections !== undefined && connections > 0) {
            this.servers.set(server, connections - 1);
        }
    }
}
```

**IP Hash**: Route based on client IP (ensures same client goes to same server).
```typescript
class IPHashLoadBalancer {
    private servers: Server[];

    constructor(servers: Server[]) {
        this.servers = servers;
    }

    getServer(clientIP: string): Server {
        const hash = this.hashIP(clientIP);
        const index = hash % this.servers.length;
        return this.servers[index];
    }

    private hashIP(ip: string): number {
        let hash = 0;
        for (let i = 0; i < ip.length; i++) {
            hash = ((hash << 5) - hash) + ip.charCodeAt(i);
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash);
    }
}
```

**Consistent Hashing**: Minimize redistribution when servers added/removed.
```typescript
class ConsistentHashLoadBalancer {
    private ring: Map<number, Server> = new Map();
    private sortedKeys: number[] = [];
    private virtualNodes = 150; // Replicas per server

    constructor(servers: Server[]) {
        servers.forEach(server => this.addServer(server));
    }

    addServer(server: Server): void {
        for (let i = 0; i < this.virtualNodes; i++) {
            const hash = this.hash(`${server.id}:${i}`);
            this.ring.set(hash, server);
            this.sortedKeys.push(hash);
        }

        this.sortedKeys.sort((a, b) => a - b);
    }

    removeServer(server: Server): void {
        for (let i = 0; i < this.virtualNodes; i++) {
            const hash = this.hash(`${server.id}:${i}`);
            this.ring.delete(hash);
            this.sortedKeys = this.sortedKeys.filter(k => k !== hash);
        }
    }

    getServer(key: string): Server {
        if (this.ring.size === 0) {
            throw new Error('No servers available');
        }

        const hash = this.hash(key);

        // Find first server with hash >= key hash
        let index = this.sortedKeys.findIndex(k => k >= hash);

        // Wrap around if necessary
        if (index === -1) {
            index = 0;
        }

        const serverHash = this.sortedKeys[index];
        return this.ring.get(serverHash)!;
    }

    private hash(key: string): number {
        let hash = 0;
        for (let i = 0; i < key.length; i++) {
            hash = ((hash << 5) - hash) + key.charCodeAt(i);
            hash = hash & hash;
        }
        return Math.abs(hash);
    }
}

// Example usage
const lb = new ConsistentHashLoadBalancer([
    { id: 'server1', url: 'http://server1:3000' },
    { id: 'server2', url: 'http://server2:3000' },
    { id: 'server3', url: 'http://server3:3000' }
]);

// Same user always goes to same server
const server1 = lb.getServer('user:123');
const server2 = lb.getServer('user:123');
// server1 === server2

// Adding server doesn't reassign most keys
lb.addServer({ id: 'server4', url: 'http://server4:3000' });
// Only ~25% of keys get reassigned (not 50% like modulo hashing)
```

## 7.2 Caching

### 7.2.1 Cache Hierarchy

```
Client
  ↓
Browser Cache (seconds to minutes)
  ↓
CDN (minutes to hours)
  ↓
API Gateway Cache (seconds to minutes)
  ↓
Application Cache (Redis, Memcached)
  ↓
Database Query Cache
  ↓
Database
```

### 7.2.2 Cache Strategies

**Cache-Aside (Lazy Loading)**:
```typescript
class UserService {
    constructor(
        private cache: Cache,
        private repository: UserRepository
    ) {}

    async getUser(id: string): Promise<User> {
        // Try cache first
        const cacheKey = `user:${id}`;
        const cached = await this.cache.get(cacheKey);

        if (cached) {
            console.log('Cache hit');
            return JSON.parse(cached);
        }

        // Cache miss, fetch from database
        console.log('Cache miss');
        const user = await this.repository.findById(id);

        if (user) {
            // Store in cache for future requests
            await this.cache.set(
                cacheKey,
                JSON.stringify(user),
                { ttl: 300 } // 5 minutes
            );
        }

        return user;
    }

    async updateUser(id: string, data: UpdateUserDTO): Promise<User> {
        const user = await this.repository.update(id, data);

        // Invalidate cache
        await this.cache.delete(`user:${id}`);

        return user;
    }
}
```

**Write-Through**:
```typescript
class UserService {
    async updateUser(id: string, data: UpdateUserDTO): Promise<User> {
        // Update database
        const user = await this.repository.update(id, data);

        // Update cache
        await this.cache.set(
            `user:${id}`,
            JSON.stringify(user),
            { ttl: 300 }
        );

        return user;
    }
}
```

**Write-Behind (Write-Back)**:
```typescript
class UserService {
    private writeQueue: Map<string, User> = new Map();
    private flushInterval = 5000; // 5 seconds

    constructor(
        private cache: Cache,
        private repository: UserRepository
    ) {
        // Flush periodically
        setInterval(() => this.flush(), this.flushInterval);
    }

    async updateUser(id: string, data: UpdateUserDTO): Promise<User> {
        const user = await this.repository.findById(id);
        Object.assign(user, data);

        // Update cache immediately
        await this.cache.set(
            `user:${id}`,
            JSON.stringify(user),
            { ttl: 300 }
        );

        // Queue database write
        this.writeQueue.set(id, user);

        return user;
    }

    private async flush(): Promise<void> {
        const updates = Array.from(this.writeQueue.entries());
        this.writeQueue.clear();

        await Promise.all(
            updates.map(([id, user]) => this.repository.update(id, user))
        );
    }
}
```

**Read-Through**:
```typescript
class CacheManager<T> {
    constructor(
        private cache: Cache,
        private loader: (key: string) => Promise<T>
    ) {}

    async get(key: string): Promise<T> {
        let value = await this.cache.get(key);

        if (!value) {
            // Cache doesn't have it, load it
            value = await this.loader(key);
            await this.cache.set(key, value);
        }

        return value;
    }
}

// Usage
const userCache = new CacheManager(
    redisCache,
    (id) => userRepository.findById(id)
);

const user = await userCache.get('123');
```

### 7.2.3 Cache Eviction Policies

**LRU (Least Recently Used)**:
```typescript
class LRUCache<K, V> {
    private cache = new Map<K, V>();
    private maxSize: number;

    constructor(maxSize: number) {
        this.maxSize = maxSize;
    }

    get(key: K): V | undefined {
        if (!this.cache.has(key)) {
            return undefined;
        }

        // Move to end (most recently used)
        const value = this.cache.get(key)!;
        this.cache.delete(key);
        this.cache.set(key, value);

        return value;
    }

    set(key: K, value: V): void {
        // Delete if exists (to update position)
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }

        // Add to end
        this.cache.set(key, value);

        // Evict oldest if over capacity
        if (this.cache.size > this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }

    has(key: K): boolean {
        return this.cache.has(key);
    }

    delete(key: K): boolean {
        return this.cache.delete(key);
    }

    clear(): void {
        this.cache.clear();
    }

    get size(): number {
        return this.cache.size;
    }
}

// Usage
const cache = new LRUCache<string, User>(1000); // Max 1000 items

cache.set('user:1', user1);
cache.set('user:2', user2);
// ... 999 more items
cache.set('user:1001', user1001); // Evicts user:1 (least recently used)
```

**TTL (Time To Live)**:
```typescript
class TTLCache<K, V> {
    private cache = new Map<K, {value: V, expiry: number}>();

    set(key: K, value: V, ttlMs: number): void {
        const expiry = Date.now() + ttlMs;
        this.cache.set(key, {value, expiry});
    }

    get(key: K): V | undefined {
        const item = this.cache.get(key);

        if (!item) {
            return undefined;
        }

        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            return undefined;
        }

        return item.value;
    }

    cleanup(): void {
        const now = Date.now();

        for (const [key, item] of this.cache) {
            if (now > item.expiry) {
                this.cache.delete(key);
            }
        }
    }
}

// Periodic cleanup
const cache = new TTLCache<string, any>();
setInterval(() => cache.cleanup(), 60000); // Clean every minute
```

### 7.2.4 Cache Stampede Prevention

**Problem**: When cache expires, multiple requests fetch data simultaneously.

**Solution: Cache Locking**:
```typescript
class CacheWithLocking {
    private cache: Cache;
    private locks = new Map<string, Promise<any>>();

    async get<T>(
        key: string,
        loader: () => Promise<T>,
        ttl: number
    ): Promise<T> {
        // Try cache
        const cached = await this.cache.get(key);
        if (cached) {
            return cached;
        }

        // Check if another request is already loading
        if (this.locks.has(key)) {
            console.log(`Waiting for existing load: ${key}`);
            return this.locks.get(key)!;
        }

        // Start loading
        console.log(`Loading: ${key}`);
        const loadPromise = loader().then(async (value) => {
            await this.cache.set(key, value, ttl);
            this.locks.delete(key);
            return value;
        }).catch((error) => {
            this.locks.delete(key);
            throw error;
        });

        this.locks.set(key, loadPromise);
        return loadPromise;
    }
}

// Usage
const cache = new CacheWithLocking();

// 100 concurrent requests for same key
const promises = Array(100).fill(null).map(() =>
    cache.get('user:123', () => fetchUserFromDB('123'), 300)
);

// Only ONE database call happens!
await Promise.all(promises);
```

**Solution: Probabilistic Early Expiration**:
```typescript
class SmartCache {
    async get<T>(
        key: string,
        loader: () => Promise<T>,
        ttl: number
    ): Promise<T> {
        const item = await this.cache.getWithTTL(key);

        if (!item) {
            // Cache miss, load normally
            const value = await loader();
            await this.cache.set(key, value, ttl);
            return value;
        }

        // Probabilistically refresh before expiry
        const timeLeft = item.expiresAt - Date.now();
        const refreshProbability = 1 - (timeLeft / ttl);

        if (Math.random() < refreshProbability) {
            // Refresh in background
            console.log(`Probabilistically refreshing: ${key}`);
            loader().then(value => this.cache.set(key, value, ttl));
        }

        return item.value;
    }
}
```

## 7.3 Database Optimization

### 7.3.1 Indexing

**Index Types**:

**B-Tree Index** (default):
```sql
-- Good for: Equality and range queries
CREATE INDEX idx_users_email ON users(email);

-- Query uses index:
SELECT * FROM users WHERE email = 'user@example.com';
SELECT * FROM users WHERE email LIKE 'user%';
SELECT * FROM users WHERE email > 'a@example.com' AND email < 'z@example.com';
```

**Hash Index**:
```sql
-- Good for: Only equality queries
CREATE INDEX idx_users_email_hash ON users USING HASH (email);

-- Uses index:
SELECT * FROM users WHERE email = 'user@example.com';

-- Does NOT use index:
SELECT * FROM users WHERE email LIKE 'user%';
```

**Composite Index**:
```sql
-- Index on multiple columns
CREATE INDEX idx_users_status_created ON users(status, created_at);

-- Uses index efficiently:
SELECT * FROM users WHERE status = 'active';
SELECT * FROM users WHERE status = 'active' AND created_at > '2024-01-01';

-- Uses index partially (only status):
SELECT * FROM users WHERE created_at > '2024-01-01';

-- Does NOT use index:
SELECT * FROM users WHERE created_at > '2024-01-01' AND status = 'active';
-- Column order matters!
```

**Covering Index**:
```sql
-- Include all columns needed by query
CREATE INDEX idx_users_email_covering ON users(email)
INCLUDE (name, status);

-- Query satisfied entirely by index (no table lookup needed):
SELECT name, status FROM users WHERE email = 'user@example.com';
```

**Partial Index**:
```sql
-- Index only subset of rows
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- Uses index:
SELECT * FROM users WHERE status = 'active' AND email = 'user@example.com';

-- Does NOT use index:
SELECT * FROM users WHERE status = 'inactive' AND email = 'user@example.com';
```

**Full-Text Index**:
```sql
-- For text search
CREATE INDEX idx_posts_content_fulltext ON posts
USING GIN (to_tsvector('english', content));

-- Full-text search:
SELECT * FROM posts
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'postgresql & performance');
```

### 7.3.2 Query Optimization

**EXPLAIN ANALYZE**:
```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 10;

/*
Output:
GroupAggregate  (cost=1234.56..5678.90 rows=100 width=16)
                (actual time=1.234..5.678 rows=50 loops=1)
  Group Key: u.id
  Filter: (count(o.id) > 10)
  Rows Removed by Filter: 25
  ->  Sort  (cost=1234.56..1234.78 rows=100 width=8)
            (actual time=1.200..1.220 rows=100 loops=1)
        Sort Key: u.id
        Sort Method: quicksort  Memory: 25kB
        ->  Hash Left Join  (cost=100.00..800.00 rows=1000 width=8)
                          (actual time=0.100..0.800 rows=1000 loops=1)
              Hash Cond: (o.user_id = u.id)
              ->  Seq Scan on orders o  (cost=0.00..500.00 rows=10000 width=4)
                                       (actual time=0.010..0.500 rows=10000 loops=1)
              ->  Hash  (cost=50.00..50.00 rows=100 width=4)
                       (actual time=0.050..0.050 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 8kB
                    ->  Index Scan using idx_users_status on users u
                        (cost=0.00..50.00 rows=100 width=4)
                        (actual time=0.005..0.040 rows=100 loops=1)
                          Index Cond: (status = 'active')
Planning Time: 0.234 ms
Execution Time: 5.789 ms
*/

-- Look for:
-- - Seq Scan (bad for large tables, needs index)
-- - High actual time
-- - Rows removed by filter (inefficient filtering)
-- - Sort operations (consider index for ORDER BY)
```

**N+1 Query Problem**:
```typescript
// BAD: N+1 queries
async function getPosts() {
    const posts = await db.query('SELECT * FROM posts'); // 1 query

    for (const post of posts) {
        post.author = await db.query(
            'SELECT * FROM users WHERE id = $1',
            [post.author_id]
        ); // N queries!
    }

    return posts;
}

// GOOD: Join or batch
async function getPosts() {
    const posts = await db.query(`
        SELECT
            p.*,
            u.name as author_name,
            u.email as author_email
        FROM posts p
        JOIN users u ON p.author_id = u.id
    `); // 1 query

    return posts;
}

// GOOD: Batch with IN clause
async function getPosts() {
    const posts = await db.query('SELECT * FROM posts');

    const authorIds = [...new Set(posts.map(p => p.author_id))];

    const authors = await db.query(
        'SELECT * FROM users WHERE id = ANY($1)',
        [authorIds]
    );

    const authorMap = new Map(authors.map(a => [a.id, a]));

    posts.forEach(post => {
        post.author = authorMap.get(post.author_id);
    });

    return posts;
}
```

**Pagination**:
```sql
-- BAD: OFFSET gets slower with larger offsets
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;
-- Has to scan 10,020 rows and discard 10,000

-- GOOD: Cursor-based pagination
SELECT * FROM posts
WHERE created_at < '2024-01-01 12:00:00'
ORDER BY created_at DESC
LIMIT 20;
-- Only scans 20 rows using index
```

### 7.3.3 Connection Pooling

```typescript
import { Pool } from 'pg';

const pool = new Pool({
    host: 'localhost',
    port: 5432,
    database: 'mydb',
    user: 'user',
    password: 'password',

    // Pool configuration
    min: 10,              // Minimum connections
    max: 20,              // Maximum connections
    idleTimeoutMillis: 30000,  // Close idle connections after 30s
    connectionTimeoutMillis: 5000,  // Wait 5s for connection

    // Application-level timeout
    statement_timeout: 10000,  // 10s query timeout
});

// Monitor pool
pool.on('connect', (client) => {
    console.log('New client connected');
});

pool.on('acquire', (client) => {
    console.log('Client acquired from pool');
});

pool.on('remove', (client) => {
    console.log('Client removed from pool');
});

pool.on('error', (err, client) => {
    console.error('Unexpected error on idle client', err);
});

// Usage
async function queryUser(id: string) {
    // Automatically acquires and releases connection
    const result = await pool.query(
        'SELECT * FROM users WHERE id = $1',
        [id]
    );

    return result.rows[0];
}

// Manual connection management (for transactions)
async function transferMoney(fromId: string, toId: string, amount: number) {
    const client = await pool.connect();

    try {
        await client.query('BEGIN');

        await client.query(
            'UPDATE accounts SET balance = balance - $1 WHERE user_id = $2',
            [amount, fromId]
        );

        await client.query(
            'UPDATE accounts SET balance = balance + $1 WHERE user_id = $2',
            [amount, toId]
        );

        await client.query('COMMIT');
    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release(); // Return to pool
    }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('Closing database pool...');
    await pool.end();
    process.exit(0);
});
```

## 7.4 Horizontal vs Vertical Scaling

### 7.4.1 Vertical Scaling (Scale Up)

**Definition**: Add more resources to existing server (CPU, RAM, disk).

**Pros**:
- Simpler (no code changes)
- No data distribution complexity
- Lower latency (everything on one machine)

**Cons**:
- Limited by hardware constraints
- Single point of failure
- More expensive (diminishing returns)
- Downtime during upgrades

**When to Use**:
- Small to medium applications
- Monolithic architecture
- Stateful applications
- Database servers (often vertically scaled first)

### 7.4.2 Horizontal Scaling (Scale Out)

**Definition**: Add more servers.

**Pros**:
- Virtually unlimited scaling
- Higher availability (no single point of failure)
- Cost-effective (commodity hardware)
- No downtime (add servers without stopping others)

**Cons**:
- More complex (load balancing, data distribution)
- Network latency between servers
- Data consistency challenges
- Application must be stateless

**When to Use**:
- Large-scale applications
- Microservices architecture
- Stateless services
- Read-heavy workloads

### 7.4.3 Database Sharding

**Horizontal Partitioning**: Split data across multiple databases.

**Sharding Strategies**:

**Range-Based Sharding**:
```typescript
class RangeShardRouter {
    private shards = [
        { range: [0, 1000000], db: db1 },
        { range: [1000001, 2000000], db: db2 },
        { range: [2000001, 3000000], db: db3 }
    ];

    getShard(userId: number): Database {
        for (const shard of this.shards) {
            if (userId >= shard.range[0] && userId <= shard.range[1]) {
                return shard.db;
            }
        }

        throw new Error('No shard found for user');
    }
}

// Usage
const router = new RangeShardRouter();
const db = router.getShard(userId);
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

**Hash-Based Sharding**:
```typescript
class HashShardRouter {
    private shards: Database[];

    constructor(shards: Database[]) {
        this.shards = shards;
    }

    getShard(key: string): Database {
        const hash = this.hash(key);
        const index = hash % this.shards.length;
        return this.shards[index];
    }

    private hash(key: string): number {
        let hash = 0;
        for (let i = 0; i < key.length; i++) {
            hash = ((hash << 5) - hash) + key.charCodeAt(i);
            hash = hash & hash;
        }
        return Math.abs(hash);
    }
}
```

**Geographic Sharding**:
```typescript
class GeoShardRouter {
    private shards = new Map<string, Database>([
        ['US', usDatabase],
        ['EU', euDatabase],
        ['ASIA', asiaDatabase]
    ]);

    getShard(region: string): Database {
        return this.shards.get(region) || this.shards.get('US')!;
    }
}
```

**Challenges**:
- Cross-shard queries (need to query multiple shards)
- Distributed transactions
- Rebalancing when adding/removing shards
- Hotspots (uneven data distribution)

**Cross-Shard Query**:
```typescript
class ShardedUserRepository {
    constructor(private router: ShardRouter) {}

    async findById(id: string): Promise<User> {
        const shard = this.router.getShard(id);
        return shard.query('SELECT * FROM users WHERE id = $1', [id]);
    }

    async search(criteria: SearchCriteria): Promise<User[]> {
        // Must query all shards
        const shards = this.router.getAllShards();

        const results = await Promise.all(
            shards.map(shard =>
                shard.query('SELECT * FROM users WHERE name LIKE $1', [criteria.name])
            )
        );

        // Merge results from all shards
        const allUsers = results.flat();

        // Sort and paginate in application
        return allUsers
            .sort((a, b) => a.name.localeCompare(b.name))
            .slice(criteria.offset, criteria.offset + criteria.limit);
    }
}
```

### 7.4.4 Database Replication

**Primary-Replica (Master-Slave)**:
```
    Primary (Write)
         |
    +----+----+
    |         |
Replica1  Replica2  (Read)
```

```typescript
class DatabaseCluster {
    private primary: Database;
    private replicas: Database[];
    private replicaIndex = 0;

    constructor(primary: Database, replicas: Database[]) {
        this.primary = primary;
        this.replicas = replicas;
    }

    async write(query: string, params: any[]): Promise<any> {
        // All writes go to primary
        return this.primary.query(query, params);
    }

    async read(query: string, params: any[]): Promise<any> {
        // Reads go to replicas (load balanced)
        const replica = this.getNextReplica();
        return replica.query(query, params);
    }

    private getNextReplica(): Database {
        const replica = this.replicas[this.replicaIndex];
        this.replicaIndex = (this.replicaIndex + 1) % this.replicas.length;
        return replica;
    }
}

// Usage
class UserRepository {
    constructor(private db: DatabaseCluster) {}

    async create(user: CreateUserDTO): Promise<User> {
        // Write to primary
        const result = await this.db.write(
            'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
            [user.name, user.email]
        );

        return result.rows[0];
    }

    async findById(id: string): Promise<User> {
        // Read from replica
        const result = await this.db.read(
            'SELECT * FROM users WHERE id = $1',
            [id]
        );

        return result.rows[0];
    }

    async findAll(): Promise<User[]> {
        // Read from replica
        const result = await this.db.read('SELECT * FROM users', []);
        return result.rows;
    }
}
```

**Multi-Primary (Multi-Master)**:
```
Primary1 ←→ Primary2 ←→ Primary3
```

- All nodes accept writes
- More complex conflict resolution
- Higher availability

**Conflict Resolution**:
```typescript
interface ConflictResolver<T> {
    resolve(local: T, remote: T): T;
}

class LastWriteWinsResolver<T extends {updatedAt: Date}> implements ConflictResolver<T> {
    resolve(local: T, remote: T): T {
        return local.updatedAt > remote.updatedAt ? local : remote;
    }
}

class MergeResolver implements ConflictResolver<any> {
    resolve(local: any, remote: any): any {
        // Custom merge logic
        return {
            ...local,
            ...remote,
            mergedAt: new Date()
        };
    }
}
```


---

# PART 8: SECURITY PRINCIPLES

## 8.1 OWASP Top 10

### 8.1.1 Injection Attacks

**SQL Injection**:
```typescript
// VULNERABLE: Never do this!
async function getUser(email: string) {
    const query = `SELECT * FROM users WHERE email = '${email}'`;
    return db.query(query);
}

// Attack: email = "' OR '1'='1"
// Resulting query: SELECT * FROM users WHERE email = '' OR '1'='1'
// Returns all users!

// SECURE: Use parameterized queries
async function getUser(email: string) {
    const query = 'SELECT * FROM users WHERE email = $1';
    return db.query(query, [email]);
}

// Attack fails: Treats entire input as string literal
```

**NoSQL Injection**:
```javascript
// VULNERABLE
app.post('/login', (req, res) => {
    db.users.findOne({
        email: req.body.email,
        password: req.body.password
    });
});

// Attack: POST { "email": {"$ne": null}, "password": {"$ne": null} }
// Matches any user!

// SECURE: Validate and sanitize
app.post('/login', (req, res) => {
    const { email, password } = req.body;

    // Validate types
    if (typeof email !== 'string' || typeof password !== 'string') {
        return res.status(400).send('Invalid input');
    }

    db.users.findOne({
        email: email,
        password: hashPassword(password)
    });
});
```

**Command Injection**:
```typescript
// VULNERABLE
import { exec } from 'child_process';

app.get('/ping', (req, res) => {
    const host = req.query.host;
    exec(`ping -c 1 ${host}`, (error, stdout) => {
        res.send(stdout);
    });
});

// Attack: /ping?host=google.com; rm -rf /
// Executes: ping -c 1 google.com; rm -rf /

// SECURE: Validate input and use safer alternatives
app.get('/ping', (req, res) => {
    const host = req.query.host as string;

    // Validate hostname
    if (!/^[a-zA-Z0-9.-]+$/.test(host)) {
        return res.status(400).send('Invalid hostname');
    }

    // Use spawn instead of exec (doesn't invoke shell)
    const { spawn } = require('child_process');
    const ping = spawn('ping', ['-c', '1', host]);

    let output = '';
    ping.stdout.on('data', (data: Buffer) => {
        output += data.toString();
    });

    ping.on('close', () => {
        res.send(output);
    });
});
```

### 8.1.2 Broken Authentication

**Password Storage**:
```typescript
import bcrypt from 'bcrypt';
import crypto from 'crypto';

// VULNERABLE: Plain text passwords
class BadUserService {
    async createUser(email: string, password: string) {
        await db.users.insert({
            email,
            password  // NEVER store plain text!
        });
    }

    async login(email: string, password: string) {
        const user = await db.users.findOne({ email });
        return user && user.password === password;
    }
}

// VULNERABLE: MD5/SHA1 (too fast, no salt)
class StillBadUserService {
    async createUser(email: string, password: string) {
        const hash = crypto.createHash('md5')
            .update(password)
            .digest('hex');

        await db.users.insert({ email, password: hash });
    }
}

// SECURE: bcrypt/scrypt/argon2
class GoodUserService {
    async createUser(email: string, password: string) {
        // bcrypt automatically salts and uses slow hashing
        const hash = await bcrypt.hash(password, 12);

        await db.users.insert({
            email,
            password: hash
        });
    }

    async login(email: string, password: string) {
        const user = await db.users.findOne({ email });

        if (!user) {
            // Use same timing to prevent user enumeration
            await bcrypt.hash(password, 12);
            return null;
        }

        const isValid = await bcrypt.compare(password, user.password);
        return isValid ? user : null;
    }
}
```

**Session Management**:
```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';

app.use(session({
    store: new RedisStore({ client: redisClient }),
    secret: process.env.SESSION_SECRET!, // Strong random secret
    resave: false,
    saveUninitialized: false,

    name: 'sessionId',  // Don't use default name
    cookie: {
        secure: true,      // HTTPS only
        httpOnly: true,    // No JavaScript access
        sameSite: 'strict', // CSRF protection
        maxAge: 1000 * 60 * 60 * 24  // 24 hours
    }
}));

// Regenerate session ID after login (prevent fixation)
app.post('/login', async (req, res) => {
    const user = await authenticate(req.body.email, req.body.password);

    if (user) {
        req.session.regenerate((err) => {
            if (err) {
                return res.status(500).send('Login failed');
            }

            req.session.userId = user.id;
            res.send({ success: true });
        });
    } else {
        res.status(401).send('Invalid credentials');
    }
});

// Destroy session on logout
app.post('/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).send('Logout failed');
        }

        res.clearCookie('sessionId');
        res.send({ success: true });
    });
});
```

**JWT Best Practices**:
```typescript
import jwt from 'jsonwebtoken';

// Token generation
function generateTokens(user: User) {
    // Short-lived access token
    const accessToken = jwt.sign(
        {
            userId: user.id,
            email: user.email,
            role: user.role
        },
        process.env.JWT_ACCESS_SECRET!,
        { expiresIn: '15m' }  // 15 minutes
    );

    // Long-lived refresh token
    const refreshToken = jwt.sign(
        { userId: user.id },
        process.env.JWT_REFRESH_SECRET!,
        { expiresIn: '7d' }  // 7 days
    );

    return { accessToken, refreshToken };
}

// Middleware
function authenticateToken(req: Request, res: Response, next: NextFunction) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).send('Access token required');
    }

    jwt.verify(token, process.env.JWT_ACCESS_SECRET!, (err, user) => {
        if (err) {
            if (err.name === 'TokenExpiredError') {
                return res.status(401).send('Token expired');
            }
            return res.status(403).send('Invalid token');
        }

        req.user = user;
        next();
    });
}

// Refresh endpoint
app.post('/refresh', (req, res) => {
    const { refreshToken } = req.body;

    if (!refreshToken) {
        return res.status(401).send('Refresh token required');
    }

    jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET!, (err, payload) => {
        if (err) {
            return res.status(403).send('Invalid refresh token');
        }

        // Check if token is blacklisted
        if (isBlacklisted(refreshToken)) {
            return res.status(403).send('Token revoked');
        }

        const user = getUserById(payload.userId);
        const tokens = generateTokens(user);

        res.json(tokens);
    });
});

// Token blacklist (for logout)
const blacklist = new Set<string>();

app.post('/logout', (req, res) => {
    const { refreshToken } = req.body;
    blacklist.add(refreshToken);
    res.send({ success: true });
});

function isBlacklisted(token: string): boolean {
    return blacklist.has(token);
}
```

### 8.1.3 Cross-Site Scripting (XSS)

**Stored XSS**:
```typescript
// VULNERABLE: Rendering untrusted data
app.get('/profile/:id', async (req, res) => {
    const user = await db.users.findById(req.params.id);

    // If user.bio contains: <script>alert('XSS')</script>
    // This will execute in browser!
    res.send(`<div>Bio: ${user.bio}</div>`);
});

// SECURE: Escape HTML
import escape from 'escape-html';

app.get('/profile/:id', async (req, res) => {
    const user = await db.users.findById(req.params.id);

    // Escapes < > & " ' to HTML entities
    const safeBio = escape(user.bio);
    res.send(`<div>Bio: ${safeBio}</div>`);
});

// BETTER: Use templating engine with auto-escaping
app.set('view engine', 'ejs'); // EJS auto-escapes by default

app.get('/profile/:id', async (req, res) => {
    const user = await db.users.findById(req.params.id);
    res.render('profile', { user }); // Auto-escaped
});
```

**React XSS Prevention**:
```typescript
// React escapes by default
function UserProfile({ user }) {
    // Safe: React escapes text content
    return <div>Bio: {user.bio}</div>;
}

// VULNERABLE: dangerouslySetInnerHTML
function UserProfile({ user }) {
    // DON'T DO THIS unless you trust the HTML!
    return <div dangerouslySetInnerHTML={{__html: user.bio}} />;
}

// SECURE: Sanitize HTML
import DOMPurify from 'dompurify';

function UserProfile({ user }) {
    const sanitizedBio = DOMPurify.sanitize(user.bio);
    return <div dangerouslySetInnerHTML={{__html: sanitizedBio}} />;
}
```

**Content Security Policy (CSP)**:
```typescript
import helmet from 'helmet';

app.use(helmet.contentSecurityPolicy({
    directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'nonce-{RANDOM}'"],  // Allow only nonce scripts
        styleSrc: ["'self'", "https://fonts.googleapis.com"],
        imgSrc: ["'self'", "https:", "data:"],
        fontSrc: ["'self'", "https://fonts.gstatic.com"],
        connectSrc: ["'self'", "https://api.example.com"],
        objectSrc: ["'none'"],
        upgradeInsecureRequests: []
    }
}));

// Generate nonce for inline scripts
app.use((req, res, next) => {
    res.locals.nonce = crypto.randomBytes(16).toString('base64');
    next();
});

// Use nonce in templates
// <script nonce="<%= nonce %>">console.log('safe');</script>
```

### 8.1.4 Cross-Site Request Forgery (CSRF)

```typescript
import csrf from 'csurf';

// Setup CSRF protection
const csrfProtection = csrf({ cookie: true });

app.use(cookieParser());
app.use(csrfProtection);

// Send token to client
app.get('/form', (req, res) => {
    res.render('form', { csrfToken: req.csrfToken() });
});

// Verify token on submission
app.post('/transfer', (req, res) => {
    // CSRF middleware automatically verifies token
    // from req.body._csrf or req.headers['csrf-token']

    // Process transfer
    transferMoney(req.body.from, req.body.to, req.body.amount);
    res.send('Success');
});

// HTML form
/*
<form action="/transfer" method="POST">
  <input type="hidden" name="_csrf" value="<%= csrfToken %>">
  <input name="to" placeholder="Recipient">
  <input name="amount" placeholder="Amount">
  <button type="submit">Transfer</button>
</form>
*/

// AJAX request
/*
fetch('/transfer', {
  method: 'POST',
  headers: {
    'CSRF-Token': document.querySelector('[name="_csrf"]').value,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ to: 'user2', amount: 100 })
});
*/

// SameSite cookie (additional protection)
app.use(session({
    cookie: {
        sameSite: 'strict'  // Browser won't send cookie on cross-origin requests
    }
}));
```

### 8.1.5 Security Misconfiguration

```typescript
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

// Security headers
app.use(helmet());

// Specific headers
app.use(helmet.hsts({
    maxAge: 31536000,  // 1 year
    includeSubDomains: true,
    preload: true
}));

app.use(helmet.frameguard({ action: 'deny' })); // Prevent clickjacking
app.use(helmet.noSniff()); // Prevent MIME sniffing
app.use(helmet.xssFilter()); // XSS protection

// Hide Express
app.disable('x-powered-by');

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP'
});

app.use('/api/', limiter);

// Stricter rate limit for auth endpoints
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5,  // Only 5 attempts
    skipSuccessfulRequests: true,  // Don't count successful logins
    message: 'Too many login attempts, please try again later'
});

app.use('/login', authLimiter);
app.use('/register', authLimiter);

// Environment-specific settings
if (process.env.NODE_ENV === 'production') {
    // Force HTTPS
    app.use((req, res, next) => {
        if (req.header('x-forwarded-proto') !== 'https') {
            return res.redirect(`https://${req.header('host')}${req.url}`);
        }
        next();
    });

    // Disable error stack traces
    app.use((err, req, res, next) => {
        res.status(500).send('Internal Server Error');
        // Log error internally
        logger.error(err);
    });
} else {
    // Development: Show detailed errors
    app.use((err, req, res, next) => {
        res.status(500).send({
            message: err.message,
            stack: err.stack
        });
    });
}

// Secrets management
// NEVER hardcode secrets!
// ❌ const API_KEY = 'sk-1234567890abcdef';

// ✅ Use environment variables
const API_KEY = process.env.API_KEY;

// ✅ Use secret management service
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

const secretsManager = new SecretsManager({ region: 'us-east-1' });

async function getSecret(secretName: string) {
    const response = await secretsManager.getSecretValue({
        SecretId: secretName
    });

    return JSON.parse(response.SecretString!);
}
```

### 8.1.6 Sensitive Data Exposure

**Encryption at Rest**:
```typescript
import crypto from 'crypto';

class EncryptionService {
    private algorithm = 'aes-256-gcm';
    private key: Buffer;

    constructor(secretKey: string) {
        // Derive 256-bit key from secret
        this.key = crypto.scryptSync(secretKey, 'salt', 32);
    }

    encrypt(data: string): string {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);

        let encrypted = cipher.update(data, 'utf8', 'hex');
        encrypted += cipher.final('hex');

        const authTag = cipher.getAuthTag();

        // Return iv + authTag + encrypted
        return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
    }

    decrypt(encrypted: string): string {
        const [ivHex, authTagHex, encryptedData] = encrypted.split(':');

        const iv = Buffer.from(ivHex, 'hex');
        const authTag = Buffer.from(authTagHex, 'hex');

        const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
        decipher.setAuthTag(authTag);

        let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
        decrypted += decipher.final('utf8');

        return decrypted;
    }
}

// Usage
const encryptionService = new EncryptionService(process.env.ENCRYPTION_KEY!);

// Encrypt sensitive data before storing
class UserRepository {
    async create(user: CreateUserDTO) {
        const encryptedSSN = encryptionService.encrypt(user.ssn);

        await db.users.insert({
            ...user,
            ssn: encryptedSSN
        });
    }

    async findById(id: string) {
        const user = await db.users.findById(id);

        if (user && user.ssn) {
            user.ssn = encryptionService.decrypt(user.ssn);
        }

        return user;
    }
}
```

**Encryption in Transit**:
```typescript
import https from 'https';
import fs from 'fs';

// HTTPS server
const options = {
    key: fs.readFileSync('private-key.pem'),
    cert: fs.readFileSync('certificate.pem')
};

const server = https.createServer(options, app);

server.listen(443, () => {
    console.log('HTTPS server running on port 443');
});

// Force TLS 1.2+
import tls from 'tls';

tls.DEFAULT_MIN_VERSION = 'TLSv1.2';

// Database connection with SSL
const pool = new Pool({
    host: 'localhost',
    database: 'mydb',
    ssl: {
        rejectUnauthorized: true,
        ca: fs.readFileSync('/path/to/server-ca.pem'),
        key: fs.readFileSync('/path/to/client-key.pem'),
        cert: fs.readFileSync('/path/to/client-cert.pem')
    }
});
```

**Data Masking**:
```typescript
function maskSensitiveData(data: any): any {
    const clone = JSON.parse(JSON.stringify(data));

    // Mask credit card numbers
    if (clone.creditCard) {
        clone.creditCard = clone.creditCard.replace(/\d(?=\d{4})/g, '*');
        // 1234567890123456 -> ************3456
    }

    // Mask email
    if (clone.email) {
        const [name, domain] = clone.email.split('@');
        clone.email = `${name.charAt(0)}***@${domain}`;
        // john@example.com -> j***@example.com
    }

    // Mask phone
    if (clone.phone) {
        clone.phone = clone.phone.replace(/\d(?=\d{4})/g, '*');
    }

    return clone;
}

// Use in logging
logger.info('User created', maskSensitiveData(userData));
// Logs: { email: 'j***@example.com', creditCard: '************3456' }
```

## 8.2 Authentication & Authorization

### 8.2.1 Multi-Factor Authentication (MFA)

```typescript
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';

class MFAService {
    // Generate secret for user
    async enableMFA(userId: string) {
        const secret = speakeasy.generateSecret({
            name: `MyApp (${userId})`,
            issuer: 'MyApp'
        });

        // Save secret to database
        await db.users.update(userId, {
            mfaSecret: secret.base32,
            mfaEnabled: false  // Not enabled until verified
        });

        // Generate QR code for user to scan
        const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url!);

        return {
            secret: secret.base32,
            qrCode: qrCodeUrl
        };
    }

    // Verify setup
    async verifyMFASetup(userId: string, token: string) {
        const user = await db.users.findById(userId);

        const verified = speakeasy.totp.verify({
            secret: user.mfaSecret,
            encoding: 'base32',
            token,
            window: 2  // Allow 2 time steps before/after
        });

        if (verified) {
            await db.users.update(userId, { mfaEnabled: true });
            return true;
        }

        return false;
    }

    // Verify login token
    async verifyMFAToken(userId: string, token: string) {
        const user = await db.users.findById(userId);

        if (!user.mfaEnabled) {
            throw new Error('MFA not enabled');
        }

        return speakeasy.totp.verify({
            secret: user.mfaSecret,
            encoding: 'base32',
            token,
            window: 2
        });
    }
}

// Login flow with MFA
app.post('/login', async (req, res) => {
    const { email, password } = req.body;

    const user = await authenticate(email, password);

    if (!user) {
        return res.status(401).send('Invalid credentials');
    }

    if (user.mfaEnabled) {
        // Issue temporary token
        const tempToken = jwt.sign(
            { userId: user.id, mfaPending: true },
            process.env.JWT_SECRET!,
            { expiresIn: '5m' }
        );

        return res.json({
            tempToken,
            mfaRequired: true
        });
    }

    // MFA not enabled, issue full token
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET!);
    res.json({ token });
});

app.post('/login/mfa', async (req, res) => {
    const { tempToken, mfaToken } = req.body;

    // Verify temp token
    const payload = jwt.verify(tempToken, process.env.JWT_SECRET!);

    if (!payload.mfaPending) {
        return res.status(400).send('Invalid token');
    }

    // Verify MFA token
    const verified = await mfaService.verifyMFAToken(payload.userId, mfaToken);

    if (!verified) {
        return res.status(401).send('Invalid MFA token');
    }

    // Issue full token
    const token = jwt.sign({ userId: payload.userId }, process.env.JWT_SECRET!);
    res.json({ token });
});
```

### 8.2.2 Role-Based Access Control (RBAC)

```typescript
enum Permission {
    READ_USER = 'read:user',
    WRITE_USER = 'write:user',
    DELETE_USER = 'delete:user',
    READ_ADMIN = 'read:admin',
    WRITE_ADMIN = 'write:admin'
}

interface Role {
    name: string;
    permissions: Permission[];
}

const roles: Record<string, Role> = {
    guest: {
        name: 'guest',
        permissions: [Permission.READ_USER]
    },
    user: {
        name: 'user',
        permissions: [
            Permission.READ_USER,
            Permission.WRITE_USER
        ]
    },
    admin: {
        name: 'admin',
        permissions: [
            Permission.READ_USER,
            Permission.WRITE_USER,
            Permission.DELETE_USER,
            Permission.READ_ADMIN,
            Permission.WRITE_ADMIN
        ]
    }
};

// Middleware
function requirePermission(...requiredPermissions: Permission[]) {
    return (req: Request, res: Response, next: NextFunction) => {
        const user = req.user; // From auth middleware

        if (!user) {
            return res.status(401).send('Unauthorized');
        }

        const userRole = roles[user.role];
        const hasPermission = requiredPermissions.every(permission =>
            userRole.permissions.includes(permission)
        );

        if (!hasPermission) {
            return res.status(403).send('Forbidden');
        }

        next();
    };
}

// Usage
app.get('/users',
    authenticate,
    requirePermission(Permission.READ_USER),
    (req, res) => {
        // List users
    }
);

app.post('/users',
    authenticate,
    requirePermission(Permission.WRITE_USER),
    (req, res) => {
        // Create user
    }
);

app.delete('/users/:id',
    authenticate,
    requirePermission(Permission.DELETE_USER),
    (req, res) => {
        // Delete user
    }
);
```

### 8.2.3 Attribute-Based Access Control (ABAC)

```typescript
interface AccessPolicy {
    effect: 'allow' | 'deny';
    actions: string[];
    resources: string[];
    conditions?: Record<string, any>;
}

class ABACService {
    private policies: AccessPolicy[] = [
        {
            effect: 'allow',
            actions: ['read', 'update'],
            resources: ['document:*'],
            conditions: {
                'document.ownerId': '{{user.id}}'  // User can only access own documents
            }
        },
        {
            effect: 'allow',
            actions: ['read'],
            resources: ['document:*'],
            conditions: {
                'document.visibility': 'public'  // Anyone can read public documents
            }
        },
        {
            effect: 'allow',
            actions: ['*'],
            resources: ['*'],
            conditions: {
                'user.role': 'admin'  // Admins can do anything
            }
        }
    ];

    canAccess(
        user: User,
        action: string,
        resource: any
    ): boolean {
        for (const policy of this.policies) {
            if (this.matchesPolicy(user, action, resource, policy)) {
                return policy.effect === 'allow';
            }
        }

        return false; // Deny by default
    }

    private matchesPolicy(
        user: User,
        action: string,
        resource: any,
        policy: AccessPolicy
    ): boolean {
        // Check action
        if (!policy.actions.includes('*') && !policy.actions.includes(action)) {
            return false;
        }

        // Check resource
        const resourceType = `${resource.type}:${resource.id}`;
        const matchesResource = policy.resources.some(pattern =>
            this.matchesPattern(resourceType, pattern)
        );

        if (!matchesResource) {
            return false;
        }

        // Check conditions
        if (policy.conditions) {
            for (const [key, value] of Object.entries(policy.conditions)) {
                const resolvedValue = this.resolveVariable(value, { user, resource });
                const actualValue = this.getNestedValue(
                    key.startsWith('user.') ? user : resource,
                    key.replace(/^(user|resource)\./, '')
                );

                if (actualValue !== resolvedValue) {
                    return false;
                }
            }
        }

        return true;
    }

    private matchesPattern(value: string, pattern: string): boolean {
        if (pattern === '*') return true;

        const regex = new RegExp(
            '^' + pattern.replace(/\*/g, '.*') + '$'
        );

        return regex.test(value);
    }

    private resolveVariable(value: string, context: any): any {
        if (typeof value !== 'string' || !value.startsWith('{{')) {
            return value;
        }

        const path = value.slice(2, -2).trim();
        return this.getNestedValue(context, path);
    }

    private getNestedValue(obj: any, path: string): any {
        return path.split('.').reduce((curr, key) => curr?.[key], obj);
    }
}

// Usage
const abac = new ABACService();

app.get('/documents/:id', authenticate, async (req, res) => {
    const document = await db.documents.findById(req.params.id);

    if (!abac.canAccess(req.user, 'read', document)) {
        return res.status(403).send('Access denied');
    }

    res.json(document);
});

app.put('/documents/:id', authenticate, async (req, res) => {
    const document = await db.documents.findById(req.params.id);

    if (!abac.canAccess(req.user, 'update', document)) {
        return res.status(403).send('Access denied');
    }

    // Update document
    const updated = await db.documents.update(req.params.id, req.body);
    res.json(updated);
});
```


---

# PART 9: DEVOPS & DEPLOYMENT

## 9.1 CI/CD Pipelines

### 9.1.1 Continuous Integration

**GitHub Actions Example**:
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run security audit
        run: npm audit --audit-level=moderate

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  build:
    runs-on: ubuntu-latest
    needs: [test, security]

    steps:
      - uses: actions/checkout@v3

      - name: Build application
        run: npm run build

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Save Docker image
        run: docker save myapp:${{ github.sha }} | gzip > image.tar.gz

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: docker-image
          path: image.tar.gz
```

### 9.1.2 Continuous Deployment

```yaml
name: CD Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Download artifact
        uses: actions/download-artifact@v3
        with:
          name: docker-image

      - name: Load Docker image
        run: docker load < image.tar.gz

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        run: |
          aws ecr get-login-password --region us-east-1 | \
          docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}

      - name: Tag and push image
        run: |
          docker tag myapp:${{ github.sha }} ${{ secrets.ECR_REGISTRY }}/myapp:staging
          docker push ${{ secrets.ECR_REGISTRY }}/myapp:staging

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster staging-cluster \
            --service myapp-service \
            --force-new-deployment

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster staging-cluster \
            --services myapp-service

      - name: Run smoke tests
        run: |
          curl -f https://staging.myapp.com/health || exit 1

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'

    environment:
      name: production
      url: https://myapp.com

    steps:
      - name: Deploy to production
        run: |
          # Similar to staging but with production cluster
          docker tag myapp:${{ github.sha }} ${{ secrets.ECR_REGISTRY }}/myapp:latest
          docker push ${{ secrets.ECR_REGISTRY }}/myapp:latest

          aws ecs update-service \
            --cluster production-cluster \
            --service myapp-service \
            --force-new-deployment

      - name: Run production smoke tests
        run: |
          curl -f https://myapp.com/health || exit 1

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment complete!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 9.2 Infrastructure as Code

### 9.2.1 Terraform

```hcl
# main.tf
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "myapp-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "myapp-vpc"
    Environment = var.environment
  }
}

# Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "myapp-public-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 100}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "myapp-private-${count.index + 1}"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = "${var.ecr_repository}:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${aws_db_instance.main.endpoint}/myapp"
        }
      ]

      secrets = [
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = var.app_name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.app]
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier             = "${var.app_name}-${var.environment}"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_encrypted      = true
  db_name                = "myapp"
  username               = "admin"
  password               = random_password.db_password.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  skip_final_snapshot    = var.environment != "production"

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  tags = {
    Environment = var.environment
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "myapp"
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

# Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}
```

### 9.2.2 Docker Best Practices

```dockerfile
# Multi-stage build for smaller image
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production image
FROM node:20-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start application
CMD ["node", "dist/index.js"]
```

**.dockerignore**:
```
node_modules
npm-debug.log
dist
.git
.gitignore
.env
.env.local
*.md
.vscode
.idea
coverage
.DS_Store
```

**Docker Compose for Development**:
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    command: npm run dev

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

## 9.3 Monitoring & Observability

### 9.3.1 Logging

```typescript
import winston from 'winston';

// Structured logging
const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: {
        service: 'myapp',
        environment: process.env.NODE_ENV
    },
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            )
        }),
        new winston.transports.File({
            filename: 'logs/error.log',
            level: 'error'
        }),
        new winston.transports.File({
            filename: 'logs/combined.log'
        })
    ]
});

// Request logging middleware
app.use((req, res, next) => {
    const start = Date.now();

    res.on('finish', () => {
        const duration = Date.now() - start;

        logger.info('HTTP Request', {
            method: req.method,
            url: req.url,
            status: res.statusCode,
            duration,
            userAgent: req.get('user-agent'),
            ip: req.ip,
            userId: req.user?.id
        });
    });

    next();
});

// Correlation IDs for request tracing
import { v4 as uuidv4 } from 'uuid';

app.use((req, res, next) => {
    req.id = req.get('X-Request-ID') || uuidv4();
    res.setHeader('X-Request-ID', req.id);
    next();
});

// Enhanced logging with context
class Logger {
    private logger: winston.Logger;

    constructor(private context: Record<string, any> = {}) {
        this.logger = logger;
    }

    info(message: string, meta: Record<string, any> = {}) {
        this.logger.info(message, { ...this.context, ...meta });
    }

    error(message: string, error?: Error, meta: Record<string, any> = {}) {
        this.logger.error(message, {
            ...this.context,
            ...meta,
            error: error ? {
                message: error.message,
                stack: error.stack,
                name: error.name
            } : undefined
        });
    }

    warn(message: string, meta: Record<string, any> = {}) {
        this.logger.warn(message, { ...this.context, ...meta });
    }

    debug(message: string, meta: Record<string, any> = {}) {
        this.logger.debug(message, { ...this.context, ...meta });
    }

    child(context: Record<string, any>): Logger {
        return new Logger({ ...this.context, ...context });
    }
}

// Usage
class UserService {
    private logger: Logger;

    constructor() {
        this.logger = new Logger({ service: 'UserService' });
    }

    async createUser(userData: CreateUserDTO, requestId: string) {
        const logger = this.logger.child({ requestId });

        logger.info('Creating user', { email: userData.email });

        try {
            const user = await db.users.create(userData);

            logger.info('User created successfully', {
                userId: user.id,
                email: user.email
            });

            return user;
        } catch (error) {
            logger.error('Failed to create user', error as Error, {
                email: userData.email
            });
            throw error;
        }
    }
}
```

### 9.3.2 Metrics

```typescript
import prometheus from 'prom-client';

// Enable default metrics (CPU, memory, etc.)
prometheus.collectDefaultMetrics({ prefix: 'myapp_' });

// Custom metrics
const httpRequestDuration = new prometheus.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.001, 0.01, 0.1, 0.5, 1, 5]
});

const httpRequestTotal = new prometheus.Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new prometheus.Gauge({
    name: 'active_connections',
    help: 'Number of active connections'
});

const databaseQueryDuration = new prometheus.Histogram({
    name: 'database_query_duration_seconds',
    help: 'Duration of database queries',
    labelNames: ['query_type'],
    buckets: [0.001, 0.01, 0.1, 0.5, 1]
});

const businessMetric = new prometheus.Gauge({
    name: 'orders_created_today',
    help: 'Number of orders created today'
});

// Middleware
app.use((req, res, next) => {
    const start = Date.now();

    res.on('finish', () => {
        const duration = (Date.now() - start) / 1000;

        httpRequestDuration.observe(
            {
                method: req.method,
                route: req.route?.path || req.path,
                status_code: res.statusCode
            },
            duration
        );

        httpRequestTotal.inc({
            method: req.method,
            route: req.route?.path || req.path,
            status_code: res.statusCode
        });
    });

    next();
});

// Track connections
app.use((req, res, next) => {
    activeConnections.inc();
    res.on('finish', () => activeConnections.dec());
    next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
    res.set('Content-Type', prometheus.register.contentType);
    res.send(await prometheus.register.metrics());
});

// Database instrumentation
class DatabaseClient {
    async query(sql: string) {
        const end = databaseQueryDuration.startTimer({
            query_type: this.getQueryType(sql)
        });

        try {
            return await db.query(sql);
        } finally {
            end();
        }
    }

    private getQueryType(sql: string): string {
        const normalized = sql.trim().toLowerCase();
        if (normalized.startsWith('select')) return 'SELECT';
        if (normalized.startsWith('insert')) return 'INSERT';
        if (normalized.startsWith('update')) return 'UPDATE';
        if (normalized.startsWith('delete')) return 'DELETE';
        return 'OTHER';
    }
}

// Business metrics
class OrderService {
    async createOrder(orderData: CreateOrderDTO) {
        const order = await db.orders.create(orderData);

        // Update business metric
        businessMetric.inc();

        return order;
    }
}
```

### 9.3.3 Distributed Tracing

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

// Initialize OpenTelemetry
const sdk = new NodeSDK({
    resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'myapp',
        [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
        environment: process.env.NODE_ENV
    }),
    traceExporter: new JaegerExporter({
        endpoint: 'http://jaeger:14268/api/traces'
    }),
    instrumentations: [
        getNodeAutoInstrumentations({
            '@opentelemetry/instrumentation-http': {
                enabled: true
            },
            '@opentelemetry/instrumentation-express': {
                enabled: true
            },
            '@opentelemetry/instrumentation-pg': {
                enabled: true
            }
        })
    ]
});

sdk.start();

// Custom spans
import { trace, SpanStatusCode } from '@opentelemetry/api';

class UserService {
    async createUser(userData: CreateUserDTO) {
        const tracer = trace.getTracer('user-service');

        return tracer.startActiveSpan('createUser', async (span) => {
            span.setAttribute('user.email', userData.email);

            try {
                // Validate user
                await tracer.startActiveSpan('validateUser', async (validateSpan) => {
                    await this.validateUser(userData);
                    validateSpan.setStatus({ code: SpanStatusCode.OK });
                    validateSpan.end();
                });

                // Create in database
                const user = await tracer.startActiveSpan('saveUser', async (saveSpan) => {
                    const result = await db.users.create(userData);
                    saveSpan.setAttribute('user.id', result.id);
                    saveSpan.setStatus({ code: SpanStatusCode.OK });
                    saveSpan.end();
                    return result;
                });

                // Send email
                await tracer.startActiveSpan('sendWelcomeEmail', async (emailSpan) => {
                    await emailService.sendWelcome(user.email);
                    emailSpan.setStatus({ code: SpanStatusCode.OK });
                    emailSpan.end();
                });

                span.setStatus({ code: SpanStatusCode.OK });
                span.setAttribute('user.id', user.id);

                return user;
            } catch (error) {
                span.setStatus({
                    code: SpanStatusCode.ERROR,
                    message: (error as Error).message
                });
                span.recordException(error as Error);
                throw error;
            } finally {
                span.end();
            }
        });
    }
}
```

### 9.3.4 Health Checks

```typescript
interface HealthCheck {
    name: string;
    check: () => Promise<boolean>;
    critical: boolean;
}

class HealthCheckService {
    private checks: HealthCheck[] = [
        {
            name: 'database',
            critical: true,
            check: async () => {
                try {
                    await db.query('SELECT 1');
                    return true;
                } catch {
                    return false;
                }
            }
        },
        {
            name: 'redis',
            critical: true,
            check: async () => {
                try {
                    await redis.ping();
                    return true;
                } catch {
                    return false;
                }
            }
        },
        {
            name: 'external-api',
            critical: false,
            check: async () => {
                try {
                    const response = await fetch('https://api.example.com/health');
                    return response.ok;
                } catch {
                    return false;
                }
            }
        }
    ];

    async getHealth(): Promise<{
        status: 'healthy' | 'degraded' | 'unhealthy';
        checks: Record<string, boolean>;
    }> {
        const results = await Promise.all(
            this.checks.map(async (check) => ({
                name: check.name,
                critical: check.critical,
                healthy: await check.check()
            }))
        );

        const checks: Record<string, boolean> = {};
        let criticalFailure = false;
        let degraded = false;

        for (const result of results) {
            checks[result.name] = result.healthy;

            if (!result.healthy) {
                if (result.critical) {
                    criticalFailure = true;
                } else {
                    degraded = true;
                }
            }
        }

        let status: 'healthy' | 'degraded' | 'unhealthy';
        if (criticalFailure) {
            status = 'unhealthy';
        } else if (degraded) {
            status = 'degraded';
        } else {
            status = 'healthy';
        }

        return { status, checks };
    }
}

// Endpoints
const healthCheck = new HealthCheckService();

// Liveness probe (is application running?)
app.get('/health/live', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

// Readiness probe (is application ready to serve traffic?)
app.get('/health/ready', async (req, res) => {
    const health = await healthCheck.getHealth();

    if (health.status === 'unhealthy') {
        return res.status(503).json(health);
    }

    res.status(200).json(health);
});
```

## 9.4 Incident Response

### 9.4.1 Runbooks

```markdown
# Incident Response Runbook

## High CPU Usage

### Symptoms
- CPU usage > 80% for more than 5 minutes
- Slow response times
- Increased error rates

### Investigation
1. Check metrics dashboard
2. Identify which process is using CPU
3. Check for infinite loops or inefficient queries
4. Review recent deployments

### Remediation
1. If caused by recent deployment: Roll back
2. If caused by traffic spike: Scale horizontally
3. If caused by specific query: Add database index or optimize query
4. If memory leak: Restart service (temporary), fix leak (permanent)

### Prevention
- Set up CPU usage alerts
- Implement auto-scaling
- Regular performance testing
- Code reviews for performance

## Database Connection Pool Exhausted

### Symptoms
- "Too many connections" errors
- Long database query times
- Application timeouts

### Investigation
1. Check active database connections
2. Identify long-running queries
3. Check for connection leaks
4. Review connection pool configuration

### Remediation
1. Kill long-running queries
2. Increase pool size (temporary)
3. Fix connection leaks in code
4. Implement connection timeout

### Prevention
- Monitor connection pool metrics
- Set connection timeouts
- Use connection pooling correctly
- Regular code audits

## Service Degradation

### Symptoms
- Increased latency (p95 > 1s)
- Partial failures
- Some features unavailable

### Investigation
1. Check all health checks
2. Review metrics for all services
3. Check external dependencies
4. Review logs for errors

### Remediation
1. Enable circuit breakers
2. Failover to backup services
3. Implement graceful degradation
4. Communicate with users

## Escalation

### Level 1: On-Call Engineer
- Acknowledge incident
- Follow runbook
- Keep incident channel updated

### Level 2: Team Lead
- If incident not resolved in 30 minutes
- Multiple services affected
- Data loss risk

### Level 3: Engineering Manager
- If incident not resolved in 2 hours
- Customer-facing impact
- Security incident
```

### 9.4.2 Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

**Date**: 2025-01-15
**Duration**: 2 hours 15 minutes
**Impact**: 15% of users unable to checkout
**Severity**: SEV-2

## Summary
Brief description of what happened.

## Timeline (all times UTC)
- **14:30**: Deployment of v2.3.5 began
- **14:35**: Deployment completed
- **14:40**: Error rate increased to 15%
- **14:42**: PagerDuty alert triggered
- **14:45**: On-call engineer acknowledged
- **14:50**: Root cause identified (database migration incomplete)
- **15:00**: Rollback initiated
- **15:10**: Rollback completed
- **15:15**: Error rate returned to normal
- **16:45**: Incident marked as resolved

## Root Cause
Detailed explanation of what caused the incident.

The database migration in v2.3.5 added a new column but didn't set a default value. The application code assumed the column existed and would never be null, causing errors for existing records.

## Impact
- **Users affected**: ~15% (approximately 1,500 users)
- **Duration**: 2 hours 15 minutes
- **Revenue impact**: Estimated $5,000 in lost sales
- **Data loss**: None

## What Went Well
- Alert triggered within 5 minutes of incident start
- On-call engineer responded quickly
- Rollback process was smooth
- Communication was clear

## What Went Wrong
- Migration wasn't tested with production-like data
- No automated rollback on deployment failure
- Monitoring didn't catch the issue during canary deployment

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add default value to migration | @alice | 2025-01-16 | Done |
| Improve migration testing process | @bob | 2025-01-22 | In Progress |
| Implement automated rollback | @charlie | 2025-02-01 | Not Started |
| Add monitoring for database errors | @dave | 2025-01-20 | Done |

## Lessons Learned
1. Always test migrations with production-like data
2. Canary deployments should include database migration checks
3. Need better monitoring of database-related errors
```


---

# PART 10: ENGINEERING JUDGMENT

## 10.1 Trade-off Analysis

### 10.1.1 Decision Framework

Every technical decision involves trade-offs. Use this framework:

1. **Identify constraints**: Time, budget, team size, skill level
2. **Define requirements**: Must-have vs nice-to-have
3. **List options**: At least 3 alternatives
4. **Evaluate trade-offs**: For each option
5. **Make decision**: Document reasoning
6. **Review outcome**: Learn from results

**Example: Choosing Database**

```
Option 1: PostgreSQL (Relational)
Pros:
- ACID compliance (strong consistency)
- Complex queries with JOIN
- Mature, well-documented
- Great tooling

Cons:
- Harder to scale horizontally
- Schema changes can be painful
- Limited performance for very large datasets

Option 2: MongoDB (Document)
Pros:
- Flexible schema
- Easy horizontal scaling
- Fast for simple queries
- Good for rapid prototyping

Cons:
- Eventual consistency
- No JOIN support (must do in application)
- Data duplication

Option 3: DynamoDB (Key-Value)
Pros:
- Fully managed (no ops)
- Infinite scalability
- Predictable performance

Cons:
- Expensive for large datasets
- Limited query patterns
- Vendor lock-in

Decision: PostgreSQL
Reasoning:
- Need ACID for financial transactions
- Complex reporting requirements need JOIN
- Team has SQL expertise
- Can scale vertically initially, add read replicas later
```

### 10.1.2 Common Trade-offs

**Performance vs Maintainability**
```typescript
// Highly optimized (fast but hard to maintain)
function fastButObscure(arr: number[]): number {
    return arr.reduce((a,b,i,r)=>i?a+b*r[i-1]:b,0);
}

// Clear and maintainable (slightly slower but readable)
function calculateWeightedSum(values: number[]): number {
    let sum = values[0];

    for (let i = 1; i < values.length; i++) {
        sum += values[i] * values[i - 1];
    }

    return sum;
}

// Choose readability unless profiling shows it's a bottleneck
// "Premature optimization is the root of all evil" - Donald Knuth
```

**Consistency vs Availability (CAP Theorem)**
```typescript
// Strong consistency (may be unavailable during network partition)
async function transferMoney(from: string, to: string, amount: number) {
    await db.transaction(async (trx) => {
        await trx('accounts').where({ id: from }).decrement('balance', amount);
        await trx('accounts').where({ id: to }).increment('balance', amount);
    });
    // Guaranteed consistent but may fail during partition
}

// Eventual consistency (always available)
async function addToCart(userId: string, itemId: string) {
    // Write to local cache immediately
    await cache.sadd(`cart:${userId}`, itemId);

    // Sync to database eventually
    queue.add('syncCart', { userId, itemId });

    // User sees update immediately, data eventually consistent
}
```

**Build vs Buy**
```
Build:
Pros: Full control, perfect fit, no licensing costs, competitive advantage
Cons: Development time, maintenance burden, opportunity cost

Buy:
Pros: Faster time to market, tested/proven, support included, focus on core business
Cons: License costs, limited customization, vendor dependency

Decision Matrix:
- Core business logic → Build
- Commodity features (auth, payments, email) → Buy/Use SaaS
- Specialized domain requirements → Build
- Common problems (logging, monitoring) → Buy/Open Source
```

## 10.2 Technical Debt Management

### 10.2.1 Types of Technical Debt

**Deliberate Debt**: Conscious decision to ship faster
```typescript
// TODO: This is a simplified version. Need to:
// - Add validation for edge cases
// - Implement retry logic
// - Add comprehensive logging
// Decision: Ship MVP now, improve later
// Ticket: TECH-123
function processPayment(payment: Payment) {
    return stripe.charge(payment.amount);
}
```

**Accidental Debt**: Lack of knowledge/awareness
```typescript
// Discovered later: This doesn't handle timezone correctly
// Should use proper timezone library
function formatDate(date: Date): string {
    return `${date.getMonth()}/${date.getDate()}/${date.getFullYear()}`;
}
```

**Incremental Debt**: Accumulation over time
```typescript
// Started simple, grew without refactoring
function handleUserAction(action: string, data: any) {
    if (action === 'create') { /* ... 50 lines ... */ }
    else if (action === 'update') { /* ... 80 lines ... */ }
    else if (action === 'delete') { /* ... 30 lines ... */ }
    // ... 15 more actions
    // Total: 500+ line function!
}

// Should refactor to:
class UserActionHandler {
    private handlers = {
        create: new CreateUserHandler(),
        update: new UpdateUserHandler(),
        delete: new DeleteUserHandler()
    };

    handle(action: string, data: any) {
        const handler = this.handlers[action];
        if (!handler) throw new Error(`Unknown action: ${action}`);
        return handler.execute(data);
    }
}
```

### 10.2.2 Managing Technical Debt

**Track It**:
```markdown
# Technical Debt Register

## High Priority
1. **Database N+1 queries in UserController**
   - Impact: 30% slower page loads
   - Effort: 2 days
   - Ticket: TECH-456

2. **No error handling in payment flow**
   - Impact: Users see generic errors
   - Effort: 3 days
   - Ticket: TECH-789

## Medium Priority
3. **Inconsistent error responses**
   - Impact: Frontend has to handle multiple formats
   - Effort: 1 week
   - Ticket: TECH-101

## Low Priority
4. **Old dependency versions**
   - Impact: Missing security patches
   - Effort: 1 day
   - Ticket: TECH-202
```

**Allocate Time**:
```
Sprint Planning:
- 70% new features
- 20% technical debt
- 10% bugs/support

Never go below 15% for tech debt - it compounds!
```

**Boy Scout Rule**: "Leave code better than you found it"
```typescript
// While fixing bug, also refactor
async function getUserOrders(userId: string) {
    // Original code (with bug):
    // const orders = await db.orders.find({ user_id: userId });
    // return orders.map(o => ({ ...o, total: o.items.reduce((s, i) => s + i.price) }));

    // Fixed bug AND improved code:
    const orders = await db.orders.find({ userId }); // Fixed: use correct field name

    return orders.map(order => ({
        ...order,
        total: this.calculateOrderTotal(order) // Extracted to method
    }));
}

private calculateOrderTotal(order: Order): number {
    return order.items.reduce((sum, item) => sum + item.price, 0);
}
```

## 10.3 When to Optimize

### 10.3.1 Optimization Guidelines

**Don't optimize without profiling**:
```typescript
// WRONG: Optimizing without measuring
function processData(items: Item[]) {
    // Spent 2 days optimizing this loop
    const cache = new Map();
    for (const item of items) {
        // Complex caching logic...
    }

    // Profiling shows this is the actual bottleneck (90% of time):
    await db.batchInsert(items);
}

// RIGHT: Profile first
import { performance } from 'perf_hooks';

function measurePerformance() {
    const start = performance.now();
    const result = processData(items);
    const duration = performance.now() - start;

    console.log(`processData took ${duration}ms`);
    // Discovered: Loop is 10ms, database is 900ms
    // Optimize database, not loop!
}
```

**Optimize when**:
1. Users complaining about slowness
2. Metrics show degradation (p95 > SLA)
3. Resource costs too high
4. Blocking scale/growth

**Don't optimize when**:
1. Code is fast enough
2. Optimization makes code much more complex
3. Premature (no users yet)
4. Other work has higher ROI

### 10.3.2 Performance Budget

```typescript
// Define performance budgets
const PERFORMANCE_BUDGET = {
    // Page load times
    'homePage': 1000,      // 1 second
    'searchResults': 2000,  // 2 seconds
    'checkout': 1500,       // 1.5 seconds

    // API response times (p95)
    'api.getUser': 100,         // 100ms
    'api.search': 500,          // 500ms
    'api.createOrder': 1000,    // 1 second

    // Bundle sizes
    'js.main': 200 * 1024,      // 200KB
    'js.vendor': 500 * 1024,    // 500KB
    'css.main': 50 * 1024       // 50KB
};

// Monitor and alert on budget violations
class PerformanceBudgetMonitor {
    checkBudget(metric: string, value: number): boolean {
        const budget = PERFORMANCE_BUDGET[metric];

        if (budget && value > budget) {
            this.alert(`Performance budget exceeded: ${metric} = ${value}ms (budget: ${budget}ms)`);
            return false;
        }

        return true;
    }
}
```

---

# PART 11: WEB APPLICATION FUNDAMENTALS

## 11.1 HTTP Protocol Deep Dive

### 11.1.1 Request/Response Cycle

```
Client                                  Server
  |                                        |
  |  GET /users/123 HTTP/1.1              |
  |  Host: api.example.com                |
  |  Accept: application/json             |
  |  Authorization: Bearer token123       |
  |--------------------------------------->|
  |                                        |
  |                                        |  [Process request]
  |                                        |  [Query database]
  |                                        |  [Format response]
  |                                        |
  |  HTTP/1.1 200 OK                      |
  |  Content-Type: application/json       |
  |  Cache-Control: max-age=300           |
  |  ETag: "abc123"                       |
  |  {"id": 123, "name": "John"}          |
  |<---------------------------------------|
  |                                        |
```

### 11.1.2 HTTP Methods

```typescript
// GET: Retrieve resource (idempotent, cacheable)
app.get('/users/:id', async (req, res) => {
    const user = await db.users.findById(req.params.id);
    res.json(user);
});

// POST: Create resource (not idempotent)
app.post('/users', async (req, res) => {
    const user = await db.users.create(req.body);
    res.status(201)
        .location(`/users/${user.id}`)
        .json(user);
});

// PUT: Replace resource (idempotent)
app.put('/users/:id', async (req, res) => {
    const user = await db.users.update(req.params.id, req.body);
    res.json(user);
});

// PATCH: Partial update (not idempotent)
app.patch('/users/:id', async (req, res) => {
    const user = await db.users.patch(req.params.id, req.body);
    res.json(user);
});

// DELETE: Remove resource (idempotent)
app.delete('/users/:id', async (req, res) => {
    await db.users.delete(req.params.id);
    res.status(204).send();
});

// HEAD: Like GET but only headers (check if resource exists)
app.head('/users/:id', async (req, res) => {
    const exists = await db.users.exists(req.params.id);
    res.status(exists ? 200 : 404).send();
});

// OPTIONS: Get allowed methods (CORS preflight)
app.options('/users', (req, res) => {
    res.set('Allow', 'GET, POST, OPTIONS');
    res.status(200).send();
});
```

### 11.1.3 HTTP Status Codes

```typescript
// 2xx Success
200 OK                  // Request successful
201 Created             // Resource created
202 Accepted            // Async processing started
204 No Content          // Success but no response body
206 Partial Content     // Range request

// 3xx Redirection
301 Moved Permanently   // Resource permanently moved
302 Found               // Temporary redirect
304 Not Modified        // Cached version still valid
307 Temporary Redirect  // Preserve method on redirect
308 Permanent Redirect  // Preserve method on redirect

// 4xx Client Errors
400 Bad Request         // Invalid request
401 Unauthorized        // Authentication required
403 Forbidden           // Authenticated but not authorized
404 Not Found           // Resource doesn't exist
405 Method Not Allowed  // HTTP method not supported
409 Conflict            // Request conflicts with current state
422 Unprocessable Entity // Validation failed
429 Too Many Requests   // Rate limit exceeded

// 5xx Server Errors
500 Internal Server Error // Generic server error
502 Bad Gateway           // Invalid upstream response
503 Service Unavailable   // Server overloaded/maintenance
504 Gateway Timeout       // Upstream timeout
```

### 11.1.4 Caching Headers

```typescript
app.get('/users/:id', async (req, res) => {
    const user = await db.users.findById(req.params.id);

    // ETag for conditional requests
    const etag = createHash('md5').update(JSON.stringify(user)).digest('hex');

    if (req.get('If-None-Match') === etag) {
        return res.status(304).send(); // Not modified
    }

    res.set({
        'ETag': etag,
        'Cache-Control': 'private, max-age=300', // Cache for 5 minutes
        'Last-Modified': user.updatedAt.toUTCString()
    });

    res.json(user);
});

// Vary header for different responses based on headers
app.get('/api/data', (req, res) => {
    const acceptLanguage = req.get('Accept-Language');

    res.set({
        'Vary': 'Accept-Language', // Cache separately per language
        'Cache-Control': 'public, max-age=3600'
    });

    res.json(getDataForLanguage(acceptLanguage));
});
```

## 11.2 Browser Rendering Pipeline

```
1. Parse HTML → DOM Tree
2. Parse CSS → CSSOM Tree
3. Combine DOM + CSSOM → Render Tree
4. Layout (calculate positions/sizes)
5. Paint (draw pixels)
6. Composite (combine layers)
```

### 11.2.1 Critical Rendering Path Optimization

```html
<!-- Bad: Blocks rendering -->
<head>
    <link rel="stylesheet" href="styles.css">
    <script src="app.js"></script>
</head>

<!-- Good: Optimized loading -->
<head>
    <!-- Inline critical CSS -->
    <style>
        /* Critical above-the-fold styles */
        .header { /* ... */ }
        .hero { /* ... */ }
    </style>

    <!-- Async load non-critical CSS -->
    <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">

    <!-- Defer JavaScript -->
    <script defer src="app.js"></script>
</head>
```

### 11.2.2 Web Performance Metrics

```typescript
// Core Web Vitals
class PerformanceMetrics {
    // Largest Contentful Paint (LCP) - Loading performance
    // Good: < 2.5s
    measureLCP() {
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];

            console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);

            // Send to analytics
            analytics.track('lcp', {
                value: lastEntry.renderTime || lastEntry.loadTime
            });
        }).observe({ entryTypes: ['largest-contentful-paint'] });
    }

    // First Input Delay (FID) - Interactivity
    // Good: < 100ms
    measureFID() {
        new PerformanceObserver((list) => {
            const entries = list.getEntries();

            entries.forEach((entry) => {
                console.log('FID:', entry.processingStart - entry.startTime);

                analytics.track('fid', {
                    value: entry.processingStart - entry.startTime
                });
            });
        }).observe({ entryTypes: ['first-input'] });
    }

    // Cumulative Layout Shift (CLS) - Visual stability
    // Good: < 0.1
    measureCLS() {
        let clsValue = 0;

        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!(entry as any).hadRecentInput) {
                    clsValue += (entry as any).value;
                }
            }

            console.log('CLS:', clsValue);

            analytics.track('cls', { value: clsValue });
        }).observe({ entryTypes: ['layout-shift'] });
    }
}

// Initialize
const metrics = new PerformanceMetrics();
metrics.measureLCP();
metrics.measureFID();
metrics.measureCLS();
```

## 11.3 State Management

### 11.3.1 Client-Side State

```typescript
// Context API (React)
const UserContext = createContext<User | null>(null);

function App() {
    const [user, setUser] = useState<User | null>(null);

    return (
        <UserContext.Provider value={user}>
            <Dashboard />
        </UserContext.Provider>
    );
}

function Dashboard() {
    const user = useContext(UserContext);
    return <div>Welcome {user?.name}</div>;
}

// Redux (for complex state)
interface AppState {
    user: User | null;
    cart: CartItem[];
    notifications: Notification[];
}

const initialState: AppState = {
    user: null,
    cart: [],
    notifications: []
};

function rootReducer(state = initialState, action: Action): AppState {
    switch (action.type) {
        case 'USER_LOGIN':
            return { ...state, user: action.payload };

        case 'ADD_TO_CART':
            return {
                ...state,
                cart: [...state.cart, action.payload]
            };

        case 'REMOVE_FROM_CART':
            return {
                ...state,
                cart: state.cart.filter(item => item.id !== action.payload)
            };

        default:
            return state;
    }
}

// Zustand (simpler alternative to Redux)
const useStore = create<AppState>((set) => ({
    user: null,
    cart: [],

    login: (user: User) => set({ user }),
    logout: () => set({ user: null }),

    addToCart: (item: CartItem) =>
        set((state) => ({ cart: [...state.cart, item] })),

    removeFromCart: (itemId: string) =>
        set((state) => ({
            cart: state.cart.filter(item => item.id !== itemId)
        }))
}));
```

### 11.3.2 Server State (React Query)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
    const queryClient = useQueryClient();

    // Fetch user
    const { data: user, isLoading, error } = useQuery({
        queryKey: ['user', userId],
        queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
        staleTime: 5 * 60 * 1000, // 5 minutes
        cacheTime: 10 * 60 * 1000, // 10 minutes
    });

    // Update user mutation
    const updateUser = useMutation({
        mutationFn: (data: Partial<User>) =>
            fetch(`/api/users/${userId}`, {
                method: 'PATCH',
                body: JSON.stringify(data)
            }).then(r => r.json()),

        onSuccess: (updatedUser) => {
            // Update cache
            queryClient.setQueryData(['user', userId], updatedUser);

            // Or invalidate to refetch
            // queryClient.invalidateQueries({ queryKey: ['user', userId] });
        }
    });

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div>
            <h1>{user.name}</h1>
            <button onClick={() => updateUser.mutate({ name: 'New Name' })}>
                Update Name
            </button>
        </div>
    );
}
```

---

# PART 12: DATABASE THEORY

## 12.1 ACID Properties

**Atomicity**: All or nothing
```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- If either fails, both are rolled back
COMMIT;
```

**Consistency**: Database remains in valid state
```sql
-- Constraint ensures consistency
ALTER TABLE accounts
ADD CONSTRAINT positive_balance CHECK (balance >= 0);

-- This transaction will fail and rollback
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
-- Error: violates check constraint "positive_balance"
ROLLBACK;
```

**Isolation**: Concurrent transactions don't interfere
```sql
-- Transaction 1
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1; -- 100
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
-- Not committed yet...

-- Transaction 2 (concurrent)
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1; -- Still sees 100!
COMMIT;

-- Transaction 1
COMMIT; -- Now balance is 50
```

**Durability**: Committed data persists
```sql
BEGIN TRANSACTION;
INSERT INTO orders (user_id, total) VALUES (1, 100);
COMMIT;

-- Even if server crashes here, data is safe (write-ahead log)
```

## 12.2 Transaction Isolation Levels

```sql
-- Read Uncommitted (Dirty reads possible)
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Read Committed (No dirty reads)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Repeatable Read (No dirty reads, no non-repeatable reads)
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Serializable (Full isolation, no phantoms)
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

**Anomalies**:

**Dirty Read**: Read uncommitted data
```sql
-- Transaction 1
BEGIN;
UPDATE accounts SET balance = 1000 WHERE id = 1;
-- Not committed

-- Transaction 2 (READ UNCOMMITTED)
SELECT balance FROM accounts WHERE id = 1; -- Sees 1000!

-- Transaction 1
ROLLBACK; -- Oops, Transaction 2 saw data that never existed!
```

**Non-Repeatable Read**: Read changes between reads
```sql
-- Transaction 1
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- 100

-- Transaction 2
UPDATE accounts SET balance = 200 WHERE id = 1;
COMMIT;

-- Transaction 1
SELECT balance FROM accounts WHERE id = 1; -- Now 200!
-- Same query, different result
COMMIT;
```

**Phantom Read**: New rows appear
```sql
-- Transaction 1
BEGIN;
SELECT COUNT(*) FROM orders WHERE user_id = 1; -- 5

-- Transaction 2
INSERT INTO orders (user_id, total) VALUES (1, 100);
COMMIT;

-- Transaction 1
SELECT COUNT(*) FROM orders WHERE user_id = 1; -- Now 6!
-- Phantom row appeared
COMMIT;
```

## 12.3 Indexing Strategies

### 12.3.1 When to Index

```sql
-- Index columns used in WHERE clauses
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';

-- Index columns used in JOIN conditions
CREATE INDEX idx_orders_user_id ON orders(user_id);
SELECT * FROM users u JOIN orders o ON u.id = o.user_id;

-- Index columns used in ORDER BY
CREATE INDEX idx_posts_created_at ON posts(created_at);
SELECT * FROM posts ORDER BY created_at DESC;

-- Composite index for multiple columns
CREATE INDEX idx_users_status_created ON users(status, created_at);
SELECT * FROM users WHERE status = 'active' ORDER BY created_at;
```

### 12.3.2 When NOT to Index

```sql
-- Don't index small tables (< 1000 rows)
-- Full table scan is faster than index lookup

-- Don't index columns with low cardinality
CREATE INDEX idx_users_is_active ON users(is_active);
-- Bad: Only 2 possible values (true/false)

-- Don't index columns that change frequently
CREATE INDEX idx_page_views_count ON pages(view_count);
-- Bad: view_count changes on every page view
-- Index maintenance overhead > benefit

-- Don't create too many indexes
-- Each index slows down INSERT/UPDATE/DELETE
```

## 12.4 Query Optimization

```sql
-- Use EXPLAIN to understand query plan
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id
HAVING COUNT(o.id) > 5;

-- Optimize by adding indexes
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Use covering index to avoid table lookup
CREATE INDEX idx_users_status_name ON users(status, name);

-- Avoid SELECT *
-- Bad:
SELECT * FROM users WHERE email = 'user@example.com';

-- Good:
SELECT id, name, email FROM users WHERE email = 'user@example.com';

-- Use LIMIT for pagination
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- Avoid subqueries when JOIN is possible
-- Bad:
SELECT * FROM users WHERE id IN (
    SELECT user_id FROM orders WHERE total > 100
);

-- Good:
SELECT DISTINCT u.* FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.total > 100;
```

---

# PART 13: CODE QUALITY

## 13.1 Code Smells & Refactoring

### 13.1.1 Long Method

```typescript
// Bad: 200-line method
function processOrder(order: Order) {
    // Validate order
    if (!order.items || order.items.length === 0) {
        throw new Error('No items');
    }
    // ... 50 lines of validation

    // Calculate total
    let total = 0;
    for (const item of order.items) {
        total += item.price * item.quantity;
    }
    // ... 30 lines of calculation

    // Apply discount
    if (order.promoCode) {
        // ... 40 lines of discount logic
    }

    // Process payment
    // ... 50 lines of payment logic

    // Send confirmation
    // ... 30 lines of email logic
}

// Good: Extract methods
class OrderProcessor {
    async process(order: Order): Promise<void> {
        this.validate(order);
        const total = this.calculateTotal(order);
        const finalAmount = this.applyDiscount(total, order.promoCode);
        await this.processPayment(order.customerId, finalAmount);
        await this.sendConfirmation(order);
    }

    private validate(order: Order): void {
        if (!order.items?.length) {
            throw new Error('No items');
        }
        // Focused validation logic
    }

    private calculateTotal(order: Order): number {
        return order.items.reduce(
            (sum, item) => sum + item.price * item.quantity,
            0
        );
    }

    private applyDiscount(total: number, promoCode?: string): number {
        if (!promoCode) return total;
        // Focused discount logic
        return total;
    }

    private async processPayment(customerId: string, amount: number): Promise<void> {
        // Focused payment logic
    }

    private async sendConfirmation(order: Order): Promise<void> {
        // Focused email logic
    }
}
```

### 13.1.2 God Object

```typescript
// Bad: One class does everything
class UserManager {
    createUser() { /* ... */ }
    deleteUser() { /* ... */ }
    updateUser() { /* ... */ }
    sendEmail() { /* ... */ }
    hashPassword() { /* ... */ }
    generateToken() { /* ... */ }
    validateInput() { /* ... */ }
    logActivity() { /* ... */ }
    // ... 50 more methods
}

// Good: Single Responsibility Principle
class UserRepository {
    create(user: User): Promise<User> { /* ... */ }
    update(id: string, data: Partial<User>): Promise<User> { /* ... */ }
    delete(id: string): Promise<void> { /* ... */ }
}

class PasswordService {
    hash(password: string): Promise<string> { /* ... */ }
    verify(password: string, hash: string): Promise<boolean> { /* ... */ }
}

class EmailService {
    send(to: string, subject: string, body: string): Promise<void> { /* ... */ }
}

class TokenService {
    generate(payload: any): string { /* ... */ }
    verify(token: string): any { /* ... */ }
}

class UserValidator {
    validate(data: CreateUserDTO): ValidationResult { /* ... */ }
}

class ActivityLogger {
    log(action: string, userId: string): void { /* ... */ }
}
```

### 13.1.3 Duplicate Code

```typescript
// Bad: Duplicated validation
function createUser(data: any) {
    if (!data.email || !data.email.includes('@')) {
        throw new Error('Invalid email');
    }
    if (!data.password || data.password.length < 8) {
        throw new Error('Password too short');
    }
    // ...
}

function updateUser(id: string, data: any) {
    if (!data.email || !data.email.includes('@')) {
        throw new Error('Invalid email');
    }
    if (!data.password || data.password.length < 8) {
        throw new Error('Password too short');
    }
    // ...
}

// Good: Extract common logic
class UserValidator {
    validateEmail(email: string): void {
        if (!email || !email.includes('@')) {
            throw new Error('Invalid email');
        }
    }

    validatePassword(password: string): void {
        if (!password || password.length < 8) {
            throw new Error('Password too short');
        }
    }
}

function createUser(data: any, validator: UserValidator) {
    validator.validateEmail(data.email);
    validator.validatePassword(data.password);
    // ...
}

function updateUser(id: string, data: any, validator: UserValidator) {
    validator.validateEmail(data.email);
    if (data.password) {
        validator.validatePassword(data.password);
    }
    // ...
}
```

## 13.2 Clean Code Principles

### 13.2.1 Meaningful Names

```typescript
// Bad
const d = new Date();
const x = getUserById(123);
function calc(a, b) { return a * b * 0.8; }

// Good
const currentDate = new Date();
const user = getUserById(123);
function calculateDiscountedPrice(price: number, quantity: number): number {
    const DISCOUNT_RATE = 0.8;
    return price * quantity * DISCOUNT_RATE;
}
```

### 13.2.2 Functions Should Do One Thing

```typescript
// Bad
function handleSubmit(formData: any) {
    // Validation
    if (!formData.email) return;

    // Transform data
    const user = {
        email: formData.email.toLowerCase(),
        name: formData.name.trim()
    };

    // Save to database
    db.users.create(user);

    // Send email
    sendWelcomeEmail(user.email);

    // Redirect
    window.location.href = '/dashboard';
}

// Good
async function handleSubmit(formData: FormData): Promise<void> {
    const userData = validateAndTransform(formData);
    const user = await createUser(userData);
    await sendWelcomeEmail(user);
    redirectToDashboard();
}

function validateAndTransform(formData: FormData): UserData {
    if (!formData.email) {
        throw new ValidationError('Email required');
    }

    return {
        email: formData.email.toLowerCase(),
        name: formData.name.trim()
    };
}

async function createUser(userData: UserData): Promise<User> {
    return db.users.create(userData);
}

async function sendWelcomeEmail(user: User): Promise<void> {
    await emailService.send(user.email, 'Welcome!', 'Thanks for joining');
}

function redirectToDashboard(): void {
    window.location.href = '/dashboard';
}
```

### 13.2.3 Comments

```typescript
// Bad: Comments that explain what (code should be self-explanatory)
// Check if user is admin
if (user.role === 'admin') {
    // Do admin stuff
}

// Good: Self-documenting code
if (user.isAdmin()) {
    this.performAdminAction();
}

// Good: Comments that explain why
// Use exponential backoff to avoid overwhelming the API
// during temporary outages (see incident INC-123)
for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    await sleep(Math.pow(2, attempt) * 1000);
    try {
        return await apiCall();
    } catch (error) {
        if (attempt === MAX_RETRIES - 1) throw error;
    }
}

// Good: Comments for complex algorithms
/**
 * Implements the Knuth-Morris-Pratt string matching algorithm.
 * Time complexity: O(n + m) where n = text length, m = pattern length
 * Space complexity: O(m) for the prefix table
 *
 * @see https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm
 */
function kmpSearch(text: string, pattern: string): number {
    // Build prefix table
    const prefixTable = buildPrefixTable(pattern);
    // ... algorithm implementation
}
```

---

# PART 14: MENTAL MODELS FOR ENGINEERS

## 14.1 First Principles Thinking

Break down complex problems to fundamental truths and rebuild from there.

**Example: Building Authentication**

Instead of: "I need authentication, I'll use Firebase Auth"

First Principles:
1. What is authentication? Verifying user identity
2. What do I need? Store user credentials securely
3. How do I verify? Compare provided credentials with stored ones
4. What are the security requirements? Passwords must be hashed, sessions must expire
5. What are the constraints? Budget, team size, time
6. Now decide: Build (JWT + bcrypt) or buy (Auth0)?

## 14.2 Systems Thinking

See how components interact within larger system.

```
User Request
    ↓
Load Balancer
    ↓
Web Server (bottleneck identified)
    ↓
Application Server
    ↓
Database

Optimizing database won't help if web server is the bottleneck!
```

## 14.3 Abstraction Layers

```
High Level: User Interface
    ↓
Business Logic
    ↓
Data Access
    ↓
Low Level: Database
```

Each layer hides complexity from layer above.

## 14.4 Separation of Concerns

```typescript
// Bad: Mixed concerns
function displayUserProfile(userId: string) {
    // Data fetching (I/O)
    const user = fetch(`/api/users/${userId}`);

    // Business logic
    const displayName = user.firstName + ' ' + user.lastName;
    const memberSince = calculateYearsSince(user.createdAt);

    // Presentation
    document.getElementById('name').textContent = displayName;
    document.getElementById('member').textContent = `Member for ${memberSince} years`;
}

// Good: Separated concerns
// Data Layer
async function fetchUser(userId: string): Promise<User> {
    return fetch(`/api/users/${userId}`).then(r => r.json());
}

// Business Logic Layer
function formatUser(user: User): UserViewModel {
    return {
        displayName: `${user.firstName} ${user.lastName}`,
        memberSince: `Member for ${calculateYearsSince(user.createdAt)} years`
    };
}

// Presentation Layer
function renderUserProfile(viewModel: UserViewModel): void {
    document.getElementById('name')!.textContent = viewModel.displayName;
    document.getElementById('member')!.textContent = viewModel.memberSince;
}

// Orchestration
async function displayUserProfile(userId: string): Promise<void> {
    const user = await fetchUser(userId);
    const viewModel = formatUser(user);
    renderUserProfile(viewModel);
}
```

---

# PART 15: REAL-WORLD APPLICATION

## 15.1 Case Study: Scaling Instagram

**Problem**: 1 billion+ users, billions of photos

**Solutions Applied**:

1. **Database Sharding**: User data sharded by user ID
2. **CDN**: Images served from edge locations
3. **Caching**: Redis for feed data
4. **Asynchronous Processing**: Feed updates via message queue
5. **Read Replicas**: Separate reads from writes
6. **Denormalization**: Store follower count rather than counting

**Architecture**:
```
User Upload
    ↓
Load Balancer
    ↓
API Servers (stateless, auto-scaled)
    ↓
Message Queue (for async processing)
    ↓
Workers (resize images, update feeds)
    ↓
Database (sharded by user ID)
    ↓
S3 (image storage)
    ↓
CDN (CloudFront)
```

## 15.2 Common Anti-Patterns

### 15.2.1 Golden Hammer

"If all you have is a hammer, everything looks like a nail"

```typescript
// Using same pattern everywhere regardless of fit

// Good for: Small, related data
const user = {
    name: "John",
    email: "john@example.com"
};

// Bad: Using for everything
const config = {
    database: {
        host: {
            primary: {
                url: "..."
            }
        }
    }
};
// Should use: Environment variables, config management system

// Bad: Using OOP everywhere
class AddService {
    add(a: number, b: number): number {
        return a + b;
    }
}
// Should use: Simple function
```

### 15.2.2 Premature Optimization

```typescript
// Bad: Optimizing before measuring
class UserService {
    private cache = new LRUCache(1000);
    private pool = new ObjectPool(100);

    async getUser(id: string) {
        // Complex caching logic
        // Object pooling
        // ...100 lines of optimization
        // No one has complained about performance!
    }
}

// Good: Start simple
class UserService {
    async getUser(id: string) {
        return db.users.findById(id);
    }
}
// Add caching WHEN needed (based on metrics)
```

### 15.2.3 Not Invented Here (NIH)

```typescript
// Bad: Reinventing the wheel
class MyAwesomeHTTPClient {
    // 500 lines of HTTP implementation
    // Missing edge cases
    // No tests
}

// Good: Use battle-tested libraries
import axios from 'axios';

const client = axios.create({
    timeout: 5000,
    retry: 3
});
```

## 15.3 Decision-Making Checklist

Before making technical decision:

- [ ] Have I identified the actual problem?
- [ ] Have I considered at least 3 alternatives?
- [ ] Do I understand the trade-offs?
- [ ] Have I consulted with the team?
- [ ] Is this decision reversible?
- [ ] Have I documented the reasoning?
- [ ] What metrics will I use to evaluate success?
- [ ] What's the worst that could happen?
- [ ] Is this optimizing for the right thing?
- [ ] Am I choosing based on familiarity or actual fit?

## 15.4 Continuous Learning Path

1. **Read Code**: Study open-source projects
   - React, Vue, Express source code
   - Learn patterns from experts

2. **Build Projects**: Apply concepts
   - Clone popular apps
   - Build with different tech stacks
   - Experiment with new patterns

3. **Write**: Explain concepts to others
   - Blog posts
   - Documentation
   - Teaching reinforces learning

4. **Practice**: Deliberate practice
   - LeetCode/HackerRank for algorithms
   - System design practice
   - Code reviews

5. **Stay Current**: Follow industry
   - Tech blogs (Hacker News, Dev.to)
   - Conferences (videos online)
   - Research papers
   - Books

## 15.5 Final Wisdom

**Embrace Failure**: Every bug is a learning opportunity

**Question Everything**: "Why" is more important than "how"

**Simplicity Wins**: The best code is no code at all

**Measure, Don't Guess**: Data beats opinions

**Collaborate**: Best solutions come from diverse perspectives

**Think Long-Term**: Code is read 10x more than it's written

**Balance Pragmatism with Perfectionism**: Ship > Perfect

**Keep Learning**: Technology changes, principles endure

---

# CONCLUSION

You've now been exposed to the breadth and depth of software engineering knowledge that separates code monkeys from scientist-level engineers. The journey from junior to senior to staff engineer is not about memorizing these concepts, but about:

1. **Understanding WHY** - Not just how to implement patterns, but why they exist
2. **Making Trade-offs** - Knowing when to apply principles and when to break them
3. **System Thinking** - Seeing the bigger picture beyond individual components
4. **Continuous Learning** - Technology evolves, but fundamentals remain
5. **Mentoring Others** - Teaching solidifies your own understanding

Remember: **The best engineers are not those who know the most, but those who make the best decisions with incomplete information.**

Keep building, keep learning, keep questioning. The field of software engineering is vast and ever-evolving. This document is a map, not the territory itself. Use it as a guide, but forge your own path through experience, experimentation, and critical thinking.

**Now go build something amazing.**

---

## References & Further Reading

### Books
- **Clean Code** by Robert Martin
- **Code Complete** by Steve McConnell
- **Designing Data-Intensive Applications** by Martin Kleppmann
- **The Pragmatic Programmer** by Hunt & Thomas
- **Domain-Driven Design** by Eric Evans
- **Release It!** by Michael Nygard
- **Site Reliability Engineering** by Google
- **Why Programs Fail** by Andreas Zeller

### Papers
- CAP Theorem (Brewer, 2000)
- Dynamo: Amazon's Highly Available Key-value Store
- MapReduce: Simplified Data Processing
- Raft Consensus Algorithm

### Online Resources
- Martin Fowler's Blog (martinfowler.com)
- High Scalability (highscalability.com)
- System Design Primer (GitHub)
- Web.dev (Performance & Best Practices)

### Practice Platforms
- LeetCode (Algorithms)
- System Design Interview
- Exercism (Language mastery)
- Frontend Mentor (UI implementation)


---

# PART 16: ADVANCED MATHEMATICS FOR SOFTWARE ENGINEERS

Mathematics is the language of computation. While you can be a functional programmer without deep mathematical knowledge, achieving scientist-level engineering requires understanding the mathematical foundations that underpin algorithms, machine learning, cryptography, graphics, and system optimization.

## 16.1 Linear Algebra

Linear algebra is foundational for graphics, machine learning, data science, computer vision, and quantum computing. Understanding vectors, matrices, and transformations is essential for modern software engineering.

### 16.1.1 Vectors and Vector Spaces

**Theory:**

A vector is an ordered collection of numbers representing magnitude and direction in n-dimensional space.

```
v = [v₁, v₂, ..., vₙ]
```

Vector operations:
- **Addition**: u + v = [u₁+v₁, u₂+v₂, ..., uₙ+vₙ]
- **Scalar multiplication**: cv = [cv₁, cv₂, ..., cvₙ]
- **Dot product**: u·v = u₁v₁ + u₂v₂ + ... + uₙvₙ
- **Magnitude/Norm**: ||v|| = √(v₁² + v₂² + ... + vₙ²)

**WHY it matters:**

1. **Word Embeddings**: In NLP, words are represented as vectors in high-dimensional space where semantic similarity correlates with geometric proximity
2. **Feature Vectors**: Machine learning models consume data as vectors
3. **3D Graphics**: Positions, velocities, normals are all vectors
4. **Recommendation Systems**: Items and users represented as vectors for collaborative filtering

**Example - Cosine Similarity for Recommendation:**

```python
import numpy as np

def cosine_similarity(vec_a, vec_b):
    """
    Measures similarity between two vectors.
    Used in recommendation systems, document similarity, etc.
    
    Returns value between -1 (opposite) and 1 (identical)
    0 means orthogonal (no correlation)
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    return dot_product / (norm_a * norm_b)

# User preferences as vectors
user_a = np.array([5, 3, 0, 1])  # ratings for 4 movies
user_b = np.array([4, 0, 0, 1])
user_c = np.array([1, 1, 5, 5])

print(f"A-B similarity: {cosine_similarity(user_a, user_b):.3f}")  # High
print(f"A-C similarity: {cosine_similarity(user_a, user_c):.3f}")  # Low
```

### 16.1.2 Matrices and Matrix Operations

**Theory:**

A matrix is a 2D array of numbers with m rows and n columns (m×n matrix).

```
A = [a₁₁  a₁₂  a₁₃]
    [a₂₁  a₂₂  a₂₃]
```

Key operations:
- **Matrix multiplication**: (AB)ᵢⱼ = Σₖ aᵢₖbₖⱼ
- **Transpose**: Aᵀ flips rows and columns
- **Inverse**: A⁻¹ such that AA⁻¹ = I (identity matrix)
- **Determinant**: det(A) - scalar value encoding matrix properties

**WHY it matters:**

1. **Computer Graphics**: Every transformation (rotation, scaling, translation) is a matrix operation
2. **Neural Networks**: Layers are matrix multiplications followed by activation functions
3. **Systems of Equations**: Solving Ax = b for thousands of variables
4. **Image Processing**: Images are matrices; convolutions are matrix operations
5. **Graph Algorithms**: Adjacency matrices represent networks

**Example - 3D Rotation Matrix:**

```python
import numpy as np
import math

def rotation_matrix_z(theta):
    """
    Creates a 3D rotation matrix around the z-axis.
    Used in graphics, robotics, game engines.
    
    theta: rotation angle in radians
    """
    return np.array([
        [math.cos(theta), -math.sin(theta), 0],
        [math.sin(theta),  math.cos(theta), 0],
        [0,                0,               1]
    ])

# Rotate a point 90 degrees
point = np.array([1, 0, 0])
rotation = rotation_matrix_z(math.pi / 2)
rotated_point = rotation @ point  # @ is matrix multiplication

print(f"Original: {point}")
print(f"Rotated: {rotated_point}")  # Should be ~[0, 1, 0]

# Chaining transformations
rotation_180 = rotation @ rotation  # Rotate twice
```

**Example - Neural Network Forward Pass:**

```python
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class NeuralLayer:
    """
    Single neural network layer.
    Demonstrates matrix multiplication as core operation.
    """
    def __init__(self, input_size, output_size):
        # Weight matrix: each column is weights for one output neuron
        self.weights = np.random.randn(input_size, output_size) * 0.01
        self.bias = np.zeros((1, output_size))
    
    def forward(self, X):
        """
        X: (batch_size, input_size)
        Returns: (batch_size, output_size)
        
        This single line is the core of deep learning!
        """
        return sigmoid(X @ self.weights + self.bias)

# Example: 3 features -> 5 neurons -> 2 outputs
layer1 = NeuralLayer(3, 5)
layer2 = NeuralLayer(5, 2)

# Batch of 10 samples
X = np.random.randn(10, 3)

# Forward pass through network
hidden = layer1.forward(X)  # (10, 5)
output = layer2.forward(hidden)  # (10, 2)

print(f"Input shape: {X.shape}")
print(f"Hidden shape: {hidden.shape}")
print(f"Output shape: {output.shape}")
```

### 16.1.3 Eigenvalues and Eigenvectors

**Theory:**

For a matrix A, eigenvectors are vectors v that only scale (don't change direction) when multiplied by A:

```
Av = λv
```

Where:
- v is the eigenvector (direction)
- λ is the eigenvalue (scaling factor)

**WHY it matters:**

1. **Principal Component Analysis (PCA)**: Eigenvectors of covariance matrix reveal principal components for dimensionality reduction
2. **Google PageRank**: Dominant eigenvector of web link matrix
3. **Stability Analysis**: Eigenvalues determine system stability in control theory
4. **Quantum Mechanics**: Observable quantities are eigenvalues of operators
5. **Markov Chains**: Steady-state probabilities from eigenvectors

**Example - PCA for Dimensionality Reduction:**

```python
import numpy as np

def pca(X, n_components):
    """
    Principal Component Analysis using eigendecomposition.
    Reduces dimensionality while preserving variance.
    
    X: (n_samples, n_features)
    Returns: (n_samples, n_components)
    """
    # Center the data
    X_centered = X - np.mean(X, axis=0)
    
    # Compute covariance matrix
    # Cov(X) = (1/n)XᵀX
    cov_matrix = np.cov(X_centered.T)
    
    # Find eigenvectors and eigenvalues
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # Sort by eigenvalue (descending)
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Select top n_components
    principal_components = eigenvectors[:, :n_components]
    
    # Project data onto principal components
    X_reduced = X_centered @ principal_components
    
    # Variance explained
    variance_explained = eigenvalues[:n_components] / eigenvalues.sum()
    
    return X_reduced, variance_explained

# Example: 1000 samples with 50 features -> reduce to 2D
np.random.seed(42)
X = np.random.randn(1000, 50)

X_2d, var_exp = pca(X, n_components=2)

print(f"Original shape: {X.shape}")
print(f"Reduced shape: {X_2d.shape}")
print(f"Variance explained: {var_exp.sum():.2%}")
```

### 16.1.4 Matrix Decompositions

**Theory:**

Key decompositions:

1. **LU Decomposition**: A = LU (lower × upper triangular)
2. **QR Decomposition**: A = QR (orthogonal × upper triangular)
3. **SVD (Singular Value Decomposition)**: A = UΣVᵀ
4. **Eigendecomposition**: A = QΛQ⁻¹

**WHY it matters:**

1. **Solving Linear Systems**: LU decomposition for Ax = b
2. **Least Squares**: QR decomposition for overdetermined systems
3. **Recommender Systems**: SVD for collaborative filtering (Netflix Prize)
4. **Image Compression**: SVD keeps only top k singular values
5. **Numerical Stability**: Certain decompositions are more numerically stable

**Example - Image Compression with SVD:**

```python
import numpy as np
from PIL import Image

def compress_image_svd(image_path, k):
    """
    Compress image using SVD by keeping only k largest singular values.
    
    Demonstrates:
    - SVD for dimensionality reduction
    - Trade-off between compression and quality
    - Matrix approximation
    """
    # Load image as grayscale
    img = Image.open(image_path).convert('L')
    img_array = np.array(img, dtype=float)
    
    # Perform SVD: A = UΣVᵀ
    U, S, Vt = np.linalg.svd(img_array, full_matrices=False)
    
    # Keep only top k singular values
    # This is a rank-k approximation of the original matrix
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    Vt_k = Vt[:k, :]
    
    # Reconstruct compressed image
    compressed = U_k @ S_k @ Vt_k
    
    # Calculate compression ratio
    original_size = img_array.size
    compressed_size = U_k.size + k + Vt_k.size
    compression_ratio = original_size / compressed_size
    
    # Calculate error (Frobenius norm)
    error = np.linalg.norm(img_array - compressed, 'fro')
    relative_error = error / np.linalg.norm(img_array, 'fro')
    
    return compressed, compression_ratio, relative_error, S

# Example usage
# img_compressed, ratio, error, singular_values = compress_image_svd('photo.jpg', k=50)
# print(f"Compression ratio: {ratio:.2f}x")
# print(f"Relative error: {error:.2%}")

# Analyzing singular values shows how much information each component captures
def analyze_svd_spectrum(S):
    """
    Plot how much variance is captured by top k singular values.
    Helps determine optimal k for compression.
    """
    cumulative_energy = np.cumsum(S**2) / np.sum(S**2)
    
    for k in [10, 50, 100]:
        print(f"Top {k} components capture {cumulative_energy[k-1]:.2%} of energy")
```

### 16.1.5 Practical Applications

**Computer Graphics Pipeline:**

```python
import numpy as np

class Transform3D:
    """
    3D transformation pipeline used in game engines and graphics.
    Every transformation is a 4x4 matrix (homogeneous coordinates).
    """
    
    @staticmethod
    def translate(tx, ty, tz):
        """Translation matrix"""
        return np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def scale(sx, sy, sz):
        """Scaling matrix"""
        return np.array([
            [sx, 0,  0,  0],
            [0,  sy, 0,  0],
            [0,  0,  sz, 0],
            [0,  0,  0,  1]
        ])
    
    @staticmethod
    def rotate_y(theta):
        """Rotation around Y-axis"""
        c, s = np.cos(theta), np.sin(theta)
        return np.array([
            [c,  0, s, 0],
            [0,  1, 0, 0],
            [-s, 0, c, 0],
            [0,  0, 0, 1]
        ])
    
    @staticmethod
    def perspective(fov, aspect, near, far):
        """
        Perspective projection matrix.
        Converts 3D coordinates to 2D screen coordinates.
        """
        f = 1 / np.tan(fov / 2)
        return np.array([
            [f/aspect, 0, 0,                           0],
            [0,        f, 0,                           0],
            [0,        0, (far+near)/(near-far),       2*far*near/(near-far)],
            [0,        0, -1,                          0]
        ])

# Model-View-Projection pipeline (MVP)
# This is the core of 3D rendering!

# Model: position object in world space
model = Transform3D.translate(0, 0, -5) @ Transform3D.rotate_y(np.pi/4)

# View: position camera
view = Transform3D.translate(0, -1, 0)  # Camera at y=1

# Projection: create perspective
projection = Transform3D.perspective(
    fov=np.pi/3,     # 60 degrees
    aspect=16/9,
    near=0.1,
    far=100
)

# Combined transformation (order matters!)
mvp = projection @ view @ model

# Apply to vertex in homogeneous coordinates [x, y, z, 1]
vertex = np.array([1, 1, 1, 1])
screen_pos = mvp @ vertex

# Perspective divide
screen_pos = screen_pos[:3] / screen_pos[3]
print(f"3D vertex {vertex[:3]} -> Screen position {screen_pos}")
```

**Connections to Other Topics:**

- **Part 18 (ML)**: Neural networks are sequences of matrix multiplications
- **Part 22.1 (Graphics)**: Rendering pipeline is linear algebra
- **Part 11 (Performance)**: Matrix operations optimized via cache locality, SIMD
- **Part 9 (Security)**: Cryptography uses modular arithmetic on matrices

---

## 16.2 Calculus & Optimization

Calculus is the mathematics of change. In software engineering, it's essential for machine learning (gradient descent), physics simulations, signal processing, and understanding algorithmic complexity.

### 16.2.1 Derivatives and Rates of Change

**Theory:**

The derivative measures instantaneous rate of change:

```
f'(x) = lim[h→0] (f(x+h) - f(x)) / h
```

Interpretation:
- Slope of tangent line
- Velocity (derivative of position)
- Acceleration (derivative of velocity)

**Chain Rule** (crucial for backpropagation):
```
d/dx[f(g(x))] = f'(g(x)) · g'(x)
```

**WHY it matters:**

1. **Gradient Descent**: Derivatives tell us which direction to adjust parameters
2. **Backpropagation**: Chain rule applied to compute gradients through neural networks
3. **Physics Engines**: Simulating motion using differential equations
4. **Signal Processing**: Fourier transforms use complex derivatives
5. **Optimization**: Finding minima/maxima of objective functions

**Example - Numerical Differentiation:**

```python
import numpy as np
import matplotlib.pyplot as plt

def numerical_derivative(f, x, h=1e-5):
    """
    Approximate derivative using finite differences.
    
    Central difference: f'(x) ≈ (f(x+h) - f(x-h)) / (2h)
    More accurate than forward/backward differences.
    """
    return (f(x + h) - f(x - h)) / (2 * h)

def f(x):
    """Example function: f(x) = x² - 3x + 2"""
    return x**2 - 3*x + 2

def f_prime(x):
    """Analytical derivative: f'(x) = 2x - 3"""
    return 2*x - 3

# Test accuracy
x = 2.0
numerical = numerical_derivative(f, x)
analytical = f_prime(x)

print(f"Numerical derivative at x={x}: {numerical:.6f}")
print(f"Analytical derivative at x={x}: {analytical:.6f}")
print(f"Error: {abs(numerical - analytical):.2e}")

# Visualize
x_vals = np.linspace(-1, 5, 100)
plt.plot(x_vals, f(x_vals), label='f(x)')
plt.plot(x_vals, f_prime(x_vals), label="f'(x)")
plt.legend()
plt.grid()
# plt.show()
```

### 16.2.2 Partial Derivatives and Gradients

**Theory:**

For multivariable functions f(x₁, x₂, ..., xₙ), partial derivatives measure change along each dimension:

```
∂f/∂xᵢ = rate of change of f with respect to xᵢ, holding others constant
```

**Gradient** is the vector of all partial derivatives:

```
∇f = [∂f/∂x₁, ∂f/∂x₂, ..., ∂f/∂xₙ]
```

Properties:
- Points in direction of steepest ascent
- Perpendicular to level curves/surfaces
- Magnitude = rate of steepest increase

**WHY it matters:**

1. **Gradient Descent**: Move opposite to gradient to minimize loss
2. **Neural Network Training**: Backpropagation computes gradients
3. **Computer Vision**: Image gradients detect edges
4. **Game Physics**: Force fields represented as gradients of potential energy

**Example - Gradient Descent from Scratch:**

```python
import numpy as np

def gradient_descent(f, grad_f, x0, learning_rate=0.01, n_iterations=100):
    """
    Minimize function f using gradient descent.
    
    Args:
        f: objective function to minimize
        grad_f: gradient of f (returns numpy array)
        x0: initial guess
        learning_rate: step size
        n_iterations: number of steps
    
    Returns:
        x: optimal parameters
        history: trajectory of optimization
    """
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    
    for i in range(n_iterations):
        # Compute gradient at current position
        gradient = grad_f(x)
        
        # Update rule: x_new = x_old - α∇f(x)
        x = x - learning_rate * gradient
        
        history.append(x.copy())
        
        # Optional: print progress
        if i % 10 == 0:
            print(f"Iteration {i}: x={x}, f(x)={f(x):.6f}")
    
    return x, np.array(history)

# Example: minimize f(x,y) = x² + 2y²
def f(x):
    return x[0]**2 + 2*x[1]**2

def grad_f(x):
    return np.array([
        2*x[0],      # ∂f/∂x
        4*x[1]       # ∂f/∂y
    ])

# Start from [10, 10]
x_opt, history = gradient_descent(
    f, grad_f, 
    x0=[10.0, 10.0],
    learning_rate=0.1,
    n_iterations=50
)

print(f"\nOptimal x: {x_opt}")
print(f"Minimum value: {f(x_opt):.6f}")
print(f"Should be [0, 0] with value 0")
```

### 16.2.3 Optimization Algorithms

**Theory:**

Gradient descent variants:

1. **Batch Gradient Descent**: Use all data to compute gradient
   - Slow but accurate
   
2. **Stochastic Gradient Descent (SGD)**: Use one sample at a time
   - Fast but noisy
   
3. **Mini-batch SGD**: Use small batches
   - Best of both worlds
   
4. **Momentum**: Add velocity term to smooth updates
   ```
   v_t = βv_{t-1} + ∇f(x_t)
   x_{t+1} = x_t - αv_t
   ```

5. **Adam (Adaptive Moment Estimation)**: Adapts learning rate per parameter
   - Combines momentum + adaptive learning rates
   - Most popular in deep learning

**WHY it matters:**

1. **Training Speed**: Optimizers determine how fast models converge
2. **Final Performance**: Poor optimization → suboptimal solutions
3. **Hyperparameter Tuning**: Learning rate is critical hyperparameter
4. **Avoiding Local Minima**: Momentum helps escape saddle points

**Example - Adam Optimizer:**

```python
import numpy as np

class AdamOptimizer:
    """
    Adam optimizer: Adaptive Moment Estimation
    
    Combines:
    - Momentum (moving average of gradients)
    - RMSprop (adaptive learning rates)
    
    Used in ~90% of deep learning applications.
    """
    
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.lr = learning_rate
        self.beta1 = beta1  # Decay rate for first moment (mean)
        self.beta2 = beta2  # Decay rate for second moment (variance)
        self.epsilon = epsilon  # Numerical stability
        
        self.m = None  # First moment (mean of gradients)
        self.v = None  # Second moment (variance of gradients)
        self.t = 0     # Time step
    
    def update(self, params, grads):
        """
        Update parameters using Adam algorithm.
        
        Args:
            params: current parameters (numpy array)
            grads: gradients (numpy array)
        
        Returns:
            updated parameters
        """
        # Initialize moments on first call
        if self.m is None:
            self.m = np.zeros_like(params)
            self.v = np.zeros_like(params)
        
        self.t += 1
        
        # Update biased first moment estimate
        self.m = self.beta1 * self.m + (1 - self.beta1) * grads
        
        # Update biased second raw moment estimate
        self.v = self.beta2 * self.v + (1 - self.beta2) * (grads ** 2)
        
        # Bias correction (important in early iterations)
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        
        # Update parameters
        params = params - self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
        
        return params

# Example: train simple linear regression with Adam
def train_linear_regression_adam(X, y, n_epochs=100):
    """
    y = Xw + b
    Loss = MSE = (1/n)Σ(y_pred - y_true)²
    """
    n_samples, n_features = X.shape
    
    # Initialize parameters
    w = np.random.randn(n_features)
    b = 0.0
    
    optimizer_w = AdamOptimizer(learning_rate=0.01)
    optimizer_b = AdamOptimizer(learning_rate=0.01)
    
    for epoch in range(n_epochs):
        # Forward pass
        y_pred = X @ w + b
        
        # Compute loss (MSE)
        loss = np.mean((y_pred - y) ** 2)
        
        # Backward pass (compute gradients)
        error = y_pred - y
        grad_w = (2 / n_samples) * (X.T @ error)
        grad_b = (2 / n_samples) * np.sum(error)
        
        # Update parameters using Adam
        w = optimizer_w.update(w, grad_w)
        b = optimizer_b.update(np.array([b]), np.array([grad_b]))[0]
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Loss = {loss:.6f}")
    
    return w, b

# Test on synthetic data
np.random.seed(42)
X = np.random.randn(100, 5)  # 100 samples, 5 features
true_w = np.array([1, 2, -3, 0.5, -1])
true_b = 3.0
y = X @ true_w + true_b + 0.1 * np.random.randn(100)  # Add noise

w_learned, b_learned = train_linear_regression_adam(X, y)

print(f"\nTrue weights: {true_w}")
print(f"Learned weights: {w_learned}")
print(f"True bias: {true_b}")
print(f"Learned bias: {b_learned}")
```

### 16.2.4 Integrals and Accumulation

**Theory:**

Integration is the inverse of differentiation:

```
∫f(x)dx = F(x) + C, where F'(x) = f(x)
```

Definite integral (area under curve):
```
∫[a,b] f(x)dx = F(b) - F(a)
```

**WHY it matters:**

1. **Probability**: Computing cumulative distribution functions
2. **Physics Simulation**: Position from velocity (integration over time)
3. **Computer Graphics**: Monte Carlo ray tracing
4. **Signal Processing**: Convolution is integration
5. **Statistics**: Expected values are integrals

**Example - Monte Carlo Integration:**

```python
import numpy as np

def monte_carlo_integrate(f, a, b, n_samples=10000):
    """
    Approximate ∫[a,b] f(x)dx using Monte Carlo method.
    
    Principle: Average value × width
    ∫[a,b] f(x)dx ≈ (b-a) × (1/n)Σf(xᵢ)
    
    Useful for:
    - High-dimensional integrals
    - Complex integrands
    - No analytical solution
    """
    # Random samples uniformly distributed in [a, b]
    x_samples = np.random.uniform(a, b, n_samples)
    
    # Evaluate function at samples
    f_samples = f(x_samples)
    
    # Monte Carlo estimate
    integral = (b - a) * np.mean(f_samples)
    
    # Standard error (decreases as 1/√n)
    std_error = (b - a) * np.std(f_samples) / np.sqrt(n_samples)
    
    return integral, std_error

# Example: integrate sin(x) from 0 to π
# Analytical answer: ∫[0,π] sin(x)dx = 2

f = np.sin
result, error = monte_carlo_integrate(f, 0, np.pi, n_samples=100000)

print(f"Monte Carlo estimate: {result:.6f} ± {error:.6f}")
print(f"Analytical answer: 2.0")
print(f"Error: {abs(result - 2.0):.6f}")
```

### 16.2.5 Multivariable Calculus Applications

**Example - Backpropagation in Neural Networks:**

```python
import numpy as np

class TwoLayerNetwork:
    """
    Demonstrates backpropagation using chain rule.
    
    Architecture: Input -> Hidden -> Output
    Forward: y = σ(W₂ · σ(W₁ · x + b₁) + b₂)
    
    Backpropagation computes:
    ∂Loss/∂W₁, ∂Loss/∂b₁, ∂Loss/∂W₂, ∂Loss/∂b₂
    using chain rule recursively.
    """
    
    def __init__(self, input_size, hidden_size, output_size):
        # Initialize with small random weights
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
    
    def sigmoid(self, z):
        """Activation function"""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    
    def sigmoid_derivative(self, z):
        """σ'(z) = σ(z)(1 - σ(z))"""
        s = self.sigmoid(z)
        return s * (1 - s)
    
    def forward(self, X):
        """
        Forward pass - store intermediate values for backprop.
        
        Returns predictions and cache of intermediate values.
        """
        # Layer 1
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.sigmoid(self.z1)
        
        # Layer 2
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self.sigmoid(self.z2)
        
        return self.a2
    
    def backward(self, X, y, output):
        """
        Backpropagation - compute gradients using chain rule.
        
        Chain rule breakdown:
        ∂Loss/∂W₂ = ∂Loss/∂a₂ · ∂a₂/∂z₂ · ∂z₂/∂W₂
        ∂Loss/∂W₁ = ∂Loss/∂a₂ · ∂a₂/∂z₂ · ∂z₂/∂a₁ · ∂a₁/∂z₁ · ∂z₁/∂W₁
        """
        m = X.shape[0]  # batch size
        
        # Output layer gradients
        # ∂Loss/∂z₂ = (a₂ - y) · σ'(z₂)
        delta2 = output - y  # For MSE loss with sigmoid output
        
        dW2 = (self.a1.T @ delta2) / m
        db2 = np.sum(delta2, axis=0, keepdims=True) / m
        
        # Hidden layer gradients (chain rule!)
        # ∂Loss/∂a₁ = ∂Loss/∂z₂ · ∂z₂/∂a₁ = delta2 · W₂ᵀ
        delta1 = (delta2 @ self.W2.T) * self.sigmoid_derivative(self.z1)
        
        dW1 = (X.T @ delta1) / m
        db1 = np.sum(delta1, axis=0, keepdims=True) / m
        
        return dW1, db1, dW2, db2
    
    def train(self, X, y, learning_rate=0.1, epochs=1000):
        """Train using gradient descent"""
        for epoch in range(epochs):
            # Forward pass
            output = self.forward(X)
            
            # Compute loss
            loss = np.mean((output - y) ** 2)
            
            # Backward pass
            dW1, db1, dW2, db2 = self.backward(X, y, output)
            
            # Update parameters
            self.W1 -= learning_rate * dW1
            self.b1 -= learning_rate * db1
            self.W2 -= learning_rate * dW2
            self.b2 -= learning_rate * db2
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}: Loss = {loss:.6f}")

# Example: XOR problem (not linearly separable)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

nn = TwoLayerNetwork(input_size=2, hidden_size=4, output_size=1)
nn.train(X, y, learning_rate=0.5, epochs=5000)

# Test
predictions = nn.forward(X)
print("\nPredictions:")
for i in range(4):
    print(f"Input: {X[i]} -> Output: {predictions[i][0]:.4f} (expected: {y[i][0]})")
```

**Connections to Other Topics:**

- **Part 18 (ML)**: Optimization algorithms are core to ML training
- **Part 17 (Statistics)**: Maximum likelihood estimation uses calculus
- **Part 22.3 (OS)**: Scheduling algorithms use optimization
- **Part 11 (Performance)**: Auto-differentiation frameworks optimize gradient computation

---

## 16.3 Discrete Mathematics

Discrete mathematics deals with countable, distinct structures. It's fundamental to computer science: algorithms, data structures, cryptography, graph theory, and computational complexity.

### 16.3.1 Graph Theory

**Theory:**

A graph G = (V, E) consists of:
- V: set of vertices (nodes)
- E: set of edges (connections)

Types:
- **Directed** (edges have direction) vs **Undirected**
- **Weighted** (edges have costs) vs **Unweighted**
- **Cyclic** (contains cycles) vs **Acyclic** (DAG)

**WHY it matters:**

1. **Social Networks**: Users = vertices, friendships = edges
2. **Web**: Pages = vertices, links = edges (PageRank)
3. **Dependencies**: Packages = vertices, dependencies = edges (build systems)
4. **Networks**: Routers = vertices, connections = edges (routing algorithms)
5. **Maps**: Intersections = vertices, roads = edges (GPS navigation)

**Example - Graph Representations:**

```python
from collections import defaultdict, deque
import heapq

class Graph:
    """
    Graph data structure with common algorithms.
    Supports both directed and undirected graphs.
    """
    
    def __init__(self, directed=False):
        self.graph = defaultdict(list)  # Adjacency list
        self.directed = directed
    
    def add_edge(self, u, v, weight=1):
        """Add edge from u to v with optional weight"""
        self.graph[u].append((v, weight))
        if not self.directed:
            self.graph[v].append((u, weight))
    
    def bfs(self, start):
        """
        Breadth-First Search: explore level by level.
        
        Applications:
        - Shortest path (unweighted)
        - Level-order traversal
        - Connected components
        
        Time: O(V + E), Space: O(V)
        """
        visited = set()
        queue = deque([start])
        visited.add(start)
        result = []
        
        while queue:
            vertex = queue.popleft()
            result.append(vertex)
            
            for neighbor, _ in self.graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    def dfs(self, start):
        """
        Depth-First Search: explore as far as possible before backtracking.
        
        Applications:
        - Topological sort
        - Cycle detection
        - Path finding
        
        Time: O(V + E), Space: O(V)
        """
        visited = set()
        result = []
        
        def dfs_helper(vertex):
            visited.add(vertex)
            result.append(vertex)
            
            for neighbor, _ in self.graph[vertex]:
                if neighbor not in visited:
                    dfs_helper(neighbor)
        
        dfs_helper(start)
        return result
    
    def dijkstra(self, start):
        """
        Dijkstra's algorithm: shortest path in weighted graph.
        
        Applications:
        - GPS navigation
        - Network routing
        - Game AI pathfinding
        
        Time: O((V + E) log V) with binary heap
        
        Returns:
            distances: dict of shortest distances from start
            previous: dict for path reconstruction
        """
        distances = {vertex: float('inf') for vertex in self.graph}
        distances[start] = 0
        previous = {vertex: None for vertex in self.graph}
        
        # Priority queue: (distance, vertex)
        pq = [(0, start)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            # Skip if we've found a better path already
            if current_dist > distances[current]:
                continue
            
            for neighbor, weight in self.graph[current]:
                distance = current_dist + weight
                
                # Relaxation step
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        return distances, previous
    
    def topological_sort(self):
        """
        Topological sort: linear ordering of vertices in DAG.
        
        Applications:
        - Build systems (dependencies)
        - Task scheduling
        - Course prerequisites
        
        Time: O(V + E)
        
        Returns list of vertices in topological order, or None if cycle exists.
        """
        in_degree = defaultdict(int)
        
        # Compute in-degrees
        for u in self.graph:
            for v, _ in self.graph[u]:
                in_degree[v] += 1
        
        # Queue vertices with no incoming edges
        queue = deque([v for v in self.graph if in_degree[v] == 0])
        result = []
        
        while queue:
            u = queue.popleft()
            result.append(u)
            
            for v, _ in self.graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        # Check for cycle
        if len(result) != len(self.graph):
            return None  # Graph has cycle
        
        return result

# Example: Package dependency graph
g = Graph(directed=True)

# Dependencies (A -> B means A depends on B)
g.add_edge('app', 'logging')
g.add_edge('app', 'database')
g.add_edge('database', 'logging')
g.add_edge('database', 'config')
g.add_edge('logging', 'config')

# Topological sort gives valid build order
build_order = g.topological_sort()
print(f"Build order: {build_order}")
# Output: ['config', 'logging', 'database', 'app'] (or similar valid order)

# Example: Road network (weighted, undirected)
road_network = Graph(directed=False)
road_network.add_edge('A', 'B', weight=4)
road_network.add_edge('A', 'C', weight=2)
road_network.add_edge('B', 'C', weight=1)
road_network.add_edge('B', 'D', weight=5)
road_network.add_edge('C', 'D', weight=8)
road_network.add_edge('C', 'E', weight=10)
road_network.add_edge('D', 'E', weight=2)

distances, previous = road_network.dijkstra('A')
print(f"\nShortest distances from A: {dict(distances)}")

# Reconstruct path
def reconstruct_path(previous, start, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    return path[::-1]

path_to_e = reconstruct_path(previous, 'A', 'E')
print(f"Shortest path A -> E: {' -> '.join(path_to_e)} (distance: {distances['E']})")
```

### 16.3.2 Combinatorics

**Theory:**

Combinatorics studies counting, arrangement, and combination.

Key concepts:
- **Permutations**: ordered arrangements (n!/(n-k)!)
- **Combinations**: unordered selections (n!/(k!(n-k)!))
- **Pigeonhole Principle**: If n items in m containers, some container has ≥⌈n/m⌉ items
- **Inclusion-Exclusion**: |A∪B| = |A| + |B| - |A∩B|

**WHY it matters:**

1. **Algorithm Analysis**: Counting possible inputs/states
2. **Probability**: Counting favorable outcomes
3. **Hashing**: Birthday paradox for collision probability
4. **Testing**: Combinatorial test design
5. **Optimization**: Exploring solution spaces

**Example - Combinatorial Generation:**

```python
import itertools
import math

def binomial_coefficient(n, k):
    """
    C(n,k) = n! / (k!(n-k)!)
    Number of ways to choose k items from n items.
    """
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate_subsets(items):
    """
    Generate all 2^n subsets of items.
    
    Applications:
    - Feature selection in ML
    - Power set enumeration
    - Subset sum problem
    """
    n = len(items)
    for i in range(2**n):
        subset = [items[j] for j in range(n) if (i >> j) & 1]
        yield subset

# Example: all subsets of {1, 2, 3}
print("All subsets:")
for subset in generate_subsets([1, 2, 3]):
    print(subset)

# Example: permutations vs combinations
items = ['A', 'B', 'C', 'D']

print(f"\nPermutations of 2 from {items}:")
for perm in itertools.permutations(items, 2):
    print(perm)
# ('A','B') and ('B','A') are different

print(f"\nCombinations of 2 from {items}:")
for comb in itertools.combinations(items, 2):
    print(comb)
# ('A','B') and ('B','A') are the same

# Verify counts
n, k = 4, 2
perm_count = math.factorial(n) // math.factorial(n - k)
comb_count = binomial_coefficient(n, k)
print(f"\n{n}P{k} = {perm_count}")  # 12
print(f"{n}C{k} = {comb_count}")    # 6
```

**Example - Hash Collision Probability (Birthday Paradox):**

```python
import math

def birthday_collision_probability(n_items, hash_space_size):
    """
    Probability that at least 2 items collide when hashing n_items
    into hash_space_size buckets.
    
    Related to birthday paradox:
    With 23 people, ~50% chance two share a birthday (365 days).
    
    Formula: 1 - (m!/(m^n * (m-n)!))
    Approximation: 1 - e^(-n²/2m)
    
    Applications:
    - Hash table design
    - UUID collision probability
    - Cryptographic security
    """
    m = hash_space_size
    
    # Exact formula (only for small n)
    if n_items < 100:
        prob_no_collision = 1.0
        for i in range(n_items):
            prob_no_collision *= (m - i) / m
        return 1 - prob_no_collision
    
    # Approximation for large n
    exponent = -(n_items ** 2) / (2 * m)
    return 1 - math.exp(exponent)

# Example: 32-bit hash (2^32 buckets)
hash_32bit = 2**32

for n in [1000, 10000, 100000, 1000000]:
    prob = birthday_collision_probability(n, hash_32bit)
    print(f"{n:7d} items in 32-bit hash: {prob:.2%} collision probability")

# Example: UUID collision (128-bit)
# UUIDs are so large that collisions are astronomically unlikely
hash_128bit = 2**128
n_uuids = 10**15  # 1 quadrillion UUIDs
prob = birthday_collision_probability(n_uuids, hash_128bit)
print(f"\n{n_uuids:.0e} UUIDs (128-bit): {prob:.2e} collision probability")
```

### 16.3.3 Logic and Proof Techniques

**Theory:**

Logical foundations:
- **Propositions**: statements that are true or false
- **Connectives**: ∧ (and), ∨ (or), ¬ (not), → (implies), ↔ (iff)
- **Quantifiers**: ∀ (for all), ∃ (there exists)

Proof techniques:
1. **Direct proof**: Assume P, derive Q
2. **Proof by contradiction**: Assume ¬Q, derive contradiction
3. **Proof by induction**: Base case + inductive step
4. **Proof by contrapositive**: Prove ¬Q → ¬P instead of P → Q

**WHY it matters:**

1. **Correctness Proofs**: Prove algorithms work correctly
2. **Invariants**: Loop invariants in algorithm design
3. **Type Systems**: Proving type safety
4. **Formal Verification**: Provably correct software
5. **Protocol Security**: Proving cryptographic properties

**Example - Proof by Induction:**

```python
def sum_first_n(n):
    """
    Compute 1 + 2 + ... + n
    
    Claim: sum = n(n+1)/2
    
    Proof by induction:
    Base case: n=1, sum=1, formula=1(2)/2=1 ✓
    
    Inductive step:
    Assume true for n=k: 1+2+...+k = k(k+1)/2
    Prove for n=k+1:
        1+2+...+k+(k+1) 
        = k(k+1)/2 + (k+1)       [by inductive hypothesis]
        = (k+1)(k/2 + 1)
        = (k+1)(k+2)/2           ✓
    """
    return n * (n + 1) // 2

# Verify
for n in [1, 10, 100, 1000]:
    computed = sum(range(1, n+1))
    formula = sum_first_n(n)
    assert computed == formula, f"Failed for n={n}"
    print(f"n={n:4d}: sum={formula}")

def binary_search_correctness():
    """
    Binary search correctness via loop invariant.
    
    Invariant: If target exists in array, it's in array[left:right+1]
    
    Initialization: left=0, right=n-1 (whole array)
    Maintenance: Each iteration maintains invariant
    Termination: left > right means target not found
    """
    def binary_search(arr, target):
        left, right = 0, len(arr) - 1
        
        while left <= right:
            # Invariant: if target in arr, then target in arr[left:right+1]
            mid = (left + right) // 2
            
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1  # Maintains invariant (target > arr[mid])
            else:
                right = mid - 1  # Maintains invariant (target < arr[mid])
        
        # Termination: left > right, invariant → target not in arr
        return -1
    
    # Test
    arr = [1, 3, 5, 7, 9, 11]
    assert binary_search(arr, 7) == 3
    assert binary_search(arr, 4) == -1
    print("Binary search correctness verified")

binary_search_correctness()
```

**Example - Logical Reasoning in Type Systems:**

```python
from typing import Optional, List, Union
from abc import ABC, abstractmethod

class Expr(ABC):
    """
    Abstract syntax tree for simple typed language.
    Demonstrates type safety via construction.
    """
    @abstractmethod
    def type_check(self) -> str:
        """Returns type of expression: 'int' or 'bool'"""
        pass

class IntLiteral(Expr):
    def __init__(self, value: int):
        self.value = value
    
    def type_check(self) -> str:
        return 'int'

class BoolLiteral(Expr):
    def __init__(self, value: bool):
        self.value = value
    
    def type_check(self) -> str:
        return 'bool'

class Add(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right
    
    def type_check(self) -> str:
        """
        Typing rule for addition:
        Γ ⊢ e₁ : int    Γ ⊢ e₂ : int
        ────────────────────────────────
               Γ ⊢ e₁ + e₂ : int
        """
        left_type = self.left.type_check()
        right_type = self.right.type_check()
        
        if left_type != 'int' or right_type != 'int':
            raise TypeError(f"Cannot add {left_type} and {right_type}")
        
        return 'int'

class IfThenElse(Expr):
    def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def type_check(self) -> str:
        """
        Typing rule for if-then-else:
        Γ ⊢ e₁ : bool    Γ ⊢ e₂ : τ    Γ ⊢ e₃ : τ
        ────────────────────────────────────────────
              Γ ⊢ if e₁ then e₂ else e₃ : τ
        """
        cond_type = self.condition.type_check()
        if cond_type != 'bool':
            raise TypeError(f"Condition must be bool, got {cond_type}")
        
        then_type = self.then_branch.type_check()
        else_type = self.else_branch.type_check()
        
        if then_type != else_type:
            raise TypeError(f"Branches have different types: {then_type} vs {else_type}")
        
        return then_type

# Example: well-typed expression
expr1 = IfThenElse(
    condition=BoolLiteral(True),
    then_branch=IntLiteral(42),
    else_branch=Add(IntLiteral(10), IntLiteral(32))
)
print(f"expr1 type: {expr1.type_check()}")  # int

# Example: ill-typed expression (caught at "compile time")
try:
    expr2 = Add(IntLiteral(5), BoolLiteral(True))
    expr2.type_check()
except TypeError as e:
    print(f"Type error caught: {e}")
```

**Connections to Other Topics:**

- **Part 4 (Data Structures)**: Graph algorithms use graph theory
- **Part 5 (Algorithms)**: Complexity analysis uses combinatorics
- **Part 9 (Security)**: Cryptography uses number theory (discrete math)
- **Part 10 (Testing)**: Combinatorial testing uses combinatorics

---

# PART 17: STATISTICS & PROBABILITY THEORY

Statistics and probability are essential for data-driven decision making, A/B testing, machine learning, system reliability, and understanding uncertainty in software systems.

## 17.1 Probability Foundations

### 17.1.1 Probability Axioms and Rules

**Theory:**

Probability measures uncertainty on scale [0, 1]:
- P(A) = 0: impossible event
- P(A) = 1: certain event

**Axioms:**
1. P(A) ≥ 0 for all events A
2. P(S) = 1 where S is sample space
3. P(A∪B) = P(A) + P(B) if A and B are mutually exclusive

**Derived rules:**
- **Complement**: P(¬A) = 1 - P(A)
- **Addition**: P(A∪B) = P(A) + P(B) - P(A∩B)
- **Multiplication** (independent): P(A∩B) = P(A)·P(B)
- **Conditional**: P(A|B) = P(A∩B) / P(B)

**WHY it matters:**

1. **A/B Testing**: Statistical significance of experiments
2. **ML Models**: Probabilistic predictions
3. **System Reliability**: Failure probability calculations
4. **Security**: Attack probability assessment
5. **Performance**: Latency percentiles

**Example - Monte Carlo Simulation:**

```python
import numpy as np
import matplotlib.pyplot as plt

def estimate_pi(n_samples):
    """
    Estimate π using Monte Carlo method.
    
    Principle:
    - Circle area = πr²
    - Square area = (2r)² = 4r²
    - Ratio = π/4
    
    Sample random points in square, count how many fall in circle.
    """
    # Random points in [0,1] × [0,1]
    x = np.random.uniform(0, 1, n_samples)
    y = np.random.uniform(0, 1, n_samples)
    
    # Check if inside quarter circle: x² + y² ≤ 1
    inside_circle = (x**2 + y**2) <= 1
    
    # Estimate: π/4 ≈ (points inside) / (total points)
    pi_estimate = 4 * np.sum(inside_circle) / n_samples
    
    return pi_estimate

# Run simulation with increasing samples
for n in [100, 1000, 10000, 100000, 1000000]:
    pi_est = estimate_pi(n)
    error = abs(pi_est - np.pi)
    print(f"n={n:7d}: π ≈ {pi_est:.6f} (error: {error:.6f})")

# Law of large numbers: error decreases as n increases
```

### 17.1.2 Probability Distributions

**Theory:**

A probability distribution describes how probability is distributed over possible values.

**Discrete distributions:**
- **Bernoulli**: Single trial (coin flip)
- **Binomial**: n independent Bernoulli trials
- **Poisson**: Number of events in fixed time interval
- **Geometric**: Trials until first success

**Continuous distributions:**
- **Uniform**: All values equally likely
- **Normal (Gaussian)**: Bell curve (Central Limit Theorem)
- **Exponential**: Time between events
- **Beta**: Probability of probability

**WHY it matters:**

1. **Load Testing**: Request arrivals follow Poisson distribution
2. **ML**: Many models assume Gaussian noise
3. **A/B Testing**: Binomial distribution for conversion rates
4. **Reliability**: Exponential distribution for time to failure
5. **Bayesian Methods**: Prior distributions

**Example - Common Distributions:**

```python
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

class ProbabilityDistributions:
    """
    Demonstrates common probability distributions and their applications.
    """
    
    @staticmethod
    def binomial_distribution():
        """
        Binomial: P(X=k) = C(n,k) * p^k * (1-p)^(n-k)
        
        Application: A/B testing
        - n trials (users)
        - k successes (conversions)
        - p probability (conversion rate)
        """
        n = 100  # 100 users
        p = 0.05  # 5% conversion rate
        
        # Probability mass function
        k_values = range(0, 20)
        probabilities = [stats.binom.pmf(k, n, p) for k in k_values]
        
        # Expected value: E[X] = np
        expected = n * p
        
        # Variance: Var(X) = np(1-p)
        variance = n * p * (1 - p)
        
        print("Binomial Distribution (A/B Testing)")
        print(f"Expected conversions: {expected:.2f}")
        print(f"Standard deviation: {np.sqrt(variance):.2f}")
        print(f"P(X ≥ 10) = {1 - stats.binom.cdf(9, n, p):.4f}")
        
        # Simulate
        simulated = np.random.binomial(n, p, size=10000)
        print(f"Simulated mean: {np.mean(simulated):.2f}")
    
    @staticmethod
    def poisson_distribution():
        """
        Poisson: P(X=k) = (λ^k * e^(-λ)) / k!
        
        Application: Request rate modeling
        - λ: average rate (e.g., 5 requests/second)
        - k: number of events
        """
        lambda_rate = 5  # Average 5 requests/second
        
        # Probability of exactly k requests in 1 second
        for k in [0, 5, 10, 15]:
            prob = stats.poisson.pmf(k, lambda_rate)
            print(f"P(X = {k:2d}) = {prob:.4f}")
        
        # Probability of more than 10 requests (capacity planning)
        prob_overload = 1 - stats.poisson.cdf(10, lambda_rate)
        print(f"\nP(X > 10) = {prob_overload:.4f}")
        print("→ Need capacity for >10 req/s to handle this load")
    
    @staticmethod
    def normal_distribution():
        """
        Normal: f(x) = (1/√(2πσ²)) * e^(-(x-μ)²/(2σ²))
        
        Application: Response time modeling (after log transform)
        """
        mu = 100  # Mean response time (ms)
        sigma = 15  # Standard deviation
        
        # 68-95-99.7 rule
        print("\nNormal Distribution (Response Times)")
        print(f"68% of requests: {mu - sigma:.0f}ms to {mu + sigma:.0f}ms")
        print(f"95% of requests: {mu - 2*sigma:.0f}ms to {mu + 2*sigma:.0f}ms")
        print(f"99.7% of requests: {mu - 3*sigma:.0f}ms to {mu + 3*sigma:.0f}ms")
        
        # Percentiles (SLA targets)
        p50 = stats.norm.ppf(0.50, mu, sigma)
        p95 = stats.norm.ppf(0.95, mu, sigma)
        p99 = stats.norm.ppf(0.99, mu, sigma)
        
        print(f"\nPercentiles:")
        print(f"P50 (median): {p50:.1f}ms")
        print(f"P95: {p95:.1f}ms")
        print(f"P99: {p99:.1f}ms")
    
    @staticmethod
    def exponential_distribution():
        """
        Exponential: f(x) = λe^(-λx)
        
        Application: Time between events (memoryless property)
        """
        lambda_rate = 0.1  # Average 1 event per 10 minutes
        
        # Probability that next event occurs within t minutes
        for t in [5, 10, 20, 30]:
            prob = stats.expon.cdf(t, scale=1/lambda_rate)
            print(f"P(T ≤ {t:2d} min) = {prob:.4f}")
        
        # Mean time between events
        mean_time = 1 / lambda_rate
        print(f"\nMean time between events: {mean_time:.1f} minutes")

# Run examples
ProbabilityDistributions.binomial_distribution()
print()
ProbabilityDistributions.poisson_distribution()
ProbabilityDistributions.normal_distribution()
print()
ProbabilityDistributions.exponential_distribution()
```

### 17.1.3 Bayes' Theorem

**Theory:**

Bayes' theorem updates beliefs based on evidence:

```
P(A|B) = P(B|A) · P(A) / P(B)
```

Where:
- P(A|B): posterior probability (after seeing evidence B)
- P(B|A): likelihood (probability of evidence given A)
- P(A): prior probability (before seeing evidence)
- P(B): marginal probability (normalization constant)

**WHY it matters:**

1. **Spam Filtering**: P(spam|words)
2. **Medical Diagnosis**: P(disease|symptoms)
3. **Machine Learning**: Naive Bayes classifier
4. **A/B Testing**: Bayesian inference
5. **Fraud Detection**: P(fraud|transaction_pattern)

**Example - Spam Filter:**

```python
import numpy as np
from collections import defaultdict

class NaiveBayesSpamFilter:
    """
    Spam filter using Bayes' theorem.
    
    P(spam|words) = P(words|spam) · P(spam) / P(words)
    
    "Naive" assumption: words are independent
    P(words|spam) = P(w₁|spam) · P(w₂|spam) · ... · P(wₙ|spam)
    """
    
    def __init__(self):
        self.word_counts_spam = defaultdict(int)
        self.word_counts_ham = defaultdict(int)
        self.spam_count = 0
        self.ham_count = 0
    
    def train(self, emails, labels):
        """
        Train on labeled emails.
        
        emails: list of strings
        labels: list of 0 (ham) or 1 (spam)
        """
        for email, label in zip(emails, labels):
            words = email.lower().split()
            
            if label == 1:  # spam
                self.spam_count += 1
                for word in words:
                    self.word_counts_spam[word] += 1
            else:  # ham
                self.ham_count += 1
                for word in words:
                    self.word_counts_ham[word] += 1
    
    def predict_proba(self, email):
        """
        Compute P(spam|email) using Bayes' theorem.
        
        Returns probability that email is spam.
        """
        words = email.lower().split()
        
        # Prior probabilities
        total = self.spam_count + self.ham_count
        p_spam = self.spam_count / total
        p_ham = self.ham_count / total
        
        # Likelihood (log probabilities for numerical stability)
        log_p_spam = np.log(p_spam)
        log_p_ham = np.log(p_ham)
        
        total_spam_words = sum(self.word_counts_spam.values())
        total_ham_words = sum(self.word_counts_ham.values())
        vocab_size = len(set(self.word_counts_spam.keys()) | 
                         set(self.word_counts_ham.keys()))
        
        for word in words:
            # Laplace smoothing: add 1 to avoid zero probabilities
            p_word_given_spam = (self.word_counts_spam[word] + 1) / \
                                (total_spam_words + vocab_size)
            p_word_given_ham = (self.word_counts_ham[word] + 1) / \
                               (total_ham_words + vocab_size)
            
            log_p_spam += np.log(p_word_given_spam)
            log_p_ham += np.log(p_word_given_ham)
        
        # Normalize to get probabilities
        # log(a/(a+b)) = log(a) - log(a+b)
        # Use log-sum-exp trick for numerical stability
        max_log_p = max(log_p_spam, log_p_ham)
        log_p_spam -= max_log_p
        log_p_ham -= max_log_p
        
        p_spam_given_email = np.exp(log_p_spam) / \
                            (np.exp(log_p_spam) + np.exp(log_p_ham))
        
        return p_spam_given_email
    
    def predict(self, email):
        """Classify email as spam (1) or ham (0)"""
        return 1 if self.predict_proba(email) > 0.5 else 0

# Example usage
spam_filter = NaiveBayesSpamFilter()

# Training data
train_emails = [
    "get free money now click here",
    "meeting tomorrow at 3pm",
    "win lottery jackpot",
    "project deadline update",
    "congratulations you won",
    "please review the attached document"
]
train_labels = [1, 0, 1, 0, 1, 0]  # 1=spam, 0=ham

spam_filter.train(train_emails, train_labels)

# Test
test_emails = [
    "free money winner",
    "meeting scheduled",
    "urgent project update"
]

for email in test_emails:
    prob = spam_filter.predict_proba(email)
    label = spam_filter.predict(email)
    print(f"Email: '{email}'")
    print(f"  P(spam) = {prob:.3f} → {'SPAM' if label else 'HAM'}\n")
```

**Example - Medical Diagnosis:**

```python
def medical_diagnosis_example():
    """
    Classic Bayes' theorem example demonstrating counter-intuitive result.
    
    Problem:
    - Disease prevalence: 1% (prior)
    - Test sensitivity: 95% (true positive rate)
    - Test specificity: 95% (true negative rate)
    
    Question: If test is positive, what's probability of having disease?
    """
    # Given
    p_disease = 0.01  # P(D)
    p_no_disease = 0.99  # P(¬D)
    p_positive_given_disease = 0.95  # P(+|D) - sensitivity
    p_positive_given_no_disease = 0.05  # P(+|¬D) - false positive rate
    
    # Compute P(+) using law of total probability
    # P(+) = P(+|D)·P(D) + P(+|¬D)·P(¬D)
    p_positive = (p_positive_given_disease * p_disease + 
                  p_positive_given_no_disease * p_no_disease)
    
    # Bayes' theorem: P(D|+) = P(+|D)·P(D) / P(+)
    p_disease_given_positive = (p_positive_given_disease * p_disease) / p_positive
    
    print("Medical Diagnosis with Bayes' Theorem")
    print(f"Prior: P(disease) = {p_disease:.1%}")
    print(f"Test sensitivity: {p_positive_given_disease:.1%}")
    print(f"Test specificity: {1 - p_positive_given_no_disease:.1%}")
    print(f"\nP(positive) = {p_positive:.4f}")
    print(f"P(disease|positive) = {p_disease_given_positive:.1%}")
    print("\n→ Despite 95% accuracy, only ~16% chance of actually having disease!")
    print("  This is because disease is rare (low prior)")

medical_diagnosis_example()
```

### 17.1.4 Expected Value and Variance

**Theory:**

**Expected value** (mean):
```
E[X] = Σ xᵢ · P(X = xᵢ)  (discrete)
E[X] = ∫ x · f(x) dx     (continuous)
```

**Variance** (spread):
```
Var(X) = E[(X - E[X])²] = E[X²] - (E[X])²
```

**Standard deviation**: σ = √Var(X)

**WHY it matters:**

1. **Decision Making**: Expected value for comparing options
2. **Performance**: Mean latency vs variance (consistency)
3. **Risk Assessment**: High variance = high uncertainty
4. **A/B Testing**: Sample size calculations
5. **Resource Planning**: Expected load

**Example - Expected Value in Decision Making:**

```python
import numpy as np

class DecisionAnalysis:
    """
    Use expected value to make optimal decisions under uncertainty.
    """
    
    @staticmethod
    def cache_sizing_decision():
        """
        Decide optimal cache size based on cost/benefit analysis.
        
        Trade-off:
        - Larger cache → fewer cache misses → faster responses
        - Larger cache → higher memory cost
        """
        cache_sizes = [0, 100, 500, 1000]  # MB
        
        for size in cache_sizes:
            # Hit rate increases with size (diminishing returns)
            hit_rate = 1 - np.exp(-size / 500)
            miss_rate = 1 - hit_rate
            
            # Costs
            cache_hit_time = 1  # ms
            cache_miss_time = 100  # ms (fetch from DB)
            memory_cost_per_mb = 0.01  # $ per MB per day
            
            # Expected latency
            expected_latency = (hit_rate * cache_hit_time + 
                              miss_rate * cache_miss_time)
            
            # Daily costs
            memory_cost = size * memory_cost_per_mb
            latency_cost = expected_latency * 0.001  # Arbitrary: $0.001 per ms
            
            total_cost = memory_cost + latency_cost
            
            print(f"Cache size: {size:4d} MB")
            print(f"  Hit rate: {hit_rate:.2%}")
            print(f"  Expected latency: {expected_latency:.1f} ms")
            print(f"  Daily cost: ${total_cost:.3f}\n")
    
    @staticmethod
    def ab_test_roi():
        """
        Calculate expected ROI of A/B test to determine if worth running.
        """
        # Current version
        current_conversion_rate = 0.05  # 5%
        revenue_per_conversion = 50  # $
        
        # Proposed version (uncertain)
        possible_improvements = [0.001, 0.003, 0.005, 0.01]
        probabilities = [0.3, 0.4, 0.2, 0.1]  # Our beliefs
        
        # Expected improvement
        expected_improvement = sum(imp * prob for imp, prob in 
                                  zip(possible_improvements, probabilities))
        
        # Monthly users
        monthly_users = 100000
        
        # Expected additional revenue
        current_revenue = monthly_users * current_conversion_rate * revenue_per_conversion
        new_conversion_rate = current_conversion_rate + expected_improvement
        new_revenue = monthly_users * new_conversion_rate * revenue_per_conversion
        expected_gain = new_revenue - current_revenue
        
        # Cost of running test
        engineering_cost = 5000  # Developer time
        opportunity_cost = 1000  # Delayed features
        
        total_cost = engineering_cost + opportunity_cost
        
        print("A/B Test ROI Analysis")
        print(f"Expected conversion rate improvement: {expected_improvement:.2%}")
        print(f"Expected monthly revenue gain: ${expected_gain:,.0f}")
        print(f"Cost of test: ${total_cost:,.0f}")
        print(f"Break-even time: {total_cost / expected_gain:.1f} months")
        print(f"Expected 1-year ROI: {(12 * expected_gain - total_cost) / total_cost:.1%}")

DecisionAnalysis.cache_sizing_decision()
print()
DecisionAnalysis.ab_test_roi()
```

**Connections to Other Topics:**

- **Part 18 (ML)**: Probabilistic models, loss functions
- **Part 11 (Performance)**: Latency percentiles
- **Part 10 (Testing)**: Statistical testing, coverage
- **Part 12 (Monitoring)**: Alerting thresholds

---

## 17.2 Statistical Methods

### 17.2.1 Hypothesis Testing

**Theory:**

Hypothesis testing determines if observed data provides enough evidence to reject a null hypothesis.

**Framework:**
1. **Null hypothesis (H₀)**: Default assumption (no effect)
2. **Alternative hypothesis (H₁)**: What we're testing for
3. **Test statistic**: Computed from data
4. **p-value**: P(observing data | H₀ is true)
5. **Significance level (α)**: Threshold for rejection (typically 0.05)

**Decision rule:**
- If p-value < α: Reject H₀ (statistically significant)
- If p-value ≥ α: Fail to reject H₀ (not significant)

**Errors:**
- **Type I error (false positive)**: Reject H₀ when it's true (probability = α)
- **Type II error (false negative)**: Fail to reject H₀ when it's false (probability = β)
- **Power**: 1 - β (probability of detecting true effect)

**WHY it matters:**

1. **A/B Testing**: Determine if variant is significantly better
2. **Performance**: Detect regressions statistically
3. **ML Evaluation**: Compare model performance
4. **Quality Assurance**: Statistical process control
5. **Business Decisions**: Data-driven conclusions

**Example - t-test for A/B Testing:**

```python
import numpy as np
import scipy.stats as stats

class ABTesting:
    """
    Statistical hypothesis testing for A/B experiments.
    """
    
    @staticmethod
    def two_sample_t_test(data_a, data_b, alpha=0.05):
        """
        Compare two groups using Welch's t-test.
        
        H₀: μ_A = μ_B (no difference in means)
        H₁: μ_A ≠ μ_B (means are different)
        
        Used for: comparing response times, conversion rates (after transform)
        """
        # Sample statistics
        n_a, n_b = len(data_a), len(data_b)
        mean_a, mean_b = np.mean(data_a), np.mean(data_b)
        std_a, std_b = np.std(data_a, ddof=1), np.std(data_b, ddof=1)
        
        # Perform Welch's t-test (doesn't assume equal variances)
        t_statistic, p_value = stats.ttest_ind(data_a, data_b, equal_var=False)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / 
                            (n_a + n_b - 2))
        cohens_d = (mean_a - mean_b) / pooled_std
        
        # Confidence interval for difference
        se_diff = np.sqrt(std_a**2 / n_a + std_b**2 / n_b)
        df = ((std_a**2 / n_a + std_b**2 / n_b)**2 / 
              ((std_a**2 / n_a)**2 / (n_a - 1) + (std_b**2 / n_b)**2 / (n_b - 1)))
        t_critical = stats.t.ppf(1 - alpha/2, df)
        ci_lower = (mean_a - mean_b) - t_critical * se_diff
        ci_upper = (mean_a - mean_b) + t_critical * se_diff
        
        # Results
        is_significant = p_value < alpha
        
        print("Two-Sample t-Test Results")
        print(f"Group A: n={n_a}, mean={mean_a:.3f}, std={std_a:.3f}")
        print(f"Group B: n={n_b}, mean={mean_b:.3f}, std={std_b:.3f}")
        print(f"\nt-statistic: {t_statistic:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Significance level: {alpha}")
        print(f"Result: {'SIGNIFICANT' if is_significant else 'NOT SIGNIFICANT'}")
        print(f"\nEffect size (Cohen's d): {cohens_d:.3f}")
        print(f"95% CI for difference: [{ci_lower:.3f}, {ci_upper:.3f}]")
        
        return is_significant, p_value, cohens_d
    
    @staticmethod
    def proportion_test(conversions_a, n_a, conversions_b, n_b, alpha=0.05):
        """
        Test difference in conversion rates (proportions).
        
        H₀: p_A = p_B
        H₁: p_A ≠ p_B
        
        Uses normal approximation (valid for large samples).
        """
        # Sample proportions
        p_a = conversions_a / n_a
        p_b = conversions_b / n_b
        
        # Pooled proportion (under H₀)
        p_pool = (conversions_a + conversions_b) / (n_a + n_b)
        
        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
        
        # Z-statistic
        z = (p_a - p_b) / se
        
        # Two-tailed p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Confidence interval for difference
        se_diff = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
        z_critical = stats.norm.ppf(1 - alpha/2)
        ci_lower = (p_a - p_b) - z_critical * se_diff
        ci_upper = (p_a - p_b) + z_critical * se_diff
        
        # Relative improvement
        relative_improvement = (p_a - p_b) / p_b if p_b > 0 else float('inf')
        
        is_significant = p_value < alpha
        
        print("Proportion Test Results (Conversion Rates)")
        print(f"Group A: {conversions_a}/{n_a} = {p_a:.2%}")
        print(f"Group B: {conversions_b}/{n_b} = {p_b:.2%}")
        print(f"Relative improvement: {relative_improvement:+.2%}")
        print(f"\nz-statistic: {z:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Result: {'SIGNIFICANT' if is_significant else 'NOT SIGNIFICANT'}")
        print(f"95% CI for difference: [{ci_lower:.2%}, {ci_upper:.2%}]")
        
        return is_significant, p_value
    
    @staticmethod
    def required_sample_size(p_control, mde, alpha=0.05, power=0.8):
        """
        Calculate required sample size for detecting minimum detectable effect.
        
        Args:
            p_control: baseline conversion rate
            mde: minimum detectable effect (relative improvement)
            alpha: significance level (Type I error rate)
            power: statistical power (1 - Type II error rate)
        
        Returns:
            samples needed per group
        """
        p_treatment = p_control * (1 + mde)
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # Sample size formula (for proportions)
        n = ((z_alpha * np.sqrt(2 * p_control * (1 - p_control)) +
              z_beta * np.sqrt(p_control * (1 - p_control) + 
                              p_treatment * (1 - p_treatment))) / 
             (p_treatment - p_control))**2
        
        return int(np.ceil(n))

# Example 1: Compare page load times
print("=" * 60)
print("Example 1: Page Load Times")
print("=" * 60)
np.random.seed(42)

# Version A: current (mean=2.0s, std=0.5s)
load_times_a = np.random.normal(2.0, 0.5, 1000)

# Version B: optimized (mean=1.8s, std=0.5s)
load_times_b = np.random.normal(1.8, 0.5, 1000)

ABTesting.two_sample_t_test(load_times_a, load_times_b)

# Example 2: Compare conversion rates
print("\n" + "=" * 60)
print("Example 2: Conversion Rates")
print("=" * 60)

# Group A: 520 conversions out of 10000 users
# Group B: 580 conversions out of 10000 users
ABTesting.proportion_test(
    conversions_a=520, n_a=10000,
    conversions_b=580, n_b=10000
)

# Example 3: Sample size calculation
print("\n" + "=" * 60)
print("Example 3: Sample Size Planning")
print("=" * 60)

baseline_rate = 0.05  # 5% conversion rate
desired_improvement = 0.10  # Want to detect 10% relative improvement

n_required = ABTesting.required_sample_size(
    p_control=baseline_rate,
    mde=desired_improvement,
    alpha=0.05,
    power=0.8
)

print(f"Baseline conversion rate: {baseline_rate:.1%}")
print(f"Minimum detectable effect: {desired_improvement:+.1%} (relative)")
print(f"Significance level: 5%")
print(f"Statistical power: 80%")
print(f"\nRequired sample size: {n_required:,} per group")
print(f"Total users needed: {2 * n_required:,}")
```

### 17.2.2 Confidence Intervals

**Theory:**

A confidence interval gives a range of plausible values for a population parameter.

95% confidence interval means:
- If we repeated the experiment many times, 95% of the intervals would contain the true parameter

**Formula (for mean):**
```
CI = x̄ ± t* · (s / √n)
```

Where:
- x̄: sample mean
- t*: critical value from t-distribution
- s: sample standard deviation
- n: sample size

**WHY it matters:**

1. **Uncertainty Quantification**: Express precision of estimates
2. **A/B Testing**: Confidence intervals more informative than p-values
3. **Performance Metrics**: SLA compliance intervals
4. **Business Metrics**: Revenue projections with uncertainty
5. **ML Models**: Prediction intervals

**Example - Confidence Intervals:**

```python
import numpy as np
import scipy.stats as stats

def confidence_interval_mean(data, confidence=0.95):
    """
    Compute confidence interval for population mean.
    
    Returns: (mean, lower_bound, upper_bound)
    """
    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)  # Standard error = std / sqrt(n)
    
    # t-distribution (accounts for sample size)
    margin_of_error = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    
    return mean, mean - margin_of_error, mean + margin_of_error

def bootstrap_confidence_interval(data, statistic_func, confidence=0.95, n_bootstrap=10000):
    """
    Bootstrap confidence interval for any statistic.
    
    Bootstrap: resample with replacement to estimate sampling distribution.
    Works for medians, percentiles, or any complex statistic.
    """
    bootstrap_statistics = []
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        sample = np.random.choice(data, size=len(data), replace=True)
        stat = statistic_func(sample)
        bootstrap_statistics.append(stat)
    
    # Percentile method
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_statistics, 100 * alpha / 2)
    upper = np.percentile(bootstrap_statistics, 100 * (1 - alpha / 2))
    observed = statistic_func(data)
    
    return observed, lower, upper

# Example: Response time measurements
np.random.seed(42)
response_times = np.random.lognormal(mean=4, sigma=0.5, size=500)  # Log-normal distribution

# Traditional CI for mean
mean, ci_lower, ci_upper = confidence_interval_mean(response_times)
print("Traditional Confidence Interval (Mean)")
print(f"Mean: {mean:.2f}ms")
print(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")

# Bootstrap CI for median (more robust to outliers)
median_func = lambda x: np.median(x)
median, boot_lower, boot_upper = bootstrap_confidence_interval(
    response_times, median_func
)
print(f"\nBootstrap Confidence Interval (Median)")
print(f"Median: {median:.2f}ms")
print(f"95% CI: [{boot_lower:.2f}, {boot_upper:.2f}]")

# Bootstrap CI for 95th percentile
p95_func = lambda x: np.percentile(x, 95)
p95, p95_lower, p95_upper = bootstrap_confidence_interval(
    response_times, p95_func
)
print(f"\nBootstrap Confidence Interval (P95)")
print(f"P95: {p95:.2f}ms")
print(f"95% CI: [{p95_lower:.2f}, {p95_upper:.2f}]")
```

### 17.2.3 Regression Analysis

**Theory:**

Regression models the relationship between dependent variable Y and independent variables X.

**Linear regression:**
```
Y = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ + ε
```

**Fitting:** Minimize sum of squared residuals (least squares)
```
min Σ(yᵢ - ŷᵢ)²
```

**Evaluation metrics:**
- **R²**: Proportion of variance explained (0 to 1)
- **RMSE**: Root mean squared error
- **MAE**: Mean absolute error

**WHY it matters:**

1. **Capacity Planning**: Predict resource needs from growth
2. **Performance**: Model latency vs load
3. **Business Forecasting**: Revenue predictions
4. **Feature Importance**: Which factors matter most
5. **ML**: Foundation for many algorithms

**Example - Linear Regression:**

```python
import numpy as np
import matplotlib.pyplot as plt

class LinearRegression:
    """
    Linear regression from scratch using normal equations.
    
    Demonstrates the mathematical foundation of regression.
    """
    
    def __init__(self):
        self.coefficients = None
        self.intercept = None
    
    def fit(self, X, y):
        """
        Fit using normal equation: β = (XᵀX)⁻¹Xᵀy
        
        This is the closed-form solution to minimize squared error.
        """
        # Add intercept term (column of ones)
        X_with_intercept = np.column_stack([np.ones(len(X)), X])
        
        # Normal equation
        # β = (XᵀX)⁻¹Xᵀy
        XtX = X_with_intercept.T @ X_with_intercept
        Xty = X_with_intercept.T @ y
        params = np.linalg.solve(XtX, Xty)
        
        self.intercept = params[0]
        self.coefficients = params[1:]
    
    def predict(self, X):
        """Make predictions"""
        return self.intercept + X @ self.coefficients
    
    def score(self, X, y):
        """Compute R² score"""
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)  # Residual sum of squares
        ss_tot = np.sum((y - np.mean(y)) ** 2)  # Total sum of squares
        return 1 - (ss_res / ss_tot)
    
    def rmse(self, X, y):
        """Root mean squared error"""
        y_pred = self.predict(X)
        return np.sqrt(np.mean((y - y_pred) ** 2))

# Example: Predict server load from time of day and day of week
np.random.seed(42)

# Generate synthetic data
n_samples = 1000
hour_of_day = np.random.randint(0, 24, n_samples)
is_weekend = np.random.randint(0, 2, n_samples)

# True relationship (unknown to model)
# Load = 100 + 5*hour - 30*is_weekend + noise
true_load = 100 + 5*hour_of_day - 30*is_weekend + np.random.normal(0, 10, n_samples)

# Prepare features
X = np.column_stack([hour_of_day, is_weekend])
y = true_load

# Split into train/test
split = int(0.8 * n_samples)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

print("Linear Regression: Server Load Prediction")
print(f"Intercept: {model.intercept:.2f}")
print(f"Coefficient (hour): {model.coefficients[0]:.2f}")
print(f"Coefficient (is_weekend): {model.coefficients[1]:.2f}")
print(f"\nR² (train): {model.score(X_train, y_train):.4f}")
print(f"R² (test): {model.score(X_test, y_test):.4f}")
print(f"RMSE (test): {model.rmse(X_test, y_test):.2f}")

# Interpret coefficients
print("\nInterpretation:")
print(f"- Each hour increases load by {model.coefficients[0]:.1f} units")
print(f"- Weekends decrease load by {-model.coefficients[1]:.1f} units")

# Make predictions
print("\nExample predictions:")
for hour, weekend in [(9, 0), (14, 0), (9, 1), (22, 1)]:
    pred = model.predict(np.array([[hour, weekend]]))[0]
    day_type = "weekend" if weekend else "weekday"
    print(f"  {hour:02d}:00 on {day_type}: {pred:.1f} load")
```

**Connections to Other Topics:**

- **Part 18 (ML)**: Regression is foundation of supervised learning
- **Part 11 (Performance)**: Statistical performance analysis
- **Part 12 (Monitoring)**: Anomaly detection using statistics
- **Part 20 (UX)**: A/B testing and user research

---

## 17.3 Data Modeling

### 17.3.1 Time Series Analysis

**Theory:**

Time series data: observations indexed by time (t₁, t₂, ..., tₙ).

Components:
- **Trend**: Long-term increase/decrease
- **Seasonality**: Repeating patterns (daily, weekly, yearly)
- **Cyclic**: Irregular fluctuations
- **Noise**: Random variation

**Models:**
- **Moving Average (MA)**: Smooth short-term fluctuations
- **Exponential Smoothing**: Weighted average with decay
- **ARIMA**: AutoRegressive Integrated Moving Average
- **Prophet**: Facebook's forecasting tool

**WHY it matters:**

1. **Capacity Planning**: Forecast resource needs
2. **Anomaly Detection**: Detect unusual patterns
3. **Business Metrics**: Predict revenue, user growth
4. **Performance Monitoring**: Track latency trends
5. **Incident Response**: Detect degradations early

**Example - Time Series Forecasting:**

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class TimeSeriesAnalysis:
    """
    Time series analysis and forecasting techniques.
    """
    
    @staticmethod
    def moving_average(data, window_size):
        """
        Simple moving average: smooth short-term fluctuations.
        
        MA(t) = (x(t) + x(t-1) + ... + x(t-window_size+1)) / window_size
        """
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')
    
    @staticmethod
    def exponential_smoothing(data, alpha=0.3):
        """
        Exponential smoothing: more weight to recent observations.
        
        S(t) = α·x(t) + (1-α)·S(t-1)
        
        α near 1: responsive to changes
        α near 0: smooth, slow to respond
        """
        smoothed = [data[0]]
        for x in data[1:]:
            smoothed.append(alpha * x + (1 - alpha) * smoothed[-1])
        return np.array(smoothed)
    
    @staticmethod
    def seasonal_decomposition(data, period):
        """
        Decompose time series into trend + seasonal + residual.
        
        Additive model: x(t) = Trend(t) + Seasonal(t) + Residual(t)
        """
        n = len(data)
        
        # Trend: centered moving average
        trend = TimeSeriesAnalysis.moving_average(data, period)
        # Pad to match original length
        pad_size = (n - len(trend)) // 2
        trend = np.pad(trend, (pad_size, n - len(trend) - pad_size), 
                      mode='edge')
        
        # Detrended
        detrended = data - trend
        
        # Seasonal: average for each period position
        seasonal = np.zeros(n)
        for i in range(period):
            indices = range(i, n, period)
            seasonal[indices] = np.mean(detrended[indices])
        
        # Residual
        residual = data - trend - seasonal
        
        return trend, seasonal, residual
    
    @staticmethod
    def forecast_with_trend_and_seasonality(historical_data, period, n_forecast):
        """
        Simple forecast using trend and seasonality.
        """
        # Decompose
        trend, seasonal, _ = TimeSeriesAnalysis.seasonal_decomposition(
            historical_data, period
        )
        
        # Extrapolate trend (linear)
        x = np.arange(len(trend))
        coeffs = np.polyfit(x, trend, deg=1)
        trend_forecast = np.polyval(coeffs, 
                                    np.arange(len(trend), len(trend) + n_forecast))
        
        # Repeat seasonal pattern
        seasonal_forecast = np.tile(seasonal[:period], 
                                   int(np.ceil(n_forecast / period)))[:n_forecast]
        
        # Combined forecast
        forecast = trend_forecast + seasonal_forecast
        
        return forecast

# Example: Website traffic forecasting
np.random.seed(42)

# Generate synthetic traffic data with trend and weekly seasonality
days = 365
t = np.arange(days)

# Trend: growing from 1000 to 2000 users/day
trend = 1000 + 1000 * (t / days)

# Weekly seasonality (lower on weekends)
weekly_pattern = np.array([1.0, 1.1, 1.1, 1.0, 1.0, 0.7, 0.6])  # Mon-Sun
seasonality = np.tile(weekly_pattern, days // 7 + 1)[:days]
seasonal_component = 300 * (seasonality - seasonality.mean())

# Noise
noise = np.random.normal(0, 50, days)

# Combined
traffic = trend + seasonal_component + noise

# Analyze
print("Time Series Analysis: Website Traffic")
print("=" * 60)

# Moving average (smooth weekly fluctuations)
ma_7 = TimeSeriesAnalysis.moving_average(traffic, window_size=7)
print(f"7-day moving average (last 3 days): {ma_7[-3:]}")

# Exponential smoothing
smoothed = TimeSeriesAnalysis.exponential_smoothing(traffic, alpha=0.2)
print(f"\nExponentially smoothed (last 3 days): {smoothed[-3:]}")

# Decomposition
trend_comp, seasonal_comp, residual_comp = TimeSeriesAnalysis.seasonal_decomposition(
    traffic, period=7
)

print(f"\nSeasonal decomposition:")
print(f"  Trend (last week avg): {trend_comp[-7:].mean():.0f}")
print(f"  Seasonal range: [{seasonal_comp.min():.0f}, {seasonal_comp.max():.0f}]")
print(f"  Residual std: {residual_comp.std():.1f}")

# Forecast next 14 days
forecast = TimeSeriesAnalysis.forecast_with_trend_and_seasonality(
    traffic, period=7, n_forecast=14
)

print(f"\n14-day forecast:")
day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
for i, value in enumerate(forecast):
    day_name = day_names[i % 7]
    print(f"  Day {i+1} ({day_name}): {value:.0f} users")
```

### 17.3.2 Feature Engineering

**Theory:**

Feature engineering: transforming raw data into features that better represent the underlying problem for ML models.

**Techniques:**
- **Scaling**: Normalization, standardization
- **Encoding**: One-hot, label, target encoding
- **Binning**: Convert continuous to categorical
- **Interactions**: Combine features (x₁ * x₂)
- **Temporal**: Extract hour, day, month from timestamps
- **Aggregations**: Rolling statistics, group-by operations

**WHY it matters:**

1. **Model Performance**: Good features → better predictions
2. **Training Speed**: Proper scaling → faster convergence
3. **Interpretability**: Engineered features can be more meaningful
4. **Domain Knowledge**: Encode expertise into features
5. **Data Efficiency**: Better features need less data

**Example - Feature Engineering:**

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

class FeatureEngineering:
    """
    Common feature engineering techniques.
    """
    
    @staticmethod
    def create_temporal_features(timestamps):
        """
        Extract temporal features from timestamps.
        
        Useful for: time-dependent patterns (hourly load, seasonal trends)
        """
        df = pd.DataFrame({'timestamp': pd.to_datetime(timestamps)})
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_business_hours'] = df['hour'].between(9, 17).astype(int)
        
        # Cyclical encoding (preserves continuity)
        # Hour 23 and hour 0 should be close
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        return df
    
    @staticmethod
    def create_interaction_features(X):
        """
        Create interaction features (products of existing features).
        
        Captures non-linear relationships.
        Example: price * quantity → total_value
        """
        interactions = {}
        feature_names = list(X.columns)
        
        for i in range(len(feature_names)):
            for j in range(i+1, len(feature_names)):
                name1, name2 = feature_names[i], feature_names[j]
                interactions[f'{name1}_x_{name2}'] = X[name1] * X[name2]
        
        return pd.DataFrame(interactions)
    
    @staticmethod
    def create_aggregation_features(df, group_col, agg_col):
        """
        Create group-wise aggregation features.
        
        Example: average purchase amount per user
        """
        agg_features = df.groupby(group_col)[agg_col].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).add_prefix(f'{agg_col}_')
        
        return df.merge(agg_features, left_on=group_col, right_index=True)
    
    @staticmethod
    def bin_continuous_feature(values, n_bins=5):
        """
        Convert continuous feature to categorical bins.
        
        Useful for: non-linear relationships, interpretability
        """
        bins = pd.qcut(values, q=n_bins, labels=False, duplicates='drop')
        return bins

# Example: E-commerce dataset
np.random.seed(42)

# Generate synthetic data
n_samples = 1000
data = {
    'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
    'user_id': np.random.randint(1, 100, n_samples),
    'page_load_time': np.random.lognormal(1, 0.5, n_samples),
    'num_items_viewed': np.random.poisson(5, n_samples),
    'session_duration': np.random.exponential(300, n_samples),
    'purchased': np.random.binomial(1, 0.1, n_samples)
}
df = pd.DataFrame(data)

print("Feature Engineering Example")
print("=" * 60)
print(f"Original features: {list(df.columns)}")
print(f"Original shape: {df.shape}")

# 1. Temporal features
temporal_features = FeatureEngineering.create_temporal_features(df['timestamp'])
df = pd.concat([df, temporal_features.drop('timestamp', axis=1)], axis=1)

print(f"\nAfter temporal features: {df.shape[1]} features")
print(f"New features: {list(temporal_features.columns)}")

# 2. Binning (discretize continuous features)
df['load_time_bin'] = FeatureEngineering.bin_continuous_feature(
    df['page_load_time'], n_bins=3
)

# 3. Aggregations (user-level features)
df = FeatureEngineering.create_aggregation_features(
    df, group_col='user_id', agg_col='session_duration'
)

print(f"\nAfter aggregations: {df.shape[1]} features")

# 4. Interaction features
interaction_df = FeatureEngineering.create_interaction_features(
    df[['num_items_viewed', 'session_duration']]
)
df = pd.concat([df, interaction_df], axis=1)

print(f"\nFinal shape: {df.shape}")
print(f"\nSample of engineered features:")
print(df[['hour', 'is_weekend', 'hour_sin', 'load_time_bin', 
         'session_duration_mean']].head())

# 5. Scaling (for ML models)
numerical_features = ['page_load_time', 'num_items_viewed', 'session_duration']
scaler = StandardScaler()
df[numerical_features] = scaler.fit_transform(df[numerical_features])

print(f"\nScaled features (mean≈0, std≈1):")
print(df[numerical_features].describe())
```

### 17.3.3 Bias-Variance Tradeoff

**Theory:**

Total error = Bias² + Variance + Irreducible Error

- **Bias**: Error from incorrect assumptions (underfitting)
  - Simple models (linear regression on non-linear data)
  - High bias → systematic errors
  
- **Variance**: Error from sensitivity to training data (overfitting)
  - Complex models (deep neural nets on small data)
  - High variance → model doesn't generalize

**Goal**: Find sweet spot that minimizes total error

**WHY it matters:**

1. **Model Selection**: Choose model complexity appropriately
2. **Regularization**: Trade variance for bias (L1, L2, dropout)
3. **Ensemble Methods**: Reduce variance (bagging) or bias (boosting)
4. **Debugging ML**: Diagnose underfitting vs overfitting
5. **Data Requirements**: High-variance models need more data

**Example - Bias-Variance Tradeoff:**

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def generate_data(n_samples=100):
    """
    Generate synthetic data: y = x² + noise
    """
    np.random.seed(42)
    X = np.random.uniform(-3, 3, n_samples)
    y = X**2 + np.random.normal(0, 2, n_samples)
    return X.reshape(-1, 1), y

def fit_polynomial(X_train, y_train, X_test, y_test, degree):
    """
    Fit polynomial of given degree and compute train/test error.
    """
    # Transform features
    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)
    
    # Fit model
    model = LinearRegression()
    model.fit(X_train_poly, y_train)
    
    # Errors
    train_error = mean_squared_error(y_train, model.predict(X_train_poly))
    test_error = mean_squared_error(y_test, model.predict(X_test_poly))
    
    return model, poly, train_error, test_error

# Generate data
X_train, y_train = generate_data(100)
X_test, y_test = generate_data(100)

print("Bias-Variance Tradeoff Demonstration")
print("=" * 60)
print("True function: y = x² + noise")
print()

# Try different polynomial degrees
degrees = [1, 2, 3, 5, 10, 20]

print("Degree | Train Error | Test Error | Diagnosis")
print("-" * 60)

for degree in degrees:
    model, poly, train_err, test_err = fit_polynomial(
        X_train, y_train, X_test, y_test, degree
    )
    
    # Diagnose
    if train_err > 5 and test_err > 5:
        diagnosis = "High Bias (Underfitting)"
    elif test_err > 2 * train_err:
        diagnosis = "High Variance (Overfitting)"
    else:
        diagnosis = "Good Balance"
    
    print(f"{degree:6d} | {train_err:11.2f} | {test_err:10.2f} | {diagnosis}")

print("\nInterpretation:")
print("- Degree 1 (linear): High bias, can't capture quadratic relationship")
print("- Degree 2: Good balance, matches true function")
print("- Degree 10+: High variance, overfits training noise")
```

**Example - Regularization to Control Variance:**

```python
from sklearn.linear_model import Ridge, Lasso

def demonstrate_regularization(X_train, y_train, X_test, y_test, degree=10):
    """
    Show how regularization reduces variance in high-degree polynomial.
    """
    # High-degree polynomial (prone to overfitting)
    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)
    
    print(f"\nRegularization with degree-{degree} polynomial")
    print("=" * 60)
    
    # Different regularization strengths
    alphas = [0, 0.01, 0.1, 1.0, 10.0]
    
    print("Alpha  | Train Error | Test Error | # Non-zero Coefs")
    print("-" * 60)
    
    for alpha in alphas:
        if alpha == 0:
            model = LinearRegression()
        else:
            model = Ridge(alpha=alpha)  # L2 regularization
        
        model.fit(X_train_poly, y_train)
        
        train_err = mean_squared_error(y_train, model.predict(X_train_poly))
        test_err = mean_squared_error(y_test, model.predict(X_test_poly))
        
        non_zero = np.sum(np.abs(model.coef_) > 0.01)
        
        print(f"{alpha:6.2f} | {train_err:11.2f} | {test_err:10.2f} | {non_zero:16d}")
    
    print("\nObservation:")
    print("- α=0: No regularization, overfits (low train error, high test error)")
    print("- α=0.1-1.0: Good balance")
    print("- α=10: High regularization, underfits (high train error)")

demonstrate_regularization(X_train, y_train, X_test, y_test, degree=10)
```

**Connections to Other Topics:**

- **Part 18 (ML)**: Core concept for all ML models
- **Part 10 (Testing)**: Cross-validation to estimate generalization
- **Part 11 (Performance)**: Model complexity vs inference speed
- **Part 15 (Engineering Judgment)**: Knowing when to add complexity

---

*[Continuing with Parts 18-22 in the next section...]*

# PART 18: MACHINE LEARNING & AI FUNDAMENTALS

Machine learning enables systems to learn from data without explicit programming. For modern engineers, understanding ML is essential for building intelligent features, data products, and automation.

## 18.1 Supervised Learning

Supervised learning trains models on labeled data: (input, correct output) pairs.

### 18.1.1 Classification vs Regression

**Theory:**

- **Classification**: Predict discrete labels (spam/not spam, cat/dog)
  - Output: Class probability P(y|x)
  - Loss: Cross-entropy
  
- **Regression**: Predict continuous values (price, temperature)
  - Output: Real number ŷ
  - Loss: Mean squared error

**WHY it matters:**

1. **Product Features**: Recommendation systems, fraud detection
2. **Operations**: Anomaly detection, capacity prediction
3. **Business**: Customer churn prediction, demand forecasting
4. **Security**: Malware detection, intrusion detection
5. **User Experience**: Personalization, search ranking

**Example - Logistic Regression (Classification):**

```python
import numpy as np

class LogisticRegression:
    """
    Binary classification using logistic regression.
    
    Model: P(y=1|x) = σ(wᵀx + b)
    where σ(z) = 1/(1 + e⁻ᶻ) is the sigmoid function
    
    Loss: Binary cross-entropy
    L = -[y log(ŷ) + (1-y) log(1-ŷ)]
    """
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.lr = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
    
    def sigmoid(self, z):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    
    def fit(self, X, y):
        """
        Train using gradient descent.
        
        Gradients:
        ∂L/∂w = (1/n) Xᵀ(ŷ - y)
        ∂L/∂b = (1/n) Σ(ŷ - y)
        """
        n_samples, n_features = X.shape
        
        # Initialize parameters
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        # Gradient descent
        for i in range(self.n_iterations):
            # Forward pass
            linear_pred = X @ self.weights + self.bias
            y_pred = self.sigmoid(linear_pred)
            
            # Compute gradients
            dw = (1/n_samples) * (X.T @ (y_pred - y))
            db = (1/n_samples) * np.sum(y_pred - y)
            
            # Update parameters
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
            
            # Log loss every 100 iterations
            if i % 100 == 0:
                loss = self.binary_cross_entropy(y, y_pred)
                print(f"Iteration {i}: Loss = {loss:.4f}")
    
    def binary_cross_entropy(self, y_true, y_pred):
        """
        Binary cross-entropy loss.
        Measures how well predicted probabilities match true labels.
        """
        epsilon = 1e-15  # Avoid log(0)
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        return -np.mean(y_true * np.log(y_pred) + 
                       (1 - y_true) * np.log(1 - y_pred))
    
    def predict_proba(self, X):
        """Predict probabilities"""
        linear_pred = X @ self.weights + self.bias
        return self.sigmoid(linear_pred)
    
    def predict(self, X, threshold=0.5):
        """Predict class labels"""
        return (self.predict_proba(X) >= threshold).astype(int)

# Example: Email spam classification
np.random.seed(42)

# Generate synthetic data
# Features: [email_length, num_links, num_capitals]
X_spam = np.random.randn(500, 3) @ np.array([[1, 2, 3]]).T + \
         np.array([100, 10, 50])
X_ham = np.random.randn(500, 3) @ np.array([[1, 1, 1]]).T + \
        np.array([50, 2, 10])

X = np.vstack([X_spam, X_ham])
y = np.hstack([np.ones(500), np.zeros(500)])

# Shuffle
indices = np.random.permutation(len(X))
X, y = X[indices], y[indices]

# Normalize features
X = (X - X.mean(axis=0)) / X.std(axis=0)

# Split train/test
split = 800
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Train
model = LogisticRegression(learning_rate=0.1, n_iterations=500)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = np.mean(y_pred == y_test)

print(f"\nTest Accuracy: {accuracy:.2%}")

# Confusion matrix
tp = np.sum((y_pred == 1) & (y_test == 1))
tn = np.sum((y_pred == 0) & (y_test == 0))
fp = np.sum((y_pred == 1) & (y_test == 0))
fn = np.sum((y_pred == 0) & (y_test == 1))

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\nConfusion Matrix:")
print(f"  True Positives: {tp}, False Positives: {fp}")
print(f"  False Negatives: {fn}, True Negatives: {tn}")
print(f"Precision: {precision:.2%} (of predicted spam, how many are actually spam)")
print(f"Recall: {recall:.2%} (of actual spam, how many did we catch)")
print(f"F1 Score: {f1:.2%} (harmonic mean of precision and recall)")
```

### 18.1.2 Decision Trees and Random Forests

**Theory:**

**Decision Tree**: Recursively split data based on features to create if-then-else rules.

Splitting criterion:
- **Gini Impurity**: 1 - Σ pᵢ² (classification)
- **Entropy**: -Σ pᵢ log(pᵢ) (classification)
- **MSE**: Mean squared error (regression)

**Random Forest**: Ensemble of decision trees
- Bootstrap aggregating (bagging)
- Random feature subset at each split
- Reduces variance compared to single tree

**WHY it matters:**

1. **Interpretability**: Easy to visualize and explain
2. **Feature Importance**: Understand which features matter most
3. **Non-linear**: Captures complex relationships
4. **Mixed Data**: Handles categorical and numerical features
5. **Robust**: Works well without heavy feature engineering

**Example - Decision Tree from Scratch:**

```python
import numpy as np
from collections import Counter

class DecisionTreeNode:
    """Node in a decision tree"""
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature      # Feature to split on
        self.threshold = threshold  # Threshold value
        self.left = left           # Left subtree
        self.right = right         # Right subtree
        self.value = value         # Leaf value (for prediction)

class DecisionTreeClassifier:
    """
    Binary decision tree classifier using Gini impurity.
    
    Algorithm (recursive):
    1. Find best split (feature, threshold) to minimize impurity
    2. Split data into left and right
    3. Recursively build left and right subtrees
    4. Stop when max_depth reached or node is pure
    """
    
    def __init__(self, max_depth=10, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
    
    def gini_impurity(self, y):
        """
        Gini impurity: 1 - Σ pᵢ²
        
        0 = pure (all same class)
        0.5 = maximum impurity (binary, 50/50 split)
        """
        if len(y) == 0:
            return 0
        
        counts = Counter(y)
        impurity = 1.0
        for count in counts.values():
            prob = count / len(y)
            impurity -= prob ** 2
        
        return impurity
    
    def information_gain(self, y, y_left, y_right):
        """
        Information gain = impurity before split - weighted impurity after split
        """
        n = len(y)
        n_left, n_right = len(y_left), len(y_right)
        
        if n_left == 0 or n_right == 0:
            return 0
        
        parent_impurity = self.gini_impurity(y)
        child_impurity = (n_left / n * self.gini_impurity(y_left) +
                         n_right / n * self.gini_impurity(y_right))
        
        return parent_impurity - child_impurity
    
    def best_split(self, X, y):
        """
        Find best feature and threshold to split on.
        
        Try all features and all possible thresholds (midpoints).
        """
        best_gain = -1
        best_feature = None
        best_threshold = None
        
        n_features = X.shape[1]
        
        for feature in range(n_features):
            thresholds = np.unique(X[:, feature])
            
            for threshold in thresholds:
                # Split data
                left_mask = X[:, feature] <= threshold
                right_mask = ~left_mask
                
                y_left = y[left_mask]
                y_right = y[right_mask]
                
                # Calculate information gain
                gain = self.information_gain(y, y_left, y_right)
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        
        return best_feature, best_threshold, best_gain
    
    def build_tree(self, X, y, depth=0):
        """Recursively build decision tree"""
        n_samples, n_features = X.shape
        n_classes = len(np.unique(y))
        
        # Stopping criteria
        if (depth >= self.max_depth or 
            n_samples < self.min_samples_split or 
            n_classes == 1):
            # Leaf node: return most common class
            leaf_value = Counter(y).most_common(1)[0][0]
            return DecisionTreeNode(value=leaf_value)
        
        # Find best split
        feature, threshold, gain = self.best_split(X, y)
        
        if gain == 0:
            # No good split found
            leaf_value = Counter(y).most_common(1)[0][0]
            return DecisionTreeNode(value=leaf_value)
        
        # Split data
        left_mask = X[:, feature] <= threshold
        right_mask = ~left_mask
        
        # Recursively build subtrees
        left_subtree = self.build_tree(X[left_mask], y[left_mask], depth + 1)
        right_subtree = self.build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return DecisionTreeNode(feature, threshold, left_subtree, right_subtree)
    
    def fit(self, X, y):
        """Build the tree"""
        self.root = self.build_tree(X, y)
    
    def predict_sample(self, x, node):
        """Traverse tree to predict single sample"""
        if node.value is not None:
            return node.value
        
        if x[node.feature] <= node.threshold:
            return self.predict_sample(x, node.left)
        else:
            return self.predict_sample(x, node.right)
    
    def predict(self, X):
        """Predict multiple samples"""
        return np.array([self.predict_sample(x, self.root) for x in X])

# Example: Iris classification
from sklearn.datasets import load_iris

iris = load_iris()
X, y = iris.data, iris.target

# Use only first 2 classes for binary classification
mask = y < 2
X, y = X[mask], y[mask]

# Shuffle and split
indices = np.random.permutation(len(X))
X, y = X[indices], y[indices]

split = 80
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Train decision tree
tree = DecisionTreeClassifier(max_depth=3)
tree.fit(X_train, y_train)

# Evaluate
y_pred = tree.predict(X_test)
accuracy = np.mean(y_pred == y_test)

print("Decision Tree Classifier")
print(f"Test Accuracy: {accuracy:.2%}")
```

### 18.1.3 Neural Networks Architecture

**Theory:**

Neural networks: composed of layers of interconnected neurons.

**Architecture:**
- **Input layer**: Raw features
- **Hidden layers**: Learned representations
- **Output layer**: Predictions

**Neuron computation:**
```
z = Σ(wᵢxᵢ) + b
a = σ(z)
```

**Common activations:**
- **ReLU**: max(0, x) - most common for hidden layers
- **Sigmoid**: 1/(1+e⁻ˣ) - binary classification output
- **Softmax**: eˣⁱ/Σeˣʲ - multi-class classification output
- **Tanh**: (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) - alternative to sigmoid

**Training:** Backpropagation + gradient descent

**WHY it matters:**

1. **Universal Approximator**: Can learn any continuous function
2. **Feature Learning**: Automatically discovers useful representations
3. **State-of-the-Art**: Best performance on many tasks
4. **Transfer Learning**: Pre-trained models as starting points
5. **Deep Learning**: Foundation for CNNs, RNNs, Transformers

**Example - Multi-Layer Neural Network:**

```python
import numpy as np

class NeuralNetwork:
    """
    Feedforward neural network with arbitrary architecture.
    
    Supports:
    - Multiple hidden layers
    - Different activation functions
    - Mini-batch gradient descent
    - L2 regularization
    """
    
    def __init__(self, layer_sizes, learning_rate=0.01, reg_lambda=0.01):
        """
        layer_sizes: list of layer dimensions
        Example: [784, 128, 64, 10] for MNIST
        """
        self.layer_sizes = layer_sizes
        self.lr = learning_rate
        self.reg_lambda = reg_lambda
        
        # Initialize weights (He initialization for ReLU)
        self.weights = []
        self.biases = []
        
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * \
                np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i+1]))
            
            self.weights.append(w)
            self.biases.append(b)
    
    def relu(self, z):
        """ReLU activation"""
        return np.maximum(0, z)
    
    def relu_derivative(self, z):
        """ReLU derivative"""
        return (z > 0).astype(float)
    
    def softmax(self, z):
        """Softmax activation (for output layer)"""
        exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)
    
    def forward(self, X):
        """
        Forward pass through network.
        
        Returns:
            output: final predictions
            cache: intermediate values for backprop
        """
        cache = {'A0': X}
        A = X
        
        # Hidden layers with ReLU
        for i in range(len(self.weights) - 1):
            Z = A @ self.weights[i] + self.biases[i]
            A = self.relu(Z)
            
            cache[f'Z{i+1}'] = Z
            cache[f'A{i+1}'] = A
        
        # Output layer with softmax
        i = len(self.weights) - 1
        Z = A @ self.weights[i] + self.biases[i]
        A = self.softmax(Z)
        
        cache[f'Z{i+1}'] = Z
        cache[f'A{i+1}'] = A
        
        return A, cache
    
    def compute_loss(self, y_true, y_pred):
        """
        Cross-entropy loss with L2 regularization.
        
        L = -Σ yᵢ log(ŷᵢ) + λ/2 Σ‖W‖²
        """
        m = y_true.shape[0]
        
        # Cross-entropy
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        cross_entropy = -np.sum(y_true * np.log(y_pred)) / m
        
        # L2 regularization
        l2_reg = 0
        for w in self.weights:
            l2_reg += np.sum(w ** 2)
        l2_reg *= self.reg_lambda / (2 * m)
        
        return cross_entropy + l2_reg
    
    def backward(self, y_true, cache):
        """
        Backpropagation to compute gradients.
        
        Uses chain rule to propagate errors backward.
        """
        m = y_true.shape[0]
        L = len(self.weights)
        
        grads_w = [None] * L
        grads_b = [None] * L
        
        # Output layer gradient
        dA = cache[f'A{L}'] - y_true
        
        # Backpropagate through layers
        for i in reversed(range(L)):
            # Gradient w.r.t. weights and biases
            A_prev = cache[f'A{i}']
            
            grads_w[i] = (A_prev.T @ dA) / m + (self.reg_lambda / m) * self.weights[i]
            grads_b[i] = np.sum(dA, axis=0, keepdims=True) / m
            
            # Gradient w.r.t. previous activation
            if i > 0:
                dA = (dA @ self.weights[i].T) * self.relu_derivative(cache[f'Z{i}'])
        
        return grads_w, grads_b
    
    def train(self, X, y, epochs=100, batch_size=32, verbose=True):
        """
        Train network using mini-batch gradient descent.
        
        y should be one-hot encoded
        """
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            # Mini-batch training
            for i in range(0, n_samples, batch_size):
                X_batch = X_shuffled[i:i+batch_size]
                y_batch = y_shuffled[i:i+batch_size]
                
                # Forward pass
                y_pred, cache = self.forward(X_batch)
                
                # Backward pass
                grads_w, grads_b = self.backward(y_batch, cache)
                
                # Update parameters
                for j in range(len(self.weights)):
                    self.weights[j] -= self.lr * grads_w[j]
                    self.biases[j] -= self.lr * grads_b[j]
            
            # Compute epoch loss
            if verbose and epoch % 10 == 0:
                y_pred, _ = self.forward(X)
                loss = self.compute_loss(y, y_pred)
                
                # Accuracy
                y_pred_classes = np.argmax(y_pred, axis=1)
                y_true_classes = np.argmax(y, axis=1)
                accuracy = np.mean(y_pred_classes == y_true_classes)
                
                print(f"Epoch {epoch}: Loss = {loss:.4f}, Accuracy = {accuracy:.2%}")
    
    def predict(self, X):
        """Predict class labels"""
        y_pred, _ = self.forward(X)
        return np.argmax(y_pred, axis=1)

# Example: Multi-class classification
from sklearn.datasets import load_digits
from sklearn.preprocessing import OneHotEncoder

# Load data
digits = load_digits()
X, y = digits.data, digits.target

# Normalize
X = X / 16.0

# One-hot encode labels
encoder = OneHotEncoder(sparse_output=False)
y_onehot = encoder.fit_transform(y.reshape(-1, 1))

# Split
split = 1200
X_train, X_test = X[:split], X[split:]
y_train, y_test = y_onehot[:split], y_onehot[split:]
y_test_labels = y[split:]

# Create and train network
nn = NeuralNetwork(
    layer_sizes=[64, 32, 16, 10],  # Input=64 (8x8 image), Output=10 (digits)
    learning_rate=0.1,
    reg_lambda=0.01
)

print("Training Neural Network on Digits Dataset")
print("=" * 60)
nn.train(X_train, y_train, epochs=100, batch_size=32, verbose=True)

# Evaluate
y_pred = nn.predict(X_test)
accuracy = np.mean(y_pred == y_test_labels)
print(f"\nTest Accuracy: {accuracy:.2%}")
```

**Connections to Other Topics:**

- **Part 16.2 (Calculus)**: Backpropagation is chain rule
- **Part 16.1 (Linear Algebra)**: Layers are matrix multiplications
- **Part 17 (Statistics)**: Probabilistic predictions, loss functions
- **Part 11 (Performance)**: Model serving, inference optimization

---

## 18.2 Unsupervised Learning

Unsupervised learning finds patterns in unlabeled data.

### 18.2.1 Clustering Algorithms

**Theory:**

Clustering: group similar data points together.

**K-Means:**
1. Initialize k cluster centers randomly
2. Assign each point to nearest center
3. Update centers to mean of assigned points
4. Repeat until convergence

Objective: minimize within-cluster variance
```
J = Σᵢ Σₓ∈Cᵢ ‖x - μᵢ‖²
```

**Other algorithms:**
- **Hierarchical**: Build tree of clusters (agglomerative/divisive)
- **DBSCAN**: Density-based, finds arbitrary shapes
- **Gaussian Mixture Models**: Probabilistic soft clustering

**WHY it matters:**

1. **Customer Segmentation**: Group users by behavior
2. **Anomaly Detection**: Outliers don't fit any cluster
3. **Data Compression**: Replace points with cluster centers
4. **Feature Engineering**: Cluster membership as feature
5. **Exploratory Analysis**: Discover hidden structure

**Example - K-Means from Scratch:**

```python
import numpy as np

class KMeans:
    """
    K-Means clustering algorithm.
    
    Minimizes within-cluster sum of squared distances.
    """
    
    def __init__(self, n_clusters=3, max_iterations=100, tol=1e-4):
        self.n_clusters = n_clusters
        self.max_iterations = max_iterations
        self.tol = tol
        self.centroids = None
        self.labels = None
    
    def initialize_centroids(self, X):
        """
        K-Means++ initialization (better than random).
        
        Choose centers that are far apart from each other.
        """
        n_samples = X.shape[0]
        centroids = []
        
        # First center: random
        centroids.append(X[np.random.randint(n_samples)])
        
        # Subsequent centers: weighted by distance to existing centers
        for _ in range(1, self.n_clusters):
            # Distance to nearest existing centroid
            distances = np.array([
                min([np.linalg.norm(x - c) for c in centroids])
                for x in X
            ])
            
            # Choose next center with probability proportional to distance²
            probabilities = distances ** 2
            probabilities /= probabilities.sum()
            
            next_centroid = X[np.random.choice(n_samples, p=probabilities)]
            centroids.append(next_centroid)
        
        return np.array(centroids)
    
    def assign_clusters(self, X):
        """Assign each point to nearest centroid"""
        distances = np.array([
            [np.linalg.norm(x - c) for c in self.centroids]
            for x in X
        ])
        return np.argmin(distances, axis=1)
    
    def update_centroids(self, X, labels):
        """Update centroids to mean of assigned points"""
        centroids = np.zeros((self.n_clusters, X.shape[1]))
        
        for k in range(self.n_clusters):
            cluster_points = X[labels == k]
            if len(cluster_points) > 0:
                centroids[k] = cluster_points.mean(axis=0)
            else:
                # Empty cluster: reinitialize
                centroids[k] = X[np.random.randint(len(X))]
        
        return centroids
    
    def compute_inertia(self, X, labels):
        """Compute within-cluster sum of squared distances"""
        inertia = 0
        for k in range(self.n_clusters):
            cluster_points = X[labels == k]
            if len(cluster_points) > 0:
                inertia += np.sum((cluster_points - self.centroids[k]) ** 2)
        return inertia
    
    def fit(self, X):
        """Run K-Means algorithm"""
        # Initialize
        self.centroids = self.initialize_centroids(X)
        
        for iteration in range(self.max_iterations):
            # Assign clusters
            labels = self.assign_clusters(X)
            
            # Update centroids
            new_centroids = self.update_centroids(X, labels)
            
            # Check convergence
            centroid_shift = np.linalg.norm(new_centroids - self.centroids)
            self.centroids = new_centroids
            
            if iteration % 10 == 0:
                inertia = self.compute_inertia(X, labels)
                print(f"Iteration {iteration}: Inertia = {inertia:.2f}, "
                      f"Centroid shift = {centroid_shift:.6f}")
            
            if centroid_shift < self.tol:
                print(f"Converged at iteration {iteration}")
                break
        
        self.labels = self.assign_clusters(X)
        return self
    
    def predict(self, X):
        """Assign new points to clusters"""
        return self.assign_clusters(X)

# Example: Customer segmentation
np.random.seed(42)

# Generate synthetic customer data
# Features: [purchase_frequency, average_order_value, recency_days]

# Cluster 1: High-value frequent customers
cluster1 = np.random.randn(100, 3) @ np.diag([2, 5, 3]) + [20, 100, 5]

# Cluster 2: Low-value frequent customers
cluster2 = np.random.randn(100, 3) @ np.diag([2, 3, 3]) + [15, 30, 10]

# Cluster 3: Inactive customers
cluster3 = np.random.randn(100, 3) @ np.diag([3, 4, 5]) + [5, 50, 90]

X = np.vstack([cluster1, cluster2, cluster3])

# Normalize features
X = (X - X.mean(axis=0)) / X.std(axis=0)

# Cluster
kmeans = KMeans(n_clusters=3, max_iterations=100)
kmeans.fit(X)

# Analyze clusters
print("\nCluster Analysis:")
for k in range(3):
    cluster_points = X[kmeans.labels == k]
    print(f"\nCluster {k}: {len(cluster_points)} customers")
    print(f"  Centroid: {kmeans.centroids[k]}")
    print(f"  Size: {len(cluster_points)}")
    
    # Interpret (denormalize for readability)
    # Note: This is simplified, real analysis would denormalize properly
    if kmeans.centroids[k][0] > 0.5:
        print("  → High purchase frequency")
    if kmeans.centroids[k][1] > 0.5:
        print("  → High order value")
    if kmeans.centroids[k][2] < -0.5:
        print("  → Recently active")
```

### 18.2.2 Dimensionality Reduction

**Theory:**

Reduce number of features while preserving information.

**PCA (Principal Component Analysis):**
- Linear transformation to uncorrelated components
- Components ordered by variance explained
- Uses eigenvectors of covariance matrix

**t-SNE (t-Distributed Stochastic Neighbor Embedding):**
- Non-linear dimensionality reduction
- Preserves local structure (neighborhoods)
- Great for visualization (2D/3D)

**Autoencoders:**
- Neural network learns compressed representation
- Encoder: high-dim → low-dim
- Decoder: low-dim → high-dim

**WHY it matters:**

1. **Visualization**: Plot high-dimensional data in 2D/3D
2. **Compression**: Reduce storage/computation
3. **Noise Reduction**: Keep signal, remove noise
4. **Feature Extraction**: Pre-processing for ML
5. **Curse of Dimensionality**: Many algorithms struggle in high dimensions

**Example - PCA (covered in Part 16.1):**

Already covered in Part 16.1.3. See that section for implementation.

### 18.2.3 Anomaly Detection

**Theory:**

Identify data points that deviate significantly from normal behavior.

**Approaches:**
1. **Statistical**: Points beyond k standard deviations
2. **Isolation Forest**: Anomalies easier to isolate (fewer splits)
3. **One-Class SVM**: Learn boundary around normal data
4. **Autoencoders**: High reconstruction error for anomalies

**WHY it matters:**

1. **Fraud Detection**: Unusual transactions
2. **System Monitoring**: Performance anomalies
3. **Security**: Intrusion detection
4. **Quality Control**: Defective products
5. **Health Monitoring**: Abnormal vital signs

**Example - Isolation Forest Concept:**

```python
import numpy as np

class IsolationTree:
    """
    Single isolation tree for anomaly detection.
    
    Principle: Anomalies are easier to isolate (require fewer splits).
    """
    
    def __init__(self, max_depth=10):
        self.max_depth = max_depth
        self.split_feature = None
        self.split_value = None
        self.left = None
        self.right = None
        self.size = 0
    
    def fit(self, X, depth=0):
        """Build isolation tree"""
        self.size = len(X)
        
        # Stop if max depth or pure node
        if depth >= self.max_depth or len(X) <= 1:
            return self
        
        # Random feature and split
        n_features = X.shape[1]
        self.split_feature = np.random.randint(0, n_features)
        
        feature_values = X[:, self.split_feature]
        min_val, max_val = feature_values.min(), feature_values.max()
        
        if min_val == max_val:
            return self
        
        self.split_value = np.random.uniform(min_val, max_val)
        
        # Split data
        left_mask = X[:, self.split_feature] < self.split_value
        right_mask = ~left_mask
        
        # Recursively build subtrees
        if np.any(left_mask):
            self.left = IsolationTree(self.max_depth)
            self.left.fit(X[left_mask], depth + 1)
        
        if np.any(right_mask):
            self.right = IsolationTree(self.max_depth)
            self.right.fit(X[right_mask], depth + 1)
        
        return self
    
    def path_length(self, x, depth=0):
        """
        Compute path length for a single point.
        
        Shorter path → easier to isolate → more likely anomaly
        """
        # Leaf node
        if self.split_feature is None:
            # Adjustment for unsplit nodes
            return depth + self._average_path_length(self.size)
        
        # Traverse tree
        if x[self.split_feature] < self.split_value:
            if self.left is not None:
                return self.left.path_length(x, depth + 1)
        else:
            if self.right is not None:
                return self.right.path_length(x, depth + 1)
        
        return depth
    
    def _average_path_length(self, n):
        """Average path length in BST of n nodes (for normalization)"""
        if n <= 1:
            return 0
        return 2 * (np.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n

class IsolationForest:
    """
    Isolation Forest for anomaly detection.
    
    Ensemble of isolation trees.
    """
    
    def __init__(self, n_estimators=100, max_samples=256, max_depth=10):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.max_depth = max_depth
        self.trees = []
    
    def fit(self, X):
        """Build forest"""
        n_samples = len(X)
        
        for i in range(self.n_estimators):
            # Sample subset
            sample_size = min(self.max_samples, n_samples)
            indices = np.random.choice(n_samples, sample_size, replace=False)
            X_sample = X[indices]
            
            # Build tree
            tree = IsolationTree(max_depth=self.max_depth)
            tree.fit(X_sample)
            self.trees.append(tree)
            
            if (i + 1) % 20 == 0:
                print(f"Built {i + 1}/{self.n_estimators} trees")
        
        return self
    
    def anomaly_score(self, X):
        """
        Compute anomaly score for each point.
        
        Score ∈ [0, 1]
        - Close to 1: anomaly
        - Close to 0: normal
        - Around 0.5: no clear distinction
        """
        avg_path_lengths = np.zeros(len(X))
        
        for tree in self.trees:
            for i, x in enumerate(X):
                avg_path_lengths[i] += tree.path_length(x)
        
        avg_path_lengths /= self.n_estimators
        
        # Normalize (c is average path length in BST)
        c = 2 * (np.log(self.max_samples - 1) + 0.5772156649) - \
            2 * (self.max_samples - 1) / self.max_samples
        
        scores = 2 ** (-avg_path_lengths / c)
        return scores
    
    def predict(self, X, threshold=0.6):
        """
        Predict anomalies.
        
        Returns: -1 for anomalies, 1 for normal points
        """
        scores = self.anomaly_score(X)
        return np.where(scores >= threshold, -1, 1)

# Example: Network traffic anomaly detection
np.random.seed(42)

# Normal traffic: low latency, moderate throughput
normal_traffic = np.random.randn(1000, 2) @ np.diag([10, 20]) + [50, 100]

# Anomalies: DDoS (high throughput), slow requests (high latency)
ddos = np.random.randn(20, 2) @ np.diag([15, 30]) + [60, 500]
slow = np.random.randn(20, 2) @ np.diag([20, 15]) + [200, 120]

# Combine
X_normal = normal_traffic
X_anomalies = np.vstack([ddos, slow])
X = np.vstack([X_normal, X_anomalies])

# True labels (for evaluation)
y_true = np.hstack([np.ones(len(X_normal)), -np.ones(len(X_anomalies))])

# Train isolation forest (on normal data ideally, but here we use all)
print("Training Isolation Forest")
print("=" * 60)
iforest = IsolationForest(n_estimators=100, max_samples=256)
iforest.fit(X_normal)  # Train only on normal data

# Detect anomalies
scores = iforest.anomaly_score(X)
predictions = iforest.predict(X, threshold=0.55)

# Evaluate
tp = np.sum((predictions == -1) & (y_true == -1))
fp = np.sum((predictions == -1) & (y_true == 1))
tn = np.sum((predictions == 1) & (y_true == 1))
fn = np.sum((predictions == 1) & (y_true == -1))

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0

print(f"\nAnomaly Detection Results:")
print(f"True Positives: {tp}, False Positives: {fp}")
print(f"False Negatives: {fn}, True Negatives: {tn}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")

# Show top anomalies
top_anomalies = np.argsort(scores)[-10:]
print(f"\nTop 10 anomaly scores:")
for idx in top_anomalies:
    print(f"  Sample {idx}: score={scores[idx]:.3f}, "
          f"latency={X[idx, 0]:.1f}, throughput={X[idx, 1]:.1f}")
```

**Connections to Other Topics:**

- **Part 17 (Statistics)**: Statistical anomaly detection
- **Part 12 (Monitoring)**: Anomaly detection in production
- **Part 9 (Security)**: Intrusion detection
- **Part 20 (UX)**: User segmentation

---

## 18.3 Deep Learning Concepts

### 18.3.1 Convolutional Neural Networks (CNNs)

**Theory:**

CNNs specialized for grid-like data (images, time series).

**Key operations:**
- **Convolution**: Apply filters to detect local patterns
  - Filter = small matrix (e.g., 3×3)
  - Slide across input, compute dot product
  - Learns edge detectors, textures, patterns
  
- **Pooling**: Downsample (max/average pooling)
  - Reduces spatial dimensions
  - Provides translation invariance
  
- **Fully connected**: Final layers for classification

**Architecture example:**
```
Input → Conv → ReLU → Pool → Conv → ReLU → Pool → FC → Output
```

**WHY it matters:**

1. **Computer Vision**: Image classification, object detection
2. **Medical Imaging**: Disease diagnosis from scans
3. **Autonomous Vehicles**: Scene understanding
4. **OCR**: Text recognition
5. **Video Analysis**: Action recognition

**Example - CNN Concepts:**

```python
import numpy as np

class ConvolutionalLayer:
    """
    2D convolution operation.
    
    Applies filters to input to detect local patterns.
    """
    
    def __init__(self, n_filters, filter_size, stride=1, padding=0):
        self.n_filters = n_filters
        self.filter_size = filter_size
        self.stride = stride
        self.padding = padding
        self.filters = None
        self.bias = None
    
    def initialize_filters(self, input_channels):
        """Initialize filters with He initialization"""
        self.filters = np.random.randn(
            self.n_filters, 
            input_channels, 
            self.filter_size, 
            self.filter_size
        ) * np.sqrt(2.0 / (input_channels * self.filter_size * self.filter_size))
        
        self.bias = np.zeros(self.n_filters)
    
    def convolve(self, input_region, filter_weights):
        """
        Compute convolution: element-wise multiply + sum.
        
        This is the core operation that detects patterns.
        """
        return np.sum(input_region * filter_weights)
    
    def forward(self, X):
        """
        Apply convolution to input.
        
        X shape: (batch, channels, height, width)
        Output shape: (batch, n_filters, out_height, out_width)
        """
        batch_size, channels, h_in, w_in = X.shape
        
        if self.filters is None:
            self.initialize_filters(channels)
        
        # Output dimensions
        h_out = (h_in + 2*self.padding - self.filter_size) // self.stride + 1
        w_out = (w_in + 2*self.padding - self.filter_size) // self.stride + 1
        
        # Pad input
        if self.padding > 0:
            X = np.pad(X, ((0,0), (0,0), 
                          (self.padding, self.padding), 
                          (self.padding, self.padding)), 
                      mode='constant')
        
        output = np.zeros((batch_size, self.n_filters, h_out, w_out))
        
        # Convolve each filter
        for b in range(batch_size):
            for f in range(self.n_filters):
                for i in range(h_out):
                    for j in range(w_out):
                        h_start = i * self.stride
                        w_start = j * self.stride
                        
                        # Extract region
                        region = X[b, :, 
                                 h_start:h_start+self.filter_size,
                                 w_start:w_start+self.filter_size]
                        
                        # Convolve
                        output[b, f, i, j] = self.convolve(region, self.filters[f]) + \
                                            self.bias[f]
        
        return output

class MaxPoolingLayer:
    """
    Max pooling: downsample by taking maximum in each region.
    
    Provides translation invariance and reduces computation.
    """
    
    def __init__(self, pool_size=2, stride=2):
        self.pool_size = pool_size
        self.stride = stride
    
    def forward(self, X):
        """
        Apply max pooling.
        
        X shape: (batch, channels, height, width)
        """
        batch_size, channels, h_in, w_in = X.shape
        
        h_out = (h_in - self.pool_size) // self.stride + 1
        w_out = (w_in - self.pool_size) // self.stride + 1
        
        output = np.zeros((batch_size, channels, h_out, w_out))
        
        for b in range(batch_size):
            for c in range(channels):
                for i in range(h_out):
                    for j in range(w_out):
                        h_start = i * self.stride
                        w_start = j * self.stride
                        
                        # Extract region
                        region = X[b, c,
                                 h_start:h_start+self.pool_size,
                                 w_start:w_start+self.pool_size]
                        
                        # Take maximum
                        output[b, c, i, j] = np.max(region)
        
        return output

# Example: Edge detection with convolution
print("Convolutional Neural Networks - Edge Detection")
print("=" * 60)

# Create simple image (8×8)
image = np.zeros((1, 1, 8, 8))
image[0, 0, 2:6, 3:5] = 1  # Vertical bar

print("Original image:")
print(image[0, 0])

# Edge detection filters
vertical_edge_filter = np.array([[
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1]
]])

horizontal_edge_filter = np.array([[
    [-1, -1, -1],
    [0, 0, 0],
    [1, 1, 1]
]])

# Apply vertical edge detector
conv_layer = ConvolutionalLayer(n_filters=1, filter_size=3, stride=1, padding=0)
conv_layer.filters = vertical_edge_filter.reshape(1, 1, 3, 3)
conv_layer.bias = np.array([0])

output = conv_layer.forward(image)
print("\nAfter vertical edge detection:")
print(output[0, 0])
print("→ Edges detected at boundaries of vertical bar")

# Apply pooling
pool_layer = MaxPoolingLayer(pool_size=2, stride=2)
pooled = pool_layer.forward(output)
print(f"\nAfter 2×2 max pooling:")
print(f"Shape reduced from {output.shape} to {pooled.shape}")
```

### 18.3.2 Recurrent Neural Networks (RNNs) and Transformers

**Theory:**

**RNNs**: Process sequences by maintaining hidden state.
```
h_t = tanh(W_h h_{t-1} + W_x x_t + b)
```

**LSTMs (Long Short-Term Memory)**: Address vanishing gradient problem
- Gates: forget, input, output
- Cell state: long-term memory
- Better at capturing long-range dependencies

**Transformers**: Attention-based architecture (replaces RNNs)
- Self-attention: weigh importance of different positions
- Parallel processing (vs sequential in RNNs)
- Foundation of modern NLP (BERT, GPT)

**WHY it matters:**

1. **NLP**: Language models, translation, summarization
2. **Time Series**: Stock prediction, weather forecasting
3. **Speech**: Recognition, synthesis
4. **Video**: Action recognition, captioning
5. **Code**: Code completion, bug detection

**Example - Simple RNN:**

```python
import numpy as np

class SimpleRNN:
    """
    Simple Recurrent Neural Network for sequence processing.
    
    Maintains hidden state that evolves over time.
    """
    
    def __init__(self, input_size, hidden_size, output_size):
        self.hidden_size = hidden_size
        
        # Parameters
        self.Wxh = np.random.randn(hidden_size, input_size) * 0.01
        self.Whh = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Why = np.random.randn(output_size, hidden_size) * 0.01
        self.bh = np.zeros((hidden_size, 1))
        self.by = np.zeros((output_size, 1))
    
    def forward(self, inputs, h_prev):
        """
        Forward pass through sequence.
        
        inputs: list of input vectors (one per time step)
        h_prev: previous hidden state
        
        Returns:
            outputs: list of output vectors
            h_last: final hidden state
            cache: intermediate values for backprop
        """
        h = h_prev
        outputs = []
        cache = {'inputs': inputs, 'h': [h_prev]}
        
        for x in inputs:
            # Recurrence relation
            # h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b_h)
            h = np.tanh(self.Wxh @ x + self.Whh @ h + self.bh)
            
            # Output
            y = self.Why @ h + self.by
            
            outputs.append(y)
            cache['h'].append(h)
        
        return outputs, h, cache
    
    def generate_sequence(self, seed, length):
        """
        Generate sequence given seed input.
        
        Example use: text generation, music generation
        """
        h = np.zeros((self.hidden_size, 1))
        x = seed
        sequence = []
        
        for _ in range(length):
            h = np.tanh(self.Wxh @ x + self.Whh @ h + self.bh)
            y = self.Why @ h + self.by
            
            # Sample from output (for probabilistic generation)
            # Here we just take argmax for simplicity
            sequence.append(y)
            
            # Feed output as next input
            x = y
        
        return sequence

# Example: Character-level language model (concept)
print("\nRecurrent Neural Networks - Sequence Processing")
print("=" * 60)

# Simplified example: predict next character
vocab = ['h', 'e', 'l', 'o', ' ', 'w', 'r', 'd']
char_to_idx = {ch: i for i, ch in enumerate(vocab)}
idx_to_char = {i: ch for i, ch in enumerate(vocab)}

vocab_size = len(vocab)
hidden_size = 20

rnn = SimpleRNN(input_size=vocab_size, hidden_size=hidden_size, output_size=vocab_size)

# Encode "hello" as one-hot vectors
def encode_char(ch):
    vec = np.zeros((vocab_size, 1))
    vec[char_to_idx[ch]] = 1
    return vec

inputs = [encode_char(ch) for ch in "hello"]

# Forward pass
h_init = np.zeros((hidden_size, 1))
outputs, h_final, cache = rnn.forward(inputs, h_init)

print(f"Processed sequence 'hello'")
print(f"Input length: {len(inputs)}")
print(f"Output length: {len(outputs)}")
print(f"Hidden state shape: {h_final.shape}")
print(f"\nRNN maintains hidden state that captures sequence context")
```

### 18.3.3 Training Strategies

**Theory:**

**Techniques for better training:**

1. **Batch Normalization**: Normalize activations
   - Reduces internal covariate shift
   - Allows higher learning rates
   - Provides regularization

2. **Dropout**: Randomly drop neurons during training
   - Prevents co-adaptation
   - Ensemble effect
   - Strong regularization

3. **Data Augmentation**: Artificially expand dataset
   - Images: rotation, flip, crop, color jitter
   - Text: back-translation, synonym replacement
   - Audio: time stretch, pitch shift

4. **Transfer Learning**: Start from pre-trained model
   - Fine-tune on target task
   - Requires less data
   - Faster training

5. **Learning Rate Scheduling**: Adjust LR during training
   - Step decay, exponential decay
   - Cosine annealing
   - Warm restarts

**WHY it matters:**

1. **Performance**: Better models, higher accuracy
2. **Efficiency**: Faster convergence, less compute
3. **Generalization**: Prevent overfitting
4. **Data Efficiency**: Work with limited data
5. **Practical**: Make deep learning actually work

**Example - Dropout and Batch Normalization:**

```python
import numpy as np

class Dropout:
    """
    Dropout regularization.
    
    During training: randomly set activations to zero
    During inference: use all neurons (scaled)
    """
    
    def __init__(self, drop_prob=0.5):
        self.drop_prob = drop_prob
        self.mask = None
    
    def forward(self, X, training=True):
        if training:
            # Create mask
            self.mask = (np.random.rand(*X.shape) > self.drop_prob)
            # Apply mask and scale
            return X * self.mask / (1 - self.drop_prob)
        else:
            # No dropout during inference
            return X

class BatchNormalization:
    """
    Batch Normalization.
    
    Normalize layer inputs to have mean 0, variance 1.
    Learnable scale (γ) and shift (β) parameters.
    """
    
    def __init__(self, n_features, epsilon=1e-5, momentum=0.9):
        self.epsilon = epsilon
        self.momentum = momentum
        
        # Learnable parameters
        self.gamma = np.ones(n_features)  # Scale
        self.beta = np.zeros(n_features)  # Shift
        
        # Running statistics (for inference)
        self.running_mean = np.zeros(n_features)
        self.running_var = np.ones(n_features)
    
    def forward(self, X, training=True):
        """
        X shape: (batch_size, n_features)
        
        Training: normalize using batch statistics
        Inference: normalize using running statistics
        """
        if training:
            # Batch statistics
            batch_mean = np.mean(X, axis=0)
            batch_var = np.var(X, axis=0)
            
            # Normalize
            X_norm = (X - batch_mean) / np.sqrt(batch_var + self.epsilon)
            
            # Update running statistics
            self.running_mean = (self.momentum * self.running_mean + 
                               (1 - self.momentum) * batch_mean)
            self.running_var = (self.momentum * self.running_var + 
                              (1 - self.momentum) * batch_var)
        else:
            # Use running statistics
            X_norm = (X - self.running_mean) / np.sqrt(self.running_var + self.epsilon)
        
        # Scale and shift
        return self.gamma * X_norm + self.beta

# Example: Effect of dropout and batch normalization
print("\nTraining Strategies - Dropout and Batch Normalization")
print("=" * 60)

# Simulate activations
np.random.seed(42)
X = np.random.randn(32, 10)  # Batch of 32, 10 features

# Dropout
dropout = Dropout(drop_prob=0.5)
X_dropped = dropout.forward(X, training=True)

print("Dropout Effect:")
print(f"Original mean: {X.mean():.4f}, std: {X.std():.4f}")
print(f"After dropout mean: {X_dropped.mean():.4f}, std: {X_dropped.std():.4f}")
print(f"Fraction of zeros: {np.mean(X_dropped == 0):.2%}")

# Batch Normalization
batch_norm = BatchNormalization(n_features=10)
X_bn = batch_norm.forward(X, training=True)

print(f"\nBatch Normalization Effect:")
print(f"Before: mean={X.mean(axis=0)[:3]}, var={X.var(axis=0)[:3]}")
print(f"After: mean={X_bn.mean(axis=0)[:3]}, var={X_bn.var(axis=0)[:3]}")
print("→ Normalized to mean≈0, var≈1")
```

**Connections to Other Topics:**

- **Part 16 (Math)**: Convolution is mathematical operation
- **Part 11 (Performance)**: GPU optimization for deep learning
- **Part 17 (Statistics)**: Regularization, generalization
- **Part 20 (UX)**: Computer vision for UI understanding

---

## 18.4 Natural Language Processing

**Theory:**

NLP: enabling computers to understand and generate human language.

**Key concepts:**

1. **Tokenization**: Split text into units (words, subwords, characters)

2. **Embeddings**: Represent words as dense vectors
   - Word2Vec: Skip-gram, CBOW
   - GloVe: Global vectors from co-occurrence
   - BERT, GPT: Contextual embeddings

3. **Language Models**: P(next word | previous words)
   - N-grams: Statistical models
   - RNN/LSTM: Neural language models
   - Transformers: State-of-the-art (GPT, BERT)

4. **Tasks**:
   - Classification: Sentiment, intent, topic
   - Named Entity Recognition (NER): Extract entities
   - Question Answering: Retrieve/generate answers
   - Translation: Seq2seq models
   - Summarization: Extract/abstract key points

**WHY it matters:**

1. **Search**: Understanding user queries
2. **Chatbots**: Customer service automation
3. **Content Moderation**: Detect harmful content
4. **Analytics**: Extract insights from text data
5. **Accessibility**: Text-to-speech, translation

**Example - Word Embeddings:**

```python
import numpy as np
from collections import defaultdict, Counter

class Word2Vec:
    """
    Simplified Word2Vec (Skip-gram model).
    
    Learn word embeddings by predicting context words from target word.
    
    Context: "The cat sat on the mat"
    Window=2: (cat, The), (cat, sat), (sat, cat), (sat, on), ...
    """
    
    def __init__(self, embedding_dim=50, window_size=2, learning_rate=0.01):
        self.embedding_dim = embedding_dim
        self.window_size = window_size
        self.lr = learning_rate
        
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.embeddings = None
        self.context_embeddings = None
    
    def build_vocab(self, sentences):
        """Build vocabulary from sentences"""
        word_counts = Counter()
        for sentence in sentences:
            word_counts.update(sentence.lower().split())
        
        # Create word-to-index mapping
        for idx, word in enumerate(word_counts.keys()):
            self.word_to_idx[word] = idx
            self.idx_to_word[idx] = word
        
        vocab_size = len(self.word_to_idx)
        
        # Initialize embeddings
        self.embeddings = np.random.randn(vocab_size, self.embedding_dim) * 0.01
        self.context_embeddings = np.random.randn(vocab_size, self.embedding_dim) * 0.01
    
    def generate_training_data(self, sentences):
        """
        Generate (target, context) pairs.
        
        Window size=2:
        "the cat sat" → (cat, the), (cat, sat)
        """
        pairs = []
        
        for sentence in sentences:
            words = sentence.lower().split()
            
            for i, target_word in enumerate(words):
                if target_word not in self.word_to_idx:
                    continue
                
                target_idx = self.word_to_idx[target_word]
                
                # Context words within window
                start = max(0, i - self.window_size)
                end = min(len(words), i + self.window_size + 1)
                
                for j in range(start, end):
                    if j != i and words[j] in self.word_to_idx:
                        context_idx = self.word_to_idx[words[j]]
                        pairs.append((target_idx, context_idx))
        
        return pairs
    
    def softmax(self, x):
        """Numerically stable softmax"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()
    
    def train(self, sentences, epochs=100):
        """
        Train embeddings using skip-gram with negative sampling.
        
        (Simplified version without negative sampling for clarity)
        """
        self.build_vocab(sentences)
        training_data = self.generate_training_data(sentences)
        
        print(f"Vocabulary size: {len(self.word_to_idx)}")
        print(f"Training pairs: {len(training_data)}")
        
        for epoch in range(epochs):
            np.random.shuffle(training_data)
            total_loss = 0
            
            for target_idx, context_idx in training_data:
                # Forward pass
                target_vec = self.embeddings[target_idx]
                
                # Compute scores for all words
                scores = self.context_embeddings @ target_vec
                probs = self.softmax(scores)
                
                # Cross-entropy loss
                loss = -np.log(probs[context_idx] + 1e-10)
                total_loss += loss
                
                # Backward pass (gradient descent)
                grad_scores = probs.copy()
                grad_scores[context_idx] -= 1
                
                # Update embeddings
                self.context_embeddings -= self.lr * np.outer(grad_scores, target_vec)
                self.embeddings[target_idx] -= self.lr * (self.context_embeddings.T @ grad_scores)
            
            if epoch % 20 == 0:
                print(f"Epoch {epoch}: Loss = {total_loss / len(training_data):.4f}")
    
    def most_similar(self, word, top_n=5):
        """Find most similar words using cosine similarity"""
        if word not in self.word_to_idx:
            return []
        
        word_idx = self.word_to_idx[word]
        word_vec = self.embeddings[word_idx]
        
        # Compute cosine similarity with all words
        similarities = []
        for idx in range(len(self.embeddings)):
            if idx == word_idx:
                continue
            
            other_vec = self.embeddings[idx]
            
            # Cosine similarity
            similarity = (word_vec @ other_vec) / \
                        (np.linalg.norm(word_vec) * np.linalg.norm(other_vec))
            
            similarities.append((self.idx_to_word[idx], similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_n]
    
    def analogy(self, word1, word2, word3):
        """
        Solve analogy: word1 is to word2 as word3 is to ?
        
        Example: king - man + woman = queen
        """
        if any(w not in self.word_to_idx for w in [word1, word2, word3]):
            return None
        
        idx1 = self.word_to_idx[word1]
        idx2 = self.word_to_idx[word2]
        idx3 = self.word_to_idx[word3]
        
        # Vector arithmetic
        target_vec = self.embeddings[idx1] - self.embeddings[idx2] + self.embeddings[idx3]
        
        # Find closest word (excluding input words)
        exclude = {idx1, idx2, idx3}
        best_similarity = -1
        best_word = None
        
        for idx in range(len(self.embeddings)):
            if idx in exclude:
                continue
            
            similarity = (target_vec @ self.embeddings[idx]) / \
                        (np.linalg.norm(target_vec) * np.linalg.norm(self.embeddings[idx]))
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_word = self.idx_to_word[idx]
        
        return best_word, best_similarity

# Example usage
print("\nNatural Language Processing - Word Embeddings")
print("=" * 60)

# Sample corpus
sentences = [
    "the cat sat on the mat",
    "the dog sat on the log",
    "cats and dogs are animals",
    "the cat chased the dog",
    "dogs and cats are pets",
    "the mat is on the floor",
    "the log is in the forest"
]

# Train Word2Vec
w2v = Word2Vec(embedding_dim=20, window_size=2, learning_rate=0.1)
w2v.train(sentences, epochs=100)

# Find similar words
print("\nMost similar words to 'cat':")
for word, sim in w2v.most_similar('cat', top_n=3):
    print(f"  {word}: {sim:.4f}")

print("\nMost similar words to 'mat':")
for word, sim in w2v.most_similar('mat', top_n=3):
    print(f"  {word}: {sim:.4f}")

print("\n→ Words appearing in similar contexts have similar embeddings")
```

**Connections to Other Topics:**

- **Part 17.1 (Probability)**: Language models are probability distributions
- **Part 16.3 (Graphs)**: Knowledge graphs for NLP
- **Part 20 (UX)**: Chatbots, search, content recommendation
- **Part 21 (Communication)**: Documentation generation

---

*[Continuing with Parts 19-22...]*

# PART 19: RESEARCH & INNOVATION METHODOLOGIES

Science-level engineers don't just implement existing solutions—they discover new ones through systematic research and experimentation.

## 19.1 Research Problem Definition

### 19.1.1 Converting Vague Problems into Research Questions

**Theory:**

Good research starts with well-defined questions:
- **Specific**: Clear scope and boundaries
- **Measurable**: Observable outcomes
- **Achievable**: Feasible with available resources
- **Relevant**: Addresses real need
- **Time-bound**: Defined timeline

**Process:**
1. **Problem Statement**: What's broken or missing?
2. **Literature Review**: What's already known?
3. **Gap Analysis**: What's unexplored?
4. **Research Questions**: What specific questions to answer?
5. **Hypotheses**: Testable predictions

**WHY it matters:**

1. **Focus**: Prevents scope creep and wasted effort
2. **Rigor**: Systematic approach yields better insights
3. **Communication**: Clear questions facilitate collaboration
4. **Impact**: Well-defined problems lead to actionable solutions
5. **Career**: Research skills distinguish senior+ engineers

**Example - Problem Definition Framework:**

```python
class ResearchProblemDefinition:
    """
    Framework for defining engineering research problems.
    
    Guides transformation from vague problem to structured research.
    """
    
    def __init__(self):
        self.problem_statement = None
        self.stakeholders = []
        self.constraints = []
        self.success_criteria = []
        self.research_questions = []
        self.hypotheses = []
    
    def define_problem(self):
        """
        Interactive problem definition worksheet.
        """
        template = """
        RESEARCH PROBLEM DEFINITION TEMPLATE
        ====================================
        
        1. PROBLEM STATEMENT
        --------------------
        Current situation:
          • What is happening now?
          • Who is affected?
          • What are the symptoms?
        
        Desired situation:
          • What should be happening?
          • What would success look like?
          • What are the benefits?
        
        2. STAKEHOLDERS
        ---------------
        Who cares about this problem?
          • End users
          • Business stakeholders
          • Technical teams
          • External partners
        
        3. CONSTRAINTS
        --------------
        What are the boundaries?
          • Time: Deadlines, milestones
          • Resources: Budget, team size, infrastructure
          • Technical: Platform, compatibility, performance
          • Regulatory: Compliance, privacy, security
        
        4. SUCCESS CRITERIA
        -------------------
        How will we measure success?
          • Quantitative metrics (latency, throughput, error rate)
          • Qualitative goals (usability, maintainability)
          • Business outcomes (revenue, user satisfaction)
        
        5. RESEARCH QUESTIONS
        ---------------------
        What specific questions need answers?
          • RQ1: [Clearly stated question]
          • RQ2: [Clearly stated question]
          • RQ3: [Clearly stated question]
        
        6. HYPOTHESES
        -------------
        What are our initial beliefs?
          • H1: [Testable prediction]
          • H2: [Testable prediction]
          • H3: [Testable prediction]
        
        7. RELATED WORK
        ---------------
        What solutions exist?
          • Prior art (academic papers, patents)
          • Existing tools/frameworks
          • Industry approaches
          • Why are they insufficient?
        """
        
        return template
    
    def example_case_study(self):
        """
        Example: Improving database query performance
        """
        return {
            'problem_statement': {
                'current': """
                    Dashboard queries taking 5-10 seconds during peak hours.
                    Users complaining about slow page loads.
                    Query complexity increasing with new features.
                """,
                'desired': """
                    Dashboard loads in <1 second even during peak.
                    Maintainable solution that scales with features.
                    No degradation under load.
                """
            },
            
            'stakeholders': [
                'End users (expecting fast dashboards)',
                'Product team (adding new features)',
                'Engineering team (maintaining system)',
                'SRE team (system reliability)'
            ],
            
            'constraints': [
                'Must work with existing PostgreSQL database',
                'Cannot require application rewrite',
                'Budget: $50k for infrastructure',
                'Timeline: 3 months to production'
            ],
            
            'success_criteria': [
                'P95 query latency < 500ms',
                'Handle 10x current traffic',
                'Code changes <1000 lines',
                'Rollback plan if issues arise'
            ],
            
            'research_questions': [
                'RQ1: What are the bottlenecks in current queries?',
                'RQ2: Would caching reduce latency sufficiently?',
                'RQ3: Can query optimization alone solve this?',
                'RQ4: Is database replication/sharding necessary?',
                'RQ5: What trade-offs exist between solutions?'
            ],
            
            'hypotheses': [
                'H1: 80% of queries hit same hot data (Pareto principle)',
                'H2: Read-through cache will reduce P95 to <500ms',
                'H3: Query plan optimization will eliminate full table scans',
                'H4: Connection pooling will reduce overhead by 30%'
            ],
            
            'related_work': [
                'Redis caching (used by Airbnb, GitHub)',
                'Query optimization techniques (academic literature)',
                'PostgreSQL performance tuning guides',
                'Read replicas (AWS RDS, Google Cloud SQL approaches)'
            ]
        }

# Example usage
rpd = ResearchProblemDefinition()

print("Research Problem Definition - Example Case Study")
print("=" * 60)

case_study = rpd.example_case_study()

print("\nPROBLEM STATEMENT:")
print("Current:", case_study['problem_statement']['current'])
print("Desired:", case_study['problem_statement']['desired'])

print("\nRESEARCH QUESTIONS:")
for rq in case_study['research_questions']:
    print(f"  • {rq}")

print("\nHYPOTHESES:")
for h in case_study['hypotheses']:
    print(f"  • {h}")

print("\nSUCCESS CRITERIA:")
for sc in case_study['success_criteria']:
    print(f"  • {sc}")

print("\n→ Well-defined problem enables systematic investigation")
```

### 19.1.2 Experimental Design

**Theory:**

Experiments test hypotheses through controlled investigation.

**Key principles:**
- **Control**: Isolate variables
- **Randomization**: Eliminate bias
- **Replication**: Ensure reliability
- **Statistical power**: Sufficient sample size

**Types:**
1. **A/B Testing**: Compare two variants
2. **Multivariate**: Test multiple factors simultaneously
3. **Factorial Design**: Test combinations of factors
4. **Quasi-experimental**: When randomization impossible

**WHY it matters:**

1. **Evidence**: Data-driven decisions, not opinions
2. **Validity**: Properly designed experiments yield trustworthy results
3. **Efficiency**: Good design maximizes information from minimal resources
4. **Reproducibility**: Others can verify findings
5. **Impact**: Convincing stakeholders requires rigorous evidence

**Example - Experimental Design:**

```python
import numpy as np
import pandas as pd
from scipy import stats

class ExperimentalDesign:
    """
    Framework for designing and analyzing experiments.
    """
    
    @staticmethod
    def sample_size_calculator(baseline_rate, mde, alpha=0.05, power=0.8):
        """
        Calculate required sample size for experiment.
        
        Args:
            baseline_rate: current conversion/success rate
            mde: minimum detectable effect (relative)
            alpha: significance level (Type I error)
            power: statistical power (1 - Type II error)
        
        Example:
            baseline_rate=0.05 (5% conversion)
            mde=0.2 (want to detect 20% relative improvement)
            → need 3,842 samples per group
        """
        treatment_rate = baseline_rate * (1 + mde)
        
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        p_avg = (baseline_rate + treatment_rate) / 2
        
        n = 2 * ((z_alpha + z_beta) ** 2) * p_avg * (1 - p_avg) / \
            ((treatment_rate - baseline_rate) ** 2)
        
        return int(np.ceil(n))
    
    @staticmethod
    def aa_test_simulation(n_simulations=1000, sample_size=1000):
        """
        A/A test: both groups identical (sanity check).
        
        Should see false positive rate ≈ significance level.
        If not, something is wrong with randomization.
        """
        p_value_distribution = []
        false_positive_count = 0
        alpha = 0.05
        
        for _ in range(n_simulations):
            # Both groups from same distribution
            group_a = np.random.binomial(1, 0.1, sample_size)
            group_b = np.random.binomial(1, 0.1, sample_size)
            
            # Test for difference (should find none)
            _, p_value = stats.ttest_ind(group_a, group_b)
            p_value_distribution.append(p_value)
            
            if p_value < alpha:
                false_positive_count += 1
        
        false_positive_rate = false_positive_count / n_simulations
        
        return {
            'expected_fpr': alpha,
            'observed_fpr': false_positive_rate,
            'p_values': p_value_distribution
        }
    
    @staticmethod
    def sequential_testing_simulation(true_effect=0.0, sample_size=1000, 
                                     n_peeks=10):
        """
        Demonstrate multiple testing problem.
        
        Looking at results repeatedly ("peeking") inflates false positive rate.
        Solution: Bonferroni correction or sequential testing methods.
        """
        # Generate data
        control = np.random.normal(100, 15, sample_size)
        treatment = np.random.normal(100 + true_effect, 15, sample_size)
        
        # Peek at different sample sizes
        peek_points = np.linspace(100, sample_size, n_peeks, dtype=int)
        
        results = []
        for n in peek_points:
            _, p_value = stats.ttest_ind(control[:n], treatment[:n])
            results.append({
                'sample_size': n,
                'p_value': p_value,
                'significant': p_value < 0.05
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def factorial_design_example():
        """
        Factorial design: test multiple factors simultaneously.
        
        Example: Website optimization
        Factors:
          - Button color (blue vs green)
          - Button text ("Buy Now" vs "Add to Cart")
          - Button size (small vs large)
        
        2×2×2 = 8 combinations (vs 6 for one-at-a-time)
        Can detect interactions between factors.
        """
        np.random.seed(42)
        
        # Simulate experiment
        factors = {
            'color': ['blue', 'green'],
            'text': ['Buy Now', 'Add to Cart'],
            'size': ['small', 'large']
        }
        
        results = []
        
        for color in factors['color']:
            for text in factors['text']:
                for size in factors['size']:
                    # Simulate conversion rate
                    base_rate = 0.10
                    
                    # Main effects
                    color_effect = 0.01 if color == 'green' else 0
                    text_effect = 0.02 if text == 'Buy Now' else 0
                    size_effect = 0.015 if size == 'large' else 0
                    
                    # Interaction: green + "Buy Now" synergy
                    interaction = 0.03 if (color == 'green' and text == 'Buy Now') else 0
                    
                    rate = base_rate + color_effect + text_effect + size_effect + interaction
                    
                    # Simulate 1000 trials
                    conversions = np.random.binomial(1000, rate)
                    
                    results.append({
                        'color': color,
                        'text': text,
                        'size': size,
                        'conversions': conversions,
                        'rate': conversions / 1000
                    })
        
        return pd.DataFrame(results)

# Example usage
print("Experimental Design Examples")
print("=" * 60)

# Sample size calculation
n_required = ExperimentalDesign.sample_size_calculator(
    baseline_rate=0.05,
    mde=0.2,  # 20% relative improvement
    alpha=0.05,
    power=0.8
)
print(f"\n1. SAMPLE SIZE CALCULATION")
print(f"   Baseline: 5% conversion rate")
print(f"   Want to detect: 20% relative improvement (5% → 6%)")
print(f"   Required sample size: {n_required:,} per group")

# A/A test sanity check
print(f"\n2. A/A TEST (Sanity Check)")
aa_results = ExperimentalDesign.aa_test_simulation(n_simulations=1000)
print(f"   Expected false positive rate: {aa_results['expected_fpr']:.1%}")
print(f"   Observed false positive rate: {aa_results['observed_fpr']:.1%}")
print(f"   → System is {'calibrated' if abs(aa_results['observed_fpr'] - aa_results['expected_fpr']) < 0.02 else 'MISCALIBRATED'}")

# Sequential testing problem
print(f"\n3. MULTIPLE TESTING PROBLEM")
seq_results = ExperimentalDesign.sequential_testing_simulation(
    true_effect=0,  # No real effect
    sample_size=1000,
    n_peeks=10
)
n_false_positives = seq_results['significant'].sum()
print(f"   Peeked 10 times at A/A test")
print(f"   False positives: {n_false_positives}/10")
print(f"   → Peeking inflates error rate! Use sequential testing methods.")

# Factorial design
print(f"\n4. FACTORIAL DESIGN")
factorial_results = ExperimentalDesign.factorial_design_example()
print(f"   Tested 3 factors (color, text, size) = 8 combinations")
print(f"\n   Top 3 combinations:")
top_3 = factorial_results.nlargest(3, 'rate')[['color', 'text', 'size', 'rate']]
for idx, row in top_3.iterrows():
    print(f"     {row['color']:6s} | {row['text']:12s} | {row['size']:5s} | {row['rate']:.1%}")
```

---

## 19.2 Prototyping & Experimentation

### 19.2.1 Rapid Prototyping Techniques

**Theory:**

Prototyping: build quick, throwaway implementations to test ideas.

**Types:**
- **Proof of Concept**: Can it be done?
- **Horizontal Prototype**: Broad but shallow (UI mockups)
- **Vertical Prototype**: Narrow but deep (one feature end-to-end)
- **Spike**: Time-boxed investigation of unknowns

**Principles:**
- **Speed over quality**: Quick and dirty is okay
- **Learn, don't build**: Goal is insights, not production code
- **Throwaway mentality**: Don't get attached
- **Focused scope**: Answer specific question

**WHY it matters:**

1. **Risk Reduction**: Fail fast, fail cheap
2. **Validation**: Test assumptions before investing
3. **Communication**: Show, don't tell
4. **Learning**: Discover unknowns early
5. **Momentum**: Quick wins build confidence

**Example - Prototyping Workflow:**

```python
import time
import random
from abc import ABC, abstractmethod

class Prototype(ABC):
    """
    Base class for rapid prototypes.
    
    Emphasizes speed and learning over production quality.
    """
    
    def __init__(self, name, time_budget_hours):
        self.name = name
        self.time_budget = time_budget_hours
        self.start_time = None
        self.learnings = []
        self.decisions = []
    
    def start(self):
        """Begin prototyping session"""
        self.start_time = time.time()
        print(f"\n{'='*60}")
        print(f"PROTOTYPE: {self.name}")
        print(f"Time Budget: {self.time_budget} hours")
        print(f"{'='*60}\n")
    
    @abstractmethod
    def build(self):
        """Implement prototype (quick and dirty)"""
        pass
    
    @abstractmethod
    def evaluate(self):
        """Test and measure prototype"""
        pass
    
    def record_learning(self, learning):
        """Document insight"""
        self.learnings.append(learning)
        print(f"💡 LEARNING: {learning}")
    
    def make_decision(self, decision):
        """Document decision"""
        self.decisions.append(decision)
        print(f"✓ DECISION: {decision}")
    
    def finish(self):
        """Conclude prototyping session"""
        elapsed = (time.time() - self.start_time) / 3600  # hours
        
        print(f"\n{'='*60}")
        print(f"PROTOTYPE COMPLETE")
        print(f"Time spent: {elapsed:.1f} hours (budget: {self.time_budget})")
        print(f"\nKey Learnings ({len(self.learnings)}):")
        for i, learning in enumerate(self.learnings, 1):
            print(f"  {i}. {learning}")
        
        print(f"\nDecisions ({len(self.decisions)}):")
        for i, decision in enumerate(self.decisions, 1):
            print(f"  {i}. {decision}")
        print(f"{'='*60}\n")

class CachingPrototype(Prototype):
    """
    Example: Prototype caching layer for slow API.
    
    Question: Will caching improve response times sufficiently?
    """
    
    def __init__(self):
        super().__init__(
            name="Redis Caching Layer",
            time_budget_hours=4
        )
        self.cache = {}
        self.api_latencies = []
        self.cache_latencies = []
    
    def slow_api_call(self, key):
        """Simulate slow API (100-200ms)"""
        time.sleep(random.uniform(0.1, 0.2))
        return f"data_for_{key}"
    
    def cache_get(self, key):
        """Simulate cache lookup (1-5ms)"""
        time.sleep(random.uniform(0.001, 0.005))
        return self.cache.get(key)
    
    def cache_set(self, key, value):
        """Simulate cache write"""
        self.cache[key] = value
    
    def build(self):
        """Build simple caching layer"""
        print("Building caching layer...")
        
        # Simulated implementation
        def get_data(key):
            # Check cache first
            cached = self.cache_get(key)
            if cached:
                return cached
            
            # Cache miss: fetch from API
            data = self.slow_api_call(key)
            self.cache_set(key, data)
            return data
        
        self.get_data = get_data
        
        self.record_learning("Redis client is straightforward to integrate")
        self.record_learning("Need TTL policy for cache invalidation")
    
    def evaluate(self):
        """Measure performance improvement"""
        print("\nEvaluating performance...")
        
        # Simulate realistic access pattern (80% hits hot data)
        keys = list(range(100))
        hot_keys = keys[:20]  # Top 20% of keys
        
        # Simulate 1000 requests
        for _ in range(1000):
            # 80% of requests hit hot keys (Pareto principle)
            if random.random() < 0.8:
                key = random.choice(hot_keys)
            else:
                key = random.choice(keys)
            
            start = time.time()
            self.get_data(key)
            latency = (time.time() - start) * 1000  # ms
            
            if key in self.cache:
                self.cache_latencies.append(latency)
            else:
                self.api_latencies.append(latency)
        
        # Analyze results
        import numpy as np
        
        api_p95 = np.percentile(self.api_latencies, 95) if self.api_latencies else 0
        cache_p95 = np.percentile(self.cache_latencies, 95) if self.cache_latencies else 0
        
        cache_hit_rate = len(self.cache_latencies) / 1000
        
        print(f"\nResults:")
        print(f"  Cache hit rate: {cache_hit_rate:.1%}")
        print(f"  API P95 latency: {api_p95:.1f}ms")
        print(f"  Cache P95 latency: {cache_p95:.1f}ms")
        print(f"  Improvement: {(api_p95 - cache_p95) / api_p95:.1%}")
        
        self.record_learning(f"Achieved {cache_hit_rate:.0%} hit rate with simple LRU")
        self.record_learning(f"P95 latency reduced by {(api_p95 - cache_p95) / api_p95:.0%}")
        
        # Decision time
        if cache_p95 < 10:  # Target: <10ms
            self.make_decision("PROCEED: Caching meets performance requirements")
            self.make_decision("Next: Design production caching strategy")
        else:
            self.make_decision("PIVOT: Caching alone insufficient, explore alternatives")

# Run prototype
prototype = CachingPrototype()
prototype.start()
prototype.build()
prototype.evaluate()
prototype.finish()

print("\n→ In 4 hours, validated approach and made informed decision")
```

### 19.2.2 Jupyter Notebooks for Exploration

**Theory:**

Jupyter notebooks: interactive environment for exploratory programming.

**Use cases:**
- Data analysis and visualization
- Algorithm prototyping
- Documentation with runnable code
- Educational materials
- Reproducible research

**Best practices:**
- Clear markdown explanations
- Modular cells (one concept per cell)
- Version control (use nbdime or jupytext)
- Extract production code to modules
- Use magic commands (%time, %debug, %load_ext)

**WHY it matters:**

1. **Interactive**: Immediate feedback loop
2. **Exploratory**: Easy to experiment and iterate
3. **Visual**: Inline plots and tables
4. **Shareable**: Communicate findings with code + narrative
5. **Reproducible**: Others can run and verify

**Example - Notebook Structure:**

```python
# Example Jupyter Notebook Structure
# ====================================

# Cell 1: Setup and Imports
"""
# Performance Analysis: Database Query Optimization

**Objective**: Identify slow queries and test optimization strategies

**Author**: Engineering Team
**Date**: 2024-01-15
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set visualization style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

# Cell 2: Load Data
"""
## Data Loading

Loading query logs from past 7 days.
"""

# In real scenario, load from database
# df = pd.read_sql("SELECT * FROM query_logs WHERE date >= NOW() - INTERVAL '7 days'", conn)

# Simulated data
np.random.seed(42)
n_queries = 10000

df = pd.DataFrame({
    'timestamp': [datetime.now() - timedelta(seconds=i*60) for i in range(n_queries)],
    'query_type': np.random.choice(['SELECT', 'INSERT', 'UPDATE'], n_queries, p=[0.7, 0.2, 0.1]),
    'duration_ms': np.random.lognormal(4, 1.5, n_queries),
    'table': np.random.choice(['users', 'orders', 'products', 'sessions'], n_queries),
    'has_index': np.random.choice([True, False], n_queries, p=[0.6, 0.4])
})

print(f"Loaded {len(df):,} queries")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
df.head()

# Cell 3: Exploratory Analysis
"""
## Exploratory Analysis

Quick overview of query performance.
"""

# Summary statistics
print("Duration Statistics (ms):")
print(df['duration_ms'].describe())

# Visualize distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
axes[0].hist(df['duration_ms'], bins=50, edgecolor='black', alpha=0.7)
axes[0].set_xlabel('Duration (ms)')
axes[0].set_ylabel('Count')
axes[0].set_title('Query Duration Distribution')
axes[0].axvline(df['duration_ms'].median(), color='red', linestyle='--', label=f'Median: {df["duration_ms"].median():.0f}ms')
axes[0].legend()

# Box plot by query type
df.boxplot(column='duration_ms', by='query_type', ax=axes[1])
axes[1].set_title('Duration by Query Type')
axes[1].set_xlabel('Query Type')
axes[1].set_ylabel('Duration (ms)')

plt.tight_layout()
# plt.show()

# Cell 4: Identify Bottlenecks
"""
## Bottleneck Identification

Finding the slowest queries.
"""

# Top 10 slowest queries
slow_queries = df.nlargest(10, 'duration_ms')
print("Top 10 Slowest Queries:")
print(slow_queries[['timestamp', 'query_type', 'table', 'duration_ms', 'has_index']])

# Queries without indexes
no_index = df[~df['has_index']]
print(f"\nQueries without index: {len(no_index):,} ({len(no_index)/len(df):.1%})")
print(f"Median duration (with index): {df[df['has_index']]['duration_ms'].median():.0f}ms")
print(f"Median duration (without index): {no_index['duration_ms'].median():.0f}ms")

# Cell 5: Hypothesis Testing
"""
## Hypothesis Test: Do indexes improve performance?

**H0**: Indexes have no effect on query duration
**H1**: Indexes reduce query duration
"""

from scipy import stats

with_index = df[df['has_index']]['duration_ms']
without_index = df[~df['has_index']]['duration_ms']

# Perform t-test
t_stat, p_value = stats.ttest_ind(without_index, with_index)

print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4e}")

if p_value < 0.05:
    print("\n✓ SIGNIFICANT: Indexes significantly reduce query duration")
    improvement = (without_index.median() - with_index.median()) / without_index.median()
    print(f"  Median improvement: {improvement:.1%}")
else:
    print("\n✗ NOT SIGNIFICANT: No evidence that indexes help")

# Cell 6: Recommendations
"""
## Recommendations

Based on analysis:

1. **Add indexes** to queries without them
   - Expected improvement: ~{improvement:.0%}
   - Affects {len(no_index):,} queries

2. **Optimize SELECT queries**
   - 70% of all queries
   - Median duration: {df[df['query_type']=='SELECT']['duration_ms'].median():.0f}ms

3. **Monitor slow queries**
   - Set alert threshold: P95 = {df['duration_ms'].quantile(0.95):.0f}ms

**Next Steps**:
- [ ] Create indexes on high-traffic tables
- [ ] Profile top 10 slowest queries
- [ ] Set up monitoring dashboard
"""

print("Analysis complete!")
```

### 19.2.3 Evaluation Metrics Design

**Theory:**

Good metrics are:
- **Measurable**: Can be quantified
- **Actionable**: Drive decisions
- **Relevant**: Align with goals
- **Timely**: Available when needed
- **Understandable**: Clear interpretation

**Types:**
- **North Star Metric**: Single most important metric
- **Input Metrics**: Leading indicators you can control
- **Output Metrics**: Lagging indicators of success
- **Guardrail Metrics**: Ensure you're not breaking things

**WHY it matters:**

1. **Alignment**: Focus team on what matters
2. **Accountability**: Clear success criteria
3. **Learning**: Understand what works
4. **Communication**: Shared language for progress
5. **Iteration**: Measure, learn, improve

**Example - Metrics Framework:**

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class MetricType(Enum):
    NORTH_STAR = "north_star"
    INPUT = "input"
    OUTPUT = "output"
    GUARDRAIL = "guardrail"

@dataclass
class Metric:
    """
    Structured metric definition.
    """
    name: str
    type: MetricType
    description: str
    formula: str
    target: Optional[float] = None
    current: Optional[float] = None
    
    def status(self):
        """Check if metric meets target"""
        if self.target is None or self.current is None:
            return "UNKNOWN"
        
        if self.current >= self.target:
            return "✓ ON TRACK"
        elif self.current >= self.target * 0.9:
            return "⚠ AT RISK"
        else:
            return "✗ OFF TRACK"
    
    def __str__(self):
        status = self.status()
        current_str = f"{self.current:.2f}" if self.current else "N/A"
        target_str = f"{self.target:.2f}" if self.target else "N/A"
        
        return f"""
{self.name} ({self.type.value})
  Description: {self.description}
  Formula: {self.formula}
  Current: {current_str} | Target: {target_str}
  Status: {status}
        """.strip()

class MetricsFramework:
    """
    Complete metrics framework for a project.
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.metrics: List[Metric] = []
    
    def add_metric(self, metric: Metric):
        """Add metric to framework"""
        self.metrics.append(metric)
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[Metric]:
        """Filter metrics by type"""
        return [m for m in self.metrics if m.type == metric_type]
    
    def summary(self):
        """Print metrics summary"""
        print(f"\n{'='*60}")
        print(f"METRICS FRAMEWORK: {self.project_name}")
        print(f"{'='*60}\n")
        
        for mtype in MetricType:
            metrics = self.get_metrics_by_type(mtype)
            if metrics:
                print(f"\n{mtype.value.upper()} METRICS ({len(metrics)}):")
                print("-" * 60)
                for metric in metrics:
                    print(metric)
                    print()

# Example: Metrics for search feature improvement
framework = MetricsFramework("Search Feature Improvement")

# North Star: Overall success
framework.add_metric(Metric(
    name="Search Success Rate",
    type=MetricType.NORTH_STAR,
    description="% of searches that result in user clicking a result",
    formula="(searches with clicks) / (total searches)",
    target=0.75,
    current=0.68
))

# Input Metrics: Things we can control
framework.add_metric(Metric(
    name="Search Response Time",
    type=MetricType.INPUT,
    description="P95 latency of search API",
    formula="95th percentile of response times",
    target=200,  # ms
    current=250
))

framework.add_metric(Metric(
    name="Result Relevance Score",
    type=MetricType.INPUT,
    description="Average relevance of top 10 results (0-1)",
    formula="Mean of relevance scores (manual evaluation)",
    target=0.85,
    current=0.78
))

# Output Metrics: Business outcomes
framework.add_metric(Metric(
    name="Click-Through Rate",
    type=MetricType.OUTPUT,
    description="% of searches resulting in click",
    formula="(searches with clicks) / (total searches)",
    target=0.70,
    current=0.65
))

framework.add_metric(Metric(
    name="Time to Click",
    type=MetricType.OUTPUT,
    description="Median time from search to first click",
    formula="Median(time_to_first_click)",
    target=5.0,  # seconds
    current=7.2
))

# Guardrail Metrics: Don't break things
framework.add_metric(Metric(
    name="Search Error Rate",
    type=MetricType.GUARDRAIL,
    description="% of searches that error",
    formula="(failed searches) / (total searches)",
    target=0.01,  # <1%
    current=0.005
))

framework.add_metric(Metric(
    name="Zero Results Rate",
    type=MetricType.GUARDRAIL,
    description="% of searches returning no results",
    formula="(searches with 0 results) / (total searches)",
    target=0.10,  # <10%
    current=0.15
))

# Print summary
framework.summary()

print("\n→ Clear metrics enable data-driven iteration")
```

**Connections to Other Topics:**

- **Part 17 (Statistics)**: Experimental design uses statistical methods
- **Part 10 (Testing)**: Metrics validate correctness
- **Part 12 (Monitoring)**: Production metrics monitoring
- **Part 15 (Judgment)**: Deciding what to measure

---

## 19.3 Academic Rigor

### 19.3.1 Literature Review Methods

**Theory:**

Literature review: systematic survey of existing research.

**Process:**
1. **Define scope**: Research questions, keywords
2. **Search**: Academic databases (Google Scholar, ACM, IEEE)
3. **Filter**: Relevance, quality, recency
4. **Synthesize**: Common themes, gaps, contradictions
5. **Cite**: Proper attribution

**Search strategies:**
- **Backward**: Follow citations in papers
- **Forward**: Find papers citing key work
- **Snowballing**: Iteratively expand search
- **Keywords**: Author names, terms, venues

**WHY it matters:**

1. **Avoid Reinvention**: Learn from prior work
2. **Context**: Understand problem landscape
3. **Credibility**: Ground work in existing knowledge
4. **Innovation**: Identify unexplored areas
5. **Standing**: Build on giants' shoulders

**Example - Literature Review Template:**

```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class Paper:
    """Structured representation of research paper"""
    title: str
    authors: List[str]
    year: int
    venue: str
    url: str
    
    # Review notes
    key_contributions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    relevant_to_my_work: str = ""
    citation_count: int = 0
    
    def cite_apa(self):
        """Generate APA citation"""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += ", et al."
        
        return f"{authors_str} ({self.year}). {self.title}. {self.venue}."
    
    def summary(self):
        """Print paper summary"""
        print(f"\n{'='*60}")
        print(f"{self.title}")
        print(f"{', '.join(self.authors)} ({self.year})")
        print(f"{self.venue}")
        print(f"Citations: {self.citation_count}")
        print(f"{'='*60}")
        
        print(f"\nKEY CONTRIBUTIONS:")
        for contrib in self.key_contributions:
            print(f"  • {contrib}")
        
        print(f"\nLIMITATIONS:")
        for limit in self.limitations:
            print(f"  • {limit}")
        
        print(f"\nRELEVANCE TO MY WORK:")
        print(f"  {self.relevant_to_my_work}")
        
        print(f"\nCITATION:")
        print(f"  {self.cite_apa()}")

class LiteratureReview:
    """
    Organize literature review process.
    """
    
    def __init__(self, topic: str):
        self.topic = topic
        self.papers: List[Paper] = []
        self.keywords: List[str] = []
        self.research_questions: List[str] = []
    
    def add_paper(self, paper: Paper):
        """Add paper to review"""
        self.papers.append(paper)
    
    def synthesize(self):
        """Synthesize findings across papers"""
        print(f"\n{'='*60}")
        print(f"LITERATURE REVIEW SYNTHESIS: {self.topic}")
        print(f"{'='*60}\n")
        
        print(f"Total papers reviewed: {len(self.papers)}")
        print(f"Date range: {min(p.year for p in self.papers)} - {max(p.year for p in self.papers)}")
        
        # Common themes
        all_contributions = []
        for paper in self.papers:
            all_contributions.extend(paper.key_contributions)
        
        print(f"\nRESEARCH QUESTIONS:")
        for i, rq in enumerate(self.research_questions, 1):
            print(f"  {i}. {rq}")
        
        print(f"\nKEY FINDINGS:")
        print("  [Synthesize common themes, contradictions, gaps]")
        
        print(f"\nGAPS IN LITERATURE:")
        print("  [Identify what hasn't been explored]")
        
        print(f"\nIMPLICATIONS FOR MY WORK:")
        print("  [How this informs your research]")
    
    def generate_bibliography(self):
        """Generate formatted bibliography"""
        print(f"\n{'='*60}")
        print("BIBLIOGRAPHY")
        print(f"{'='*60}\n")
        
        # Sort by author last name, then year
        sorted_papers = sorted(self.papers, key=lambda p: (p.authors[0].split()[-1], p.year))
        
        for paper in sorted_papers:
            print(f"{paper.cite_apa()}")
            print(f"  {paper.url}\n")

# Example: Literature review on caching strategies
review = LiteratureReview("Distributed Caching Strategies for Web Applications")

review.research_questions = [
    "What caching strategies exist for distributed systems?",
    "How do different eviction policies perform?",
    "What are the trade-offs between consistency and performance?"
]

# Add papers (examples)
review.add_paper(Paper(
    title="Memcached: A Distributed Memory Object Caching System",
    authors=["Brad Fitzpatrick"],
    year=2004,
    venue="Linux Journal",
    url="https://example.com/memcached",
    key_contributions=[
        "Introduced distributed hash table for caching",
        "Demonstrated 10x performance improvement",
        "LRU eviction policy for memory management"
    ],
    limitations=[
        "No built-in persistence",
        "No replication (single point of failure)",
        "Eventually consistent (no strong guarantees)"
    ],
    relevant_to_my_work="Baseline for comparison. Our work extends with persistence.",
    citation_count=1247
))

review.add_paper(Paper(
    title="Redis: An In-Memory Database System",
    authors=["Salvatore Sanfilippo"],
    year=2009,
    venue="NoSQL Matters",
    url="https://example.com/redis",
    key_contributions=[
        "Rich data structures (lists, sets, sorted sets)",
        "Optional persistence (RDB, AOF)",
        "Pub/sub messaging support"
    ],
    limitations=[
        "Single-threaded (CPU bound for complex operations)",
        "Memory-limited scalability",
        "Replication lag in distributed setup"
    ],
    relevant_to_my_work="Alternative to Memcached. Persistence is key differentiator.",
    citation_count=892
))

review.add_paper(Paper(
    title="TAO: Facebook's Distributed Data Store for the Social Graph",
    authors=["Nathan Bronson", "Zach Amsden", "et al."],
    year=2013,
    venue="USENIX ATC",
    url="https://example.com/tao",
    key_contributions=[
        "Write-through cache for social graph",
        "Hierarchical cache architecture (leader-follower)",
        "Handles 1 billion queries/second"
    ],
    limitations=[
        "Tightly coupled to Facebook's infrastructure",
        "Complex consistency model",
        "Not open source"
    ],
    relevant_to_my_work="Demonstrates scalability patterns. Leader-follower relevant.",
    citation_count=534
))

# Show individual paper
review.papers[0].summary()

# Synthesize findings
review.synthesize()

# Generate bibliography
review.generate_bibliography()
```

---

## 19.4 Publishing & Presenting

### 19.4.1 Technical Paper Writing

**Theory:**

Structure of technical paper:
1. **Abstract**: Problem, approach, results (150-250 words)
2. **Introduction**: Motivation, problem statement, contributions
3. **Related Work**: Literature review, position your work
4. **Methodology**: Approach, algorithms, system design
5. **Evaluation**: Experiments, results, analysis
6. **Discussion**: Implications, limitations, future work
7. **Conclusion**: Summary of contributions

**Writing principles:**
- **Clarity**: Simple language, define terms
- **Precision**: Specific claims, exact measurements
- **Evidence**: Data supports claims
- **Reproducibility**: Others can verify results
- **Contribution**: Clear novelty statement

**WHY it matters:**

1. **Knowledge Sharing**: Advance field
2. **Peer Review**: Validate work through scrutiny
3. **Career**: Publications = credibility
4. **Impact**: Ideas adopted by others
5. **Documentation**: Permanent record

**Example - Paper Outline Template:**

```python
class TechnicalPaper:
    """
    Template for technical paper structure.
    """
    
    def __init__(self, title: str):
        self.title = title
        self.abstract = ""
        self.introduction = ""
        self.related_work = []
        self.methodology = ""
        self.evaluation = {}
        self.discussion = ""
        self.conclusion = ""
    
    def generate_outline(self):
        """Generate paper outline"""
        outline = f"""
{'='*70}
TECHNICAL PAPER OUTLINE
{'='*70}

TITLE: {self.title}

{'='*70}
ABSTRACT (150-250 words)
{'='*70}

[Problem Statement - 2 sentences]
• What problem are we solving?
• Why is it important?

[Approach - 2-3 sentences]
• What is our solution?
• Key insight or technique

[Results - 2 sentences]
• Main findings (quantitative)
• Significance of results

Example:
  "Web applications face performance challenges when serving
   personalized content at scale. Existing caching strategies
   fail to handle personalization effectively, resulting in
   cache hit rates below 30%. We present PersonalCache, a
   novel caching architecture that exploits user similarity
   to achieve 75% hit rates while maintaining personalization.
   In production deployment serving 10M users, PersonalCache
   reduced P95 latency from 450ms to 85ms (81% improvement)
   with 40% reduction in database load."

{'='*70}
1. INTRODUCTION
{'='*70}

1.1 Motivation
• Why does this problem matter?
• Real-world impact
• Current pain points

1.2 Problem Statement
• Precise definition of problem
• Scope and boundaries
• Challenges

1.3 Contributions
• Novelty 1: [Specific contribution]
• Novelty 2: [Specific contribution]
• Novelty 3: [Specific contribution]

1.4 Paper Organization
• Section 2: Related work
• Section 3: System design
• etc.

{'='*70}
2. RELATED WORK
{'='*70}

2.1 Caching Strategies
• Traditional approaches (Memcached, Redis)
• Limitations for our problem

2.2 Personalization Techniques
• Prior work on personalized systems
• How they handle caching

2.3 Comparison
• What makes our approach different?
• Table comparing features

{'='*70}
3. METHODOLOGY / SYSTEM DESIGN
{'='*70}

3.1 Overview
• High-level architecture diagram
• Key components
• Design principles

3.2 Core Algorithm
• Pseudocode or detailed description
• Complexity analysis
• Correctness argument

3.3 Implementation
• Technology stack
• Key engineering decisions
• Trade-offs made

{'='*70}
4. EVALUATION
{'='*70}

4.1 Experimental Setup
• Dataset description
• Baseline systems
• Evaluation metrics
• Hardware/infrastructure

4.2 Results
• Primary metrics
• Graphs and tables
• Statistical significance

4.3 Analysis
• Why did approach work?
• Sensitivity analysis
• Edge cases

4.4 Case Studies
• Real-world deployments
• Lessons learned

{'='*70}
5. DISCUSSION
{'='*70}

5.1 Implications
• What do results mean?
• Practical takeaways
• When to use this approach

5.2 Limitations
• What doesn't work well?
• Assumptions made
• Scope boundaries

5.3 Future Work
• Open questions
• Potential improvements
• Research directions

{'='*70}
6. CONCLUSION
{'='*70}

• Restate problem
• Summary of approach
• Key results
• Impact statement

{'='*70}
REFERENCES
{'='*70}

[1] Author et al. "Title." Venue, Year.
[2] ...

{'='*70}
        """
        
        return outline
    
    def writing_checklist(self):
        """Checklist for paper quality"""
        checklist = """
TECHNICAL PAPER WRITING CHECKLIST
==================================

CONTENT
□ Clear problem statement
□ Novelty clearly articulated
□ Related work comprehensive and fair
□ Methodology described in sufficient detail
□ Experiments address research questions
□ Results presented with statistical rigor
□ Limitations honestly discussed
□ Contributions summarized in conclusion

CLARITY
□ Abstract readable by non-experts
□ Technical terms defined on first use
□ Figures have descriptive captions
□ Tables are readable and well-formatted
□ Equations explained in text
□ Code/pseudocode is understandable

EVIDENCE
□ Claims supported by data
□ Experiments are reproducible
□ Baselines are appropriate
□ Statistical tests used correctly
□ Error bars shown where appropriate
□ Edge cases discussed

PRESENTATION
□ Spelling and grammar checked
□ Consistent terminology throughout
□ References formatted consistently
□ Figures readable when printed B&W
□ Page limit respected
□ Follows venue style guide

REPRODUCIBILITY
□ Dataset publicly available (or described)
□ Code released (or detailed pseudocode)
□ Hyperparameters documented
□ Experimental setup replicable
□ Random seeds mentioned
        """
        
        return checklist

# Example usage
paper = TechnicalPaper("PersonalCache: Scalable Personalized Content Caching")

print(paper.generate_outline())
print("\n")
print(paper.writing_checklist())
```

**Connections to Other Topics:**

- **Part 17 (Statistics)**: Experimental results need statistical rigor
- **Part 21 (Communication)**: Writing for technical audiences
- **Part 15 (Judgment)**: Knowing what's worth publishing
- **Part 13 (Architecture)**: System design papers

---

*[Continuing with Parts 20-22...]*

# PART 20: UI/UX & HUMAN-COMPUTER INTERACTION

Great software requires understanding humans as much as machines. UI/UX design is not just aesthetics—it's applying cognitive science, psychology, and empirical research to create effective interfaces.

## 20.1 User-Centered Design (UCD)

### 20.1.1 User Research Methods

**Theory:**

User research: systematic study of users, needs, and behaviors.

**Methods:**
1. **Interviews**: Deep qualitative insights
   - Structured, semi-structured, unstructured
   - 5-10 users often sufficient for patterns

2. **Surveys**: Quantitative data at scale
   - Multiple choice, Likert scales, open-ended
   - Statistical analysis required

3. **Contextual Inquiry**: Observe users in natural environment
   - Watch real work, not stated work
   - Understand context and constraints

4. **Usability Testing**: Watch users attempt tasks
   - Think-aloud protocol
   - Measure success rate, time, errors

5. **Analytics**: Behavioral data from production
   - Funnels, heatmaps, session recordings
   - Complement qualitative research

**WHY it matters:**

1. **User Needs**: Build what users actually need
2. **Avoid Assumptions**: Test beliefs against reality
3. **Prioritization**: Focus on highest-impact problems
4. **Empathy**: Understand user frustrations
5. **Validation**: Measure whether solution works

**Example - User Research Framework:**

```python
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
from enum import Enum

class ResearchMethod(Enum):
    INTERVIEW = "interview"
    SURVEY = "survey"
    USABILITY_TEST = "usability_test"
    CONTEXTUAL_INQUIRY = "contextual_inquiry"
    ANALYTICS = "analytics"

@dataclass
class ResearchFinding:
    """Structured user research finding"""
    method: ResearchMethod
    finding: str
    evidence: str
    impact: str  # high, medium, low
    participant_count: int
    
    def __str__(self):
        return f"""
Finding ({self.method.value}, n={self.participant_count}):
  {self.finding}
  
  Evidence: {self.evidence}
  Impact: {self.impact}
        """.strip()

@dataclass
class UserPersona:
    """User archetype representing segment"""
    name: str
    role: str
    goals: List[str]
    pain_points: List[str]
    tech_proficiency: str  # novice, intermediate, expert
    quote: str  # Representative quote from research
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"PERSONA: {self.name}")
        print(f"Role: {self.role}")
        print(f"Tech Proficiency: {self.tech_proficiency}")
        print(f"{'='*60}")
        
        print(f"\nGOALS:")
        for goal in self.goals:
            print(f"  • {goal}")
        
        print(f"\nPAIN POINTS:")
        for pain in self.pain_points:
            print(f"  • {pain}")
        
        print(f'\nQUOTE: "{self.quote}"')

class UserResearchStudy:
    """
    Organize and synthesize user research.
    """
    
    def __init__(self, study_name: str, research_questions: List[str]):
        self.study_name = study_name
        self.research_questions = research_questions
        self.findings: List[ResearchFinding] = []
        self.personas: List[UserPersona] = []
    
    def add_finding(self, finding: ResearchFinding):
        """Add research finding"""
        self.findings.append(finding)
    
    def add_persona(self, persona: UserPersona):
        """Add user persona"""
        self.personas.append(persona)
    
    def synthesize_findings(self):
        """Synthesize insights across methods"""
        print(f"\n{'='*60}")
        print(f"USER RESEARCH SYNTHESIS: {self.study_name}")
        print(f"{'='*60}\n")
        
        print("RESEARCH QUESTIONS:")
        for i, rq in enumerate(self.research_questions, 1):
            print(f"  {i}. {rq}")
        
        print(f"\nMETHODS USED:")
        methods = set(f.method for f in self.findings)
        for method in methods:
            method_findings = [f for f in self.findings if f.method == method]
            total_participants = sum(f.participant_count for f in method_findings)
            print(f"  • {method.value}: {len(method_findings)} findings, {total_participants} participants")
        
        # High-impact findings
        high_impact = [f for f in self.findings if f.impact == "high"]
        print(f"\nHIGH IMPACT FINDINGS ({len(high_impact)}):")
        for finding in high_impact:
            print(f"\n  • {finding.finding}")
            print(f"    Evidence: {finding.evidence}")
            print(f"    Method: {finding.method.value} (n={finding.participant_count})")
        
        # Personas
        print(f"\nUSER PERSONAS ({len(self.personas)}):")
        for persona in self.personas:
            print(f"  • {persona.name} - {persona.role}")

# Example: E-commerce checkout research
study = UserResearchStudy(
    study_name="E-commerce Checkout Flow Optimization",
    research_questions=[
        "Why do users abandon checkout?",
        "What friction points exist in payment flow?",
        "How do users decide between shipping options?"
    ]
)

# Add findings from different methods
study.add_finding(ResearchFinding(
    method=ResearchMethod.USABILITY_TEST,
    finding="Users struggle to find promo code field",
    evidence="7/10 participants failed to apply discount code within 2 minutes",
    impact="high",
    participant_count=10
))

study.add_finding(ResearchFinding(
    method=ResearchMethod.ANALYTICS,
    finding="60% cart abandonment at shipping address step",
    evidence="Funnel analysis shows 12,453 dropoffs at address form (60% of carts)",
    impact="high",
    participant_count=20789  # total carts analyzed
))

study.add_finding(ResearchFinding(
    method=ResearchMethod.INTERVIEW,
    finding="Users want to save multiple shipping addresses",
    evidence='"I order gifts for family, but have to re-enter addresses every time" - 4 participants',
    impact="medium",
    participant_count=8
))

study.add_finding(ResearchFinding(
    method=ResearchMethod.SURVEY,
    finding="Users prefer free shipping over fast shipping",
    evidence="78% chose free 5-7 day over $5.99 2-day shipping (n=523)",
    impact="medium",
    participant_count=523
))

# Create personas
study.add_persona(UserPersona(
    name="Busy Parent Brian",
    role="Working parent, frequent buyer",
    goals=[
        "Quick reordering of regular items",
        "Track multiple deliveries",
        "Split payment between cards"
    ],
    pain_points=[
        "Re-entering address for gifts",
        "Checkout takes too long (5+ min)",
        "Can't save payment methods securely"
    ],
    tech_proficiency="intermediate",
    quote="I shop during my lunch break, so speed is everything"
))

study.add_persona(UserPersona(
    name="First-time Buyer Fiona",
    role="New customer, price-conscious",
    goals=[
        "Find best deal/discount",
        "Understand return policy",
        "Feel secure entering payment info"
    ],
    pain_points=[
        "Unclear total cost until final step",
        "Hesitant about creating account",
        "Worried about security"
    ],
    tech_proficiency="novice",
    quote="I just want to know the final price upfront, including shipping and taxes"
))

# Synthesize
study.synthesize_findings()

# Show personas
for persona in study.personas:
    persona.summary()

print("\n→ Research reveals user needs that aren't obvious from analytics alone")
```

### 20.1.2 Usability Testing

**Theory:**

Usability testing: observing users attempting tasks to identify issues.

**Process:**
1. **Define tasks**: Realistic scenarios users will perform
2. **Recruit participants**: Representative of target users (5-8 often enough)
3. **Prepare**: Test environment, materials, consent forms
4. **Facilitate**: Think-aloud protocol, minimal intervention
5. **Observe**: Note struggles, errors, confusion
6. **Debrief**: Post-task questions
7. **Analyze**: Identify patterns across participants
8. **Iterate**: Fix issues, test again

**Metrics:**
- **Success rate**: % completing task correctly
- **Time on task**: How long to complete
- **Errors**: Number and type of mistakes
- **Satisfaction**: Post-task ratings

**WHY it matters:**

1. **Validation**: Does design actually work?
2. **Discovery**: Find unexpected issues
3. **Prioritization**: Which problems are most severe?
4. **Empathy**: See user struggles firsthand
5. **ROI**: Catch issues before expensive production deployment

**Example - Usability Test Framework:**

```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime, timedelta
import numpy as np

@dataclass
class Task:
    """Task for usability testing"""
    id: str
    description: str
    scenario: str
    success_criteria: str
    expected_time_seconds: int
    
    def present(self):
        """Present task to participant"""
        return f"""
TASK {self.id}

Scenario:
{self.scenario}

Your task:
{self.description}

Please think aloud as you work through this task.
        """.strip()

@dataclass
class TaskAttempt:
    """Record of participant attempting task"""
    task_id: str
    participant_id: str
    success: bool
    time_seconds: int
    errors: List[str] = field(default_factory=list)
    confusion_points: List[str] = field(default_factory=list)
    satisfaction_rating: int = 0  # 1-5 scale
    notes: str = ""

class UsabilityTest:
    """
    Framework for running and analyzing usability tests.
    """
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.tasks: List[Task] = []
        self.attempts: List[TaskAttempt] = []
    
    def add_task(self, task: Task):
        """Add task to test"""
        self.tasks.append(task)
    
    def record_attempt(self, attempt: TaskAttempt):
        """Record task attempt"""
        self.attempts.append(attempt)
    
    def analyze_task(self, task_id: str):
        """Analyze results for specific task"""
        task = next(t for t in self.tasks if t.id == task_id)
        task_attempts = [a for a in self.attempts if a.task_id == task_id]
        
        if not task_attempts:
            print(f"No data for task {task_id}")
            return
        
        # Calculate metrics
        success_rate = sum(a.success for a in task_attempts) / len(task_attempts)
        avg_time = np.mean([a.time_seconds for a in task_attempts])
        median_time = np.median([a.time_seconds for a in task_attempts])
        avg_satisfaction = np.mean([a.satisfaction_rating for a in task_attempts])
        
        # Collect all errors and confusion points
        all_errors = []
        all_confusion = []
        for attempt in task_attempts:
            all_errors.extend(attempt.errors)
            all_confusion.extend(attempt.confusion_points)
        
        # Count frequencies
        from collections import Counter
        error_counts = Counter(all_errors)
        confusion_counts = Counter(all_confusion)
        
        print(f"\n{'='*60}")
        print(f"TASK ANALYSIS: {task_id}")
        print(f"Description: {task.description}")
        print(f"{'='*60}")
        
        print(f"\nPARTICIPANTS: {len(task_attempts)}")
        
        print(f"\nSUCCESS METRICS:")
        print(f"  Success rate: {success_rate:.1%} ({sum(a.success for a in task_attempts)}/{len(task_attempts)})")
        
        # Severity assessment
        if success_rate < 0.7:
            severity = "CRITICAL - Most users fail"
        elif success_rate < 0.9:
            severity = "MAJOR - Significant issues"
        else:
            severity = "MINOR - Mostly successful"
        print(f"  Severity: {severity}")
        
        print(f"\nTIME METRICS:")
        print(f"  Expected time: {task.expected_time_seconds}s")
        print(f"  Average time: {avg_time:.1f}s ({avg_time/task.expected_time_seconds:.1f}x expected)")
        print(f"  Median time: {median_time:.1f}s")
        print(f"  Range: {min(a.time_seconds for a in task_attempts)}s - {max(a.time_seconds for a in task_attempts)}s")
        
        print(f"\nSATISFACTION:")
        print(f"  Average rating: {avg_satisfaction:.1f}/5")
        
        if error_counts:
            print(f"\nTOP ERRORS:")
            for error, count in error_counts.most_common(3):
                print(f"  • {error} ({count} participants)")
        
        if confusion_counts:
            print(f"\nTOP CONFUSION POINTS:")
            for confusion, count in confusion_counts.most_common(3):
                print(f"  • {confusion} ({count} participants)")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS:")
        if success_rate < 0.7:
            print("  ⚠ URGENT: Redesign required")
        elif avg_time > task.expected_time_seconds * 1.5:
            print("  ⚠ Streamline flow to reduce time")
        if avg_satisfaction < 3.5:
            print("  ⚠ Address user frustration")
        if not error_counts and success_rate > 0.9:
            print("  ✓ Task works well, minor polish needed")
    
    def summary_report(self):
        """Generate overall test summary"""
        print(f"\n{'='*60}")
        print(f"USABILITY TEST SUMMARY: {self.test_name}")
        print(f"{'='*60}\n")
        
        total_participants = len(set(a.participant_id for a in self.attempts))
        print(f"Participants: {total_participants}")
        print(f"Tasks: {len(self.tasks)}")
        print(f"Total attempts: {len(self.attempts)}")
        
        print(f"\nTASK OVERVIEW:")
        for task in self.tasks:
            task_attempts = [a for a in self.attempts if a.task_id == task.id]
            if task_attempts:
                success_rate = sum(a.success for a in task_attempts) / len(task_attempts)
                avg_time = np.mean([a.time_seconds for a in task_attempts])
                
                status = "✓" if success_rate >= 0.9 else "⚠" if success_rate >= 0.7 else "✗"
                print(f"  {status} {task.id}: {success_rate:.0%} success, {avg_time:.0f}s avg time")

# Example: Mobile app usability test
test = UsabilityTest("Mobile Banking App - Fund Transfer")

# Define tasks
test.add_task(Task(
    id="T1",
    description="Transfer $50 to your friend John",
    scenario="You owe your friend John $50 for dinner. Send him the money using the app.",
    success_criteria="Successfully initiate transfer to correct contact for correct amount",
    expected_time_seconds=30
))

test.add_task(Task(
    id="T2",
    description="Schedule recurring payment",
    scenario="Set up automatic $200 rent payment on the 1st of each month.",
    success_criteria="Recurring payment scheduled with correct amount and frequency",
    expected_time_seconds=45
))

test.add_task(Task(
    id="T3",
    description="Find transaction from 3 weeks ago",
    scenario="You need to verify a grocery store charge from 3 weeks ago.",
    success_criteria="Locate specific transaction in history",
    expected_time_seconds=20
))

# Simulate test results (in real test, collect from actual participants)
np.random.seed(42)

participants = [f"P{i}" for i in range(1, 9)]  # 8 participants

for participant in participants:
    # Task 1: Most succeed, some confusion
    test.record_attempt(TaskAttempt(
        task_id="T1",
        participant_id=participant,
        success=np.random.random() > 0.2,  # 80% success rate
        time_seconds=int(np.random.normal(35, 8)),
        errors=["Tapped wrong button"] if np.random.random() > 0.7 else [],
        confusion_points=["Couldn't find contacts list"] if np.random.random() > 0.6 else [],
        satisfaction_rating=int(np.random.normal(4, 0.5))
    ))
    
    # Task 2: More difficult, lower success
    test.record_attempt(TaskAttempt(
        task_id="T2",
        participant_id=participant,
        success=np.random.random() > 0.4,  # 60% success rate
        time_seconds=int(np.random.normal(75, 15)),
        errors=["Selected wrong date", "Couldn't find recurring option"] if np.random.random() > 0.5 else ["Couldn't find recurring option"],
        confusion_points=["Menu structure unclear", "Didn't see 'recurring' option"],
        satisfaction_rating=int(np.random.normal(3, 0.7))
    ))
    
    # Task 3: Easy, high success
    test.record_attempt(TaskAttempt(
        task_id="T3",
        participant_id=participant,
        success=np.random.random() > 0.1,  # 90% success rate
        time_seconds=int(np.random.normal(22, 5)),
        errors=[],
        confusion_points=[],
        satisfaction_rating=int(np.random.normal(4.5, 0.3))
    ))

# Analyze results
test.summary_report()

for task in test.tasks:
    test.analyze_task(task.id)

print("\n→ Usability testing reveals real user struggles, not assumptions")
```

---

## 20.2 Information Architecture (IA)

### 20.2.1 Content Organization

**Theory:**

Information architecture: structuring and organizing content for findability and usability.

**Principles:**
1. **Mental Models**: Match user's expectations
2. **Hierarchy**: Clear parent-child relationships
3. **Labeling**: Descriptive, consistent terminology
4. **Navigation**: Multiple paths to content
5. **Search**: When browsing fails

**Organization schemes:**
- **Exact**: Alphabetical, chronological, geographical
- **Ambiguous**: Topic, task, audience, metaphor

**Card sorting:** Users group/label content cards
- **Open**: Users create categories
- **Closed**: Users sort into predefined categories

**WHY it matters:**

1. **Findability**: Users can locate information
2. **Scannability**: Quick orientation
3. **Scalability**: Structure supports growth
4. **Consistency**: Predictable organization
5. **Task completion**: Efficient workflows

**Example - IA Evaluation:**

```python
from dataclasses import dataclass
from typing import List, Dict, Set
import networkx as nx

@dataclass
class ContentItem:
    """Piece of content in IA"""
    id: str
    title: str
    category: str
    tags: List[str]
    
@dataclass
class NavigationPath:
    """Path through IA to reach content"""
    steps: List[str]
    
    def depth(self):
        return len(self.steps)
    
    def __str__(self):
        return " → ".join(self.steps)

class InformationArchitecture:
    """
    Analyze and evaluate information architecture.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.structure = nx.DiGraph()  # Directed graph for hierarchy
        self.content_items: List[ContentItem] = []
    
    def add_page(self, page_id: str, parent_id: str = None):
        """Add page to structure"""
        self.structure.add_node(page_id)
        if parent_id:
            self.structure.add_edge(parent_id, page_id)
    
    def add_content(self, item: ContentItem):
        """Add content item"""
        self.content_items.append(item)
    
    def find_path(self, start: str, end: str) -> NavigationPath:
        """Find navigation path between pages"""
        try:
            path = nx.shortest_path(self.structure, start, end)
            return NavigationPath(path)
        except nx.NetworkXNoPath:
            return None
    
    def analyze_depth(self):
        """Analyze depth of IA (too deep = hard to navigate)"""
        if not self.structure.nodes():
            return
        
        # Find root (node with no incoming edges)
        roots = [n for n in self.structure.nodes() if self.structure.in_degree(n) == 0]
        
        depths = {}
        for root in roots:
            for node in self.structure.nodes():
                try:
                    path_length = nx.shortest_path_length(self.structure, root, node)
                    depths[node] = max(depths.get(node, 0), path_length)
                except nx.NetworkXNoPath:
                    pass
        
        print(f"\n{'='*60}")
        print(f"DEPTH ANALYSIS: {self.name}")
        print(f"{'='*60}\n")
        
        max_depth = max(depths.values()) if depths else 0
        avg_depth = sum(depths.values()) / len(depths) if depths else 0
        
        print(f"Maximum depth: {max_depth}")
        print(f"Average depth: {avg_depth:.1f}")
        
        # Recommendation (3-click rule: important content within 3 clicks)
        if max_depth > 3:
            print(f"\n⚠ WARNING: Some content requires {max_depth} clicks")
            print("  Recommendation: Flatten hierarchy or add shortcuts")
        else:
            print(f"\n✓ GOOD: All content reachable within 3 clicks")
        
        # Show deepest pages
        deep_pages = [page for page, depth in depths.items() if depth == max_depth]
        if deep_pages:
            print(f"\nDeepest pages ({max_depth} clicks):")
            for page in deep_pages[:5]:
                print(f"  • {page}")
    
    def analyze_breadth(self):
        """Analyze breadth (too many choices = overwhelming)"""
        print(f"\n{'='*60}")
        print(f"BREADTH ANALYSIS: {self.name}")
        print(f"{'='*60}\n")
        
        # Children per parent
        breadths = {}
        for node in self.structure.nodes():
            children = list(self.structure.successors(node))
            if children:
                breadths[node] = len(children)
        
        if not breadths:
            print("No hierarchy defined")
            return
        
        max_breadth = max(breadths.values())
        avg_breadth = sum(breadths.values()) / len(breadths)
        
        print(f"Maximum breadth: {max_breadth} items")
        print(f"Average breadth: {avg_breadth:.1f} items")
        
        # Miller's Law: 7±2 items in working memory
        if max_breadth > 9:
            print(f"\n⚠ WARNING: Some menus have {max_breadth} items (exceeds 7±2 rule)")
            print("  Recommendation: Group items into categories")
        else:
            print(f"\n✓ GOOD: Menu sizes manageable")
        
        # Show widest menus
        wide_menus = sorted(breadths.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"\nWidest menus:")
        for page, width in wide_menus:
            print(f"  • {page}: {width} items")
    
    def analyze_findability(self):
        """Analyze how easy it is to find content"""
        print(f"\n{'='*60}")
        print(f"FINDABILITY ANALYSIS: {self.name}")
        print(f"{'='*60}\n")
        
        # How many categories?
        categories = set(item.category for item in self.content_items)
        print(f"Categories: {len(categories)}")
        
        # Items per category
        from collections import Counter
        category_counts = Counter(item.category for item in self.content_items)
        
        print(f"\nItems per category:")
        for category, count in category_counts.most_common():
            print(f"  • {category}: {count} items")
        
        # Tagging coverage
        tagged = sum(1 for item in self.content_items if item.tags)
        tagging_rate = tagged / len(self.content_items) if self.content_items else 0
        
        print(f"\nTagging:")
        print(f"  Items with tags: {tagged}/{len(self.content_items)} ({tagging_rate:.0%})")
        
        if tagging_rate < 0.8:
            print("  ⚠ Recommendation: Improve tagging for better findability")

# Example: Documentation site IA
ia = InformationArchitecture("Developer Documentation")

# Build hierarchy
ia.add_page("home")
ia.add_page("getting-started", "home")
ia.add_page("guides", "home")
ia.add_page("api-reference", "home")
ia.add_page("tutorials", "home")

# Getting Started
ia.add_page("installation", "getting-started")
ia.add_page("quickstart", "getting-started")
ia.add_page("configuration", "getting-started")

# Guides (too many direct children - breadth issue)
ia.add_page("authentication", "guides")
ia.add_page("database", "guides")
ia.add_page("caching", "guides")
ia.add_page("deployment", "guides")
ia.add_page("monitoring", "guides")
ia.add_page("security", "guides")
ia.add_page("testing", "guides")
ia.add_page("performance", "guides")
ia.add_page("troubleshooting", "guides")
ia.add_page("migration", "guides")  # 10 items - too many!

# API Reference (good hierarchy)
ia.add_page("core-api", "api-reference")
ia.add_page("plugin-api", "api-reference")
ia.add_page("core-classes", "core-api")
ia.add_page("core-functions", "core-api")

# Deep nesting issue
ia.add_page("advanced-config", "configuration")
ia.add_page("env-variables", "advanced-config")
ia.add_page("custom-loaders", "env-variables")  # 5 clicks deep!

# Add some content
ia.add_content(ContentItem(
    id="auth-1",
    title="OAuth2 Setup",
    category="authentication",
    tags=["oauth", "security", "api"]
))

ia.add_content(ContentItem(
    id="db-1",
    title="Connection Pooling",
    category="database",
    tags=["performance", "database"]
))

# Analyze
ia.analyze_depth()
ia.analyze_breadth()
ia.analyze_findability()

# Show example navigation path
path = ia.find_path("home", "custom-loaders")
if path:
    print(f"\nExample path:")
    print(f"  {path} ({path.depth()} clicks)")
```

---

## 20.3 Interaction Design

### 20.3.1 Affordances and Signifiers

**Theory:**

**Affordance**: What actions an object permits (independent of discoverability)
- Button affords pressing
- Scrollbar affords scrolling

**Signifier**: Communicates where action should take place
- Underlined text signifies link
- Drop shadow signifies clickable button

**Feedback**: System response to user action
- Visual (button depression, color change)
- Auditory (click sound)
- Haptic (vibration)

**Constraints**: Limit possible actions
- Physical (can't scroll beyond content)
- Logical (can't submit invalid form)
- Cultural (red = stop, green = go)

**WHY it matters:**

1. **Discoverability**: Users know what's possible
2. **Learnability**: Interface is self-explanatory
3. **Error Prevention**: Constraints prevent mistakes
4. **Efficiency**: Clear affordances → fast interaction
5. **Confidence**: Users feel in control

**Example - Interaction Design Patterns:**

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class FeedbackType(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    HAPTIC = "haptic"
    TEXTUAL = "textual"

class ConstraintType(Enum):
    PHYSICAL = "physical"
    LOGICAL = "logical"
    CULTURAL = "cultural"

@dataclass
class InteractionPattern:
    """
    Document interaction design pattern.
    """
    name: str
    description: str
    affordances: List[str]
    signifiers: List[str]
    feedback: Dict[str, FeedbackType]
    constraints: List[tuple[str, ConstraintType]]
    example_code: Optional[str] = None
    
    def document(self):
        print(f"\n{'='*60}")
        print(f"INTERACTION PATTERN: {self.name}")
        print(f"{'='*60}\n")
        
        print(f"Description:\n  {self.description}\n")
        
        print("AFFORDANCES (what actions are possible):")
        for affordance in self.affordances:
            print(f"  • {affordance}")
        
        print("\nSIGNIFIERS (how users know what to do):")
        for signifier in self.signifiers:
            print(f"  • {signifier}")
        
        print("\nFEEDBACK (system responses):")
        for action, feedback_type in self.feedback.items():
            print(f"  • {action} → {feedback_type.value}")
        
        print("\nCONSTRAINTS (what's prevented):")
        for constraint, constraint_type in self.constraints:
            print(f"  • [{constraint_type.value}] {constraint}")
        
        if self.example_code:
            print(f"\nEXAMPLE CODE:")
            print(self.example_code)

# Example patterns
button_pattern = InteractionPattern(
    name="Primary Action Button",
    description="High-prominence button for primary user action (e.g., Submit, Buy, Continue)",
    affordances=[
        "Can be clicked/tapped",
        "Can receive keyboard focus",
        "Can be activated via Enter key"
    ],
    signifiers=[
        "Distinct background color (e.g., blue/green)",
        "Raised appearance (drop shadow)",
        "Cursor changes to pointer on hover",
        "Button text is action-oriented verb"
    ],
    feedback={
        "hover": FeedbackType.VISUAL,
        "press": FeedbackType.VISUAL,
        "click": FeedbackType.VISUAL,
        "success": FeedbackType.TEXTUAL,
        "error": FeedbackType.TEXTUAL
    },
    constraints=[
        ("Disabled when form invalid", ConstraintType.LOGICAL),
        ("Cannot be clicked while loading", ConstraintType.LOGICAL),
        ("Only one primary button per screen", ConstraintType.CULTURAL)
    ],
    example_code="""
<!-- HTML/CSS -->
<button class="btn-primary" onclick="submitForm()">
  Submit Order
</button>

<style>
.btn-primary {
  background: #007bff;
  color: white;
  padding: 12px 24px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #0056b3;
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
  box-shadow: none;
}
</style>
    """.strip()
)

form_validation_pattern = InteractionPattern(
    name="Inline Form Validation",
    description="Real-time feedback on form field validity as user types",
    affordances=[
        "User can enter text",
        "User can see validation status",
        "User can correct errors immediately"
    ],
    signifiers=[
        "Red border/text for errors",
        "Green checkmark for valid input",
        "Error message below field",
        "Required fields marked with asterisk"
    ],
    feedback={
        "invalid_input": FeedbackType.VISUAL,
        "valid_input": FeedbackType.VISUAL,
        "typing": FeedbackType.VISUAL,
        "submit_attempt_with_errors": FeedbackType.TEXTUAL
    },
    constraints=[
        ("Email must match pattern", ConstraintType.LOGICAL),
        ("Password minimum length", ConstraintType.LOGICAL),
        ("Can't submit with errors", ConstraintType.LOGICAL)
    ],
    example_code="""
<!-- HTML -->
<div class="form-field">
  <label for="email">Email *</label>
  <input 
    type="email" 
    id="email" 
    onblur="validateEmail(this)"
    oninput="clearError(this)"
  />
  <span class="error-message" id="email-error"></span>
  <span class="success-indicator">✓</span>
</div>

<script>
function validateEmail(input) {
  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  const errorSpan = document.getElementById('email-error');
  const successIcon = input.nextElementSibling.nextElementSibling;
  
  if (!emailRegex.test(input.value)) {
    input.classList.add('invalid');
    input.classList.remove('valid');
    errorSpan.textContent = 'Please enter a valid email address';
    successIcon.style.display = 'none';
  } else {
    input.classList.remove('invalid');
    input.classList.add('valid');
    errorSpan.textContent = '';
    successIcon.style.display = 'inline';
  }
}
</script>

<style>
.form-field input.invalid {
  border: 2px solid #dc3545;
}

.form-field input.valid {
  border: 2px solid #28a745;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 4px;
}

.success-indicator {
  color: #28a745;
  display: none;
}
</style>
    """.strip()
)

# Document patterns
button_pattern.document()
form_validation_pattern.document()

print("\n→ Well-designed interactions are discoverable, provide feedback, and prevent errors")
```

---

## 20.4 Visual Design Principles

### 20.4.1 Visual Hierarchy and Layout

**Theory:**

Visual hierarchy: arrangement of elements to show importance.

**Techniques:**
1. **Size**: Larger = more important
2. **Color**: High contrast draws attention
3. **Position**: Top-left scanned first (F-pattern, Z-pattern)
4. **Whitespace**: Breathing room emphasizes elements
5. **Typography**: Weight, size, font family
6. **Grouping**: Related items together (Gestalt principles)

**Gestalt Principles:**
- **Proximity**: Near objects grouped together
- **Similarity**: Similar objects grouped together
- **Closure**: Mind completes incomplete shapes
- **Continuity**: Eye follows lines/curves
- **Figure/Ground**: Distinguish object from background

**WHY it matters:**

1. **Scannability**: Users quickly find information
2. **Focus**: Direct attention to important elements
3. **Comprehension**: Structure aids understanding
4. **Aesthetics**: Professional, polished appearance
5. **Accessibility**: Clear hierarchy aids screen readers

**Example - Visual Design Analysis:**

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class DesignIssueType(Enum):
    HIERARCHY = "hierarchy"
    CONTRAST = "contrast"
    SPACING = "spacing"
    TYPOGRAPHY = "typography"
    COLOR = "color"
    ACCESSIBILITY = "accessibility"

class SeverityLevel(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"

@dataclass
class DesignIssue:
    """Visual design issue found in review"""
    type: DesignIssueType
    severity: SeverityLevel
    description: str
    location: str
    recommendation: str
    
    def __str__(self):
        severity_symbol = {
            SeverityLevel.CRITICAL: "🔴",
            SeverityLevel.MAJOR: "🟡",
            SeverityLevel.MINOR: "🟢"
        }
        
        return f"""
{severity_symbol[self.severity]} [{self.severity.value.upper()}] {self.type.value.title()} Issue
  Location: {self.location}
  Problem: {self.description}
  Fix: {self.recommendation}
        """.strip()

class VisualDesignReview:
    """
    Framework for reviewing visual design quality.
    """
    
    def __init__(self, page_name: str):
        self.page_name = page_name
        self.issues: List[DesignIssue] = []
    
    def add_issue(self, issue: DesignIssue):
        """Record design issue"""
        self.issues.append(issue)
    
    def check_contrast_ratio(self, foreground_rgb: tuple, background_rgb: tuple) -> float:
        """
        Calculate WCAG contrast ratio.
        
        Minimum ratios:
        - 4.5:1 for normal text
        - 3:1 for large text (18pt+ or 14pt+ bold)
        - 7:1 for AAA compliance
        """
        def luminance(rgb):
            # Convert RGB to relative luminance
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = luminance(foreground_rgb)
        l2 = luminance(background_rgb)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def analyze_typography(self):
        """Check typography best practices"""
        print(f"\n{'='*60}")
        print(f"TYPOGRAPHY ANALYSIS")
        print(f"{'='*60}\n")
        
        typography_checklist = [
            ("Font size at least 16px for body text", True),
            ("Line height 1.5-1.6 for readability", True),
            ("Line length 50-75 characters", False),
            ("Use max 2-3 font families", True),
            ("Heading hierarchy clear (h1 > h2 > h3)", False),
        ]
        
        for check, passes in typography_checklist:
            status = "✓" if passes else "✗"
            print(f"  {status} {check}")
    
    def analyze_color_accessibility(self):
        """Check color contrast for accessibility"""
        print(f"\n{'='*60}")
        print(f"COLOR ACCESSIBILITY ANALYSIS")
        print(f"{'='*60}\n")
        
        # Example color combinations to check
        color_pairs = [
            ("Body text", (51, 51, 51), (255, 255, 255)),  # Dark gray on white
            ("Primary button", (255, 255, 255), (0, 123, 255)),  # White on blue
            ("Error message", (255, 0, 0), (255, 255, 255)),  # Red on white
            ("Link text", (0, 0, 238), (255, 255, 255)),  # Blue on white
        ]
        
        for label, fg, bg in color_pairs:
            ratio = self.check_contrast_ratio(fg, bg)
            
            # Determine compliance
            if ratio >= 7:
                compliance = "AAA"
            elif ratio >= 4.5:
                compliance = "AA"
            elif ratio >= 3:
                compliance = "AA Large Text"
            else:
                compliance = "FAIL"
            
            status = "✓" if ratio >= 4.5 else "✗"
            print(f"  {status} {label}: {ratio:.2f}:1 ({compliance})")
            
            if ratio < 4.5:
                self.add_issue(DesignIssue(
                    type=DesignIssueType.ACCESSIBILITY,
                    severity=SeverityLevel.CRITICAL,
                    description=f"Insufficient contrast ratio ({ratio:.2f}:1, need 4.5:1)",
                    location=label,
                    recommendation="Darken foreground or lighten background to meet WCAG AA"
                ))
    
    def generate_report(self):
        """Generate design review report"""
        print(f"\n{'='*60}")
        print(f"DESIGN REVIEW REPORT: {self.page_name}")
        print(f"{'='*60}\n")
        
        if not self.issues:
            print("✓ No major issues found")
            return
        
        # Group by severity
        critical = [i for i in self.issues if i.severity == SeverityLevel.CRITICAL]
        major = [i for i in self.issues if i.severity == SeverityLevel.MAJOR]
        minor = [i for i in self.issues if i.severity == SeverityLevel.MINOR]
        
        print(f"Total issues: {len(self.issues)}")
        print(f"  Critical: {len(critical)}")
        print(f"  Major: {len(major)}")
        print(f"  Minor: {len(minor)}")
        
        if critical:
            print(f"\nCRITICAL ISSUES (fix immediately):")
            for issue in critical:
                print(issue)
                print()
        
        if major:
            print(f"\nMAJOR ISSUES (fix soon):")
            for issue in major:
                print(issue)
                print()

# Example: Review login page design
review = VisualDesignReview("Login Page")

# Add example issues
review.add_issue(DesignIssue(
    type=DesignIssueType.HIERARCHY,
    severity=SeverityLevel.MAJOR,
    description="Primary CTA button same size as secondary link",
    location="Login form",
    recommendation="Make 'Sign In' button larger and more prominent than 'Forgot Password' link"
))

review.add_issue(DesignIssue(
    type=DesignIssueType.SPACING,
    severity=SeverityLevel.MINOR,
    description="Inconsistent spacing between form fields (12px, 16px, 20px)",
    location="Form inputs",
    recommendation="Use consistent 16px spacing between all fields"
))

review.add_issue(DesignIssue(
    type=DesignIssueType.TYPOGRAPHY,
    severity=SeverityLevel.MAJOR,
    description="Error messages too small (12px)",
    location="Validation errors",
    recommendation="Increase to 14px minimum for readability"
))

# Run analyses
review.analyze_typography()
review.analyze_color_accessibility()

# Generate report
review.generate_report()

print("\n→ Systematic design review ensures quality and accessibility")
```

---

## 20.5 User Experience Metrics

**Theory:**

UX metrics quantify user experience quality.

**Categories:**

1. **Task Success**: Can users complete tasks?
   - Success rate
   - Error rate
   - Task completion time

2. **Efficiency**: How quickly can users work?
   - Time on task
   - Number of clicks/steps
   - Error recovery time

3. **Satisfaction**: How do users feel?
   - NPS (Net Promoter Score)
   - CSAT (Customer Satisfaction)
   - SUS (System Usability Scale)

4. **Engagement**: Do users return?
   - DAU/MAU (Daily/Monthly Active Users)
   - Session duration
   - Return rate

**WHY it matters:**

1. **Measurement**: "If you can't measure it, you can't improve it"
2. **Prioritization**: Focus on biggest impact
3. **Validation**: Did changes actually help?
4. **Alignment**: Connect UX to business goals
5. **Communication**: Show UX value to stakeholders

**Example - UX Metrics Dashboard:**

```python
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class UXMetric:
    """Individual UX metric"""
    name: str
    value: float
    target: float
    unit: str
    trend: str  # "up", "down", "stable"
    
    def status(self):
        """Check if metric meets target"""
        if self.value >= self.target:
            return "✓ ON TARGET"
        elif self.value >= self.target * 0.9:
            return "⚠ CLOSE"
        else:
            return "✗ BELOW TARGET"
    
    def __str__(self):
        trend_symbol = {"up": "↑", "down": "↓", "stable": "→"}
        return f"{self.name}: {self.value}{self.unit} (target: {self.target}{self.unit}) {trend_symbol[self.trend]} {self.status()}"

class UXMetricsDashboard:
    """
    Track and report UX metrics.
    """
    
    def __init__(self, product_name: str):
        self.product_name = product_name
        self.metrics = {}
    
    def add_metric(self, category: str, metric: UXMetric):
        """Add metric to dashboard"""
        if category not in self.metrics:
            self.metrics[category] = []
        self.metrics[category].append(metric)
    
    def calculate_sus_score(self, responses: List[int]) -> float:
        """
        Calculate System Usability Scale score.
        
        SUS: 10-question survey, 1-5 scale
        Odd questions (1,3,5,7,9): positive
        Even questions (2,4,6,8,10): negative
        
        Score 0-100, average is 68
        """
        if len(responses) != 10:
            raise ValueError("SUS requires 10 responses")
        
        score = 0
        for i, response in enumerate(responses):
            if i % 2 == 0:  # Odd question (0-indexed, so even index)
                score += response - 1
            else:  # Even question
                score += 5 - response
        
        return score * 2.5  # Scale to 0-100
    
    def calculate_nps(self, scores: List[int]) -> float:
        """
        Calculate Net Promoter Score.
        
        NPS: "How likely to recommend?" (0-10 scale)
        Promoters (9-10): Enthusiastic
        Passives (7-8): Satisfied but unenthusiastic
        Detractors (0-6): Unhappy
        
        NPS = % Promoters - % Detractors (range: -100 to 100)
        """
        promoters = sum(1 for s in scores if s >= 9)
        detractors = sum(1 for s in scores if s <= 6)
        
        nps = ((promoters - detractors) / len(scores)) * 100
        return nps
    
    def report(self):
        """Generate metrics report"""
        print(f"\n{'='*60}")
        print(f"UX METRICS DASHBOARD: {self.product_name}")
        print(f"{'='*60}\n")
        
        for category, metrics in self.metrics.items():
            print(f"\n{category.upper()}")
            print("-" * 60)
            for metric in metrics:
                print(f"  {metric}")
        
        # Overall health
        all_metrics = [m for metrics in self.metrics.values() for m in metrics]
        on_target = sum(1 for m in all_metrics if m.value >= m.target)
        total = len(all_metrics)
        
        health_percentage = (on_target / total * 100) if total > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"OVERALL HEALTH: {on_target}/{total} metrics on target ({health_percentage:.0f}%)")
        print(f"{'='*60}")

# Example: E-commerce checkout metrics
dashboard = UXMetricsDashboard("E-commerce Checkout")

# Task Success metrics
dashboard.add_metric("Task Success", UXMetric(
    name="Checkout Completion Rate",
    value=72.5,
    target=75.0,
    unit="%",
    trend="up"
))

dashboard.add_metric("Task Success", UXMetric(
    name="Payment Error Rate",
    value=2.1,
    target=2.0,
    unit="%",
    trend="down"
))

# Efficiency metrics
dashboard.add_metric("Efficiency", UXMetric(
    name="Time to Checkout",
    value=145,
    target=120,
    unit="s",
    trend="stable"
))

dashboard.add_metric("Efficiency", UXMetric(
    name="Form Fields Required",
    value=12,
    target=10,
    unit="",
    trend="stable"
))

# Calculate SUS score
np.random.seed(42)
sus_responses = [
    np.random.randint(1, 6, 10)  # Simulate 10 responses from one user
    for _ in range(50)  # 50 users
]

average_sus = np.mean([dashboard.calculate_sus_score(r.tolist()) for r in sus_responses])

dashboard.add_metric("Satisfaction", UXMetric(
    name="System Usability Scale (SUS)",
    value=average_sus,
    target=70.0,
    unit="",
    trend="up"
))

# Calculate NPS
nps_scores = [np.random.randint(0, 11) for _ in range(100)]
nps = dashboard.calculate_nps(nps_scores)

dashboard.add_metric("Satisfaction", UXMetric(
    name="Net Promoter Score (NPS)",
    value=nps,
    target=30.0,
    unit="",
    trend="up"
))

# Engagement metrics
dashboard.add_metric("Engagement", UXMetric(
    name="Return Customer Rate",
    value=45.2,
    target=50.0,
    unit="%",
    trend="stable"
))

# Generate report
dashboard.report()

print("\n→ UX metrics provide objective evidence of user experience quality")
```

**Connections to Other Topics:**

- **Part 17 (Statistics)**: A/B testing for UX improvements
- **Part 19 (Research)**: User research methods
- **Part 12 (Monitoring)**: Analytics and instrumentation
- **Part 21 (Communication)**: Presenting UX findings

---

*[Continuing with Parts 21-22...]*

# PART 21: LEADERSHIP & SOFT SKILLS

Technical mastery alone doesn't make a scientist-level engineer. Leadership, communication, and collaboration amplify individual impact through teams.

## 21.1 Mentorship

### 21.1.1 Code Review as Teaching

**Theory:**

Code review: not just quality gate, but learning opportunity.

**Effective code review:**
1. **Explain the "why"**: Don't just say what's wrong, explain why
2. **Ask questions**: Socratic method encourages thinking
3. **Provide context**: Link to docs, examples, best practices
4. **Balance praise and critique**: Recognize good work
5. **Be specific**: Point to exact lines, suggest alternatives
6. **Prioritize**: Critical bugs vs style preferences

**Review levels:**
- **Automated**: Linters, formatters, tests
- **Peer review**: Code quality, design, maintainability
- **Architectural review**: System-level concerns

**WHY it matters:**

1. **Knowledge Transfer**: Spread best practices across team
2. **Code Quality**: Catch bugs, improve design
3. **Team Growth**: Develop junior engineers
4. **Consistency**: Maintain codebase standards
5. **Collaboration**: Build shared understanding

**Example - Code Review Framework:**

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class ReviewCategory(Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    LEARNING = "learning"

class ReviewPriority(Enum):
    MUST_FIX = "must_fix"  # Block merge
    SHOULD_FIX = "should_fix"  # Important but not blocking
    CONSIDER = "consider"  # Suggestion for improvement
    PRAISE = "praise"  # Positive feedback

@dataclass
class CodeReviewComment:
    """Structured code review comment"""
    category: ReviewCategory
    priority: ReviewPriority
    line_number: int
    comment: str
    explanation: str
    suggestion: str = ""
    resource_link: str = ""
    
    def format(self):
        """Format comment for clarity"""
        priority_icons = {
            ReviewPriority.MUST_FIX: "🔴",
            ReviewPriority.SHOULD_FIX: "🟡",
            ReviewPriority.CONSIDER: "💡",
            ReviewPriority.PRAISE: "✅"
        }
        
        output = f"""
{priority_icons[self.priority]} Line {self.line_number} - {self.category.value.upper()}

{self.comment}

WHY: {self.explanation}
        """.strip()
        
        if self.suggestion:
            output += f"\n\nSUGGESTION:\n{self.suggestion}"
        
        if self.resource_link:
            output += f"\n\nREFERENCE: {self.resource_link}"
        
        return output

class CodeReview:
    """
    Structured code review with teaching focus.
    """
    
    def __init__(self, pr_title: str, author: str):
        self.pr_title = pr_title
        self.author = author
        self.comments: List[CodeReviewComment] = []
        self.overall_feedback = ""
    
    def add_comment(self, comment: CodeReviewComment):
        """Add review comment"""
        self.comments.append(comment)
    
    def generate_review(self):
        """Generate complete review"""
        print(f"\n{'='*60}")
        print(f"CODE REVIEW: {self.pr_title}")
        print(f"Author: {self.author}")
        print(f"{'='*60}\n")
        
        # Summary
        must_fix = [c for c in self.comments if c.priority == ReviewPriority.MUST_FIX]
        should_fix = [c for c in self.comments if c.priority == ReviewPriority.SHOULD_FIX]
        suggestions = [c for c in self.comments if c.priority == ReviewPriority.CONSIDER]
        praise = [c for c in self.comments if c.priority == ReviewPriority.PRAISE]
        
        print("SUMMARY:")
        print(f"  🔴 Must fix: {len(must_fix)}")
        print(f"  🟡 Should fix: {len(should_fix)}")
        print(f"  💡 Suggestions: {len(suggestions)}")
        print(f"  ✅ Praise: {len(praise)}")
        
        # Blocking?
        if must_fix:
            print(f"\n⚠ CHANGES REQUESTED - Please address must-fix items before merging")
        else:
            print(f"\n✅ APPROVED with suggestions")
        
        # Comments by category
        for category in ReviewCategory:
            category_comments = [c for c in self.comments if c.category == category]
            if category_comments:
                print(f"\n{category.value.upper()} ({len(category_comments)} comments)")
                print("-" * 60)
                for comment in category_comments:
                    print(comment.format())
                    print()
        
        # Overall feedback
        if self.overall_feedback:
            print(f"\n{'='*60}")
            print("OVERALL FEEDBACK:")
            print(f"{'='*60}\n")
            print(self.overall_feedback)

# Example: Review of API endpoint implementation
review = CodeReview(
    pr_title="Add user authentication endpoint",
    author="junior_dev"
)

# Critical security issue
review.add_comment(CodeReviewComment(
    category=ReviewCategory.SECURITY,
    priority=ReviewPriority.MUST_FIX,
    line_number=42,
    comment="Password is being logged in plain text",
    explanation="""
    Logging passwords is a critical security vulnerability. Even in development logs,
    this exposes user credentials. Logs may be stored, transmitted, or accessed by
    unauthorized parties.
    """,
    suggestion="""
    # Before
    logger.info(f"Login attempt: {username} with password {password}")
    
    # After
    logger.info(f"Login attempt: {username}")
    """,
    resource_link="https://owasp.org/www-community/vulnerabilities/Logging_Credentials"
))

# Performance concern
review.add_comment(CodeReviewComment(
    category=ReviewCategory.PERFORMANCE,
    priority=ReviewPriority.SHOULD_FIX,
    line_number=67,
    comment="Database query inside loop (N+1 query problem)",
    explanation="""
    This code makes one database query per user, leading to N+1 queries total.
    For 100 users, that's 101 queries instead of 2. This will cause severe performance
    issues as data grows.
    """,
    suggestion="""
    # Before (N+1 queries)
    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        process(user)
    
    # After (2 queries)
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    for user in users:
        process(user)
    """,
    resource_link="https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem"
))

# Maintainability suggestion
review.add_comment(CodeReviewComment(
    category=ReviewCategory.MAINTAINABILITY,
    priority=ReviewPriority.CONSIDER,
    line_number=23,
    comment="Consider extracting validation logic to separate function",
    explanation="""
    The validation logic is mixing input validation, business rules, and database
    checks. Extracting to a dedicated function would improve:
    - Testability (can unit test validation separately)
    - Reusability (can use in other endpoints)
    - Readability (clearer separation of concerns)
    """,
    suggestion="""
    def validate_user_registration(data):
        if not data.get('email'):
            raise ValidationError("Email required")
        if not is_valid_email(data['email']):
            raise ValidationError("Invalid email format")
        if user_exists(data['email']):
            raise ValidationError("Email already registered")
        return True
    
    # Then in endpoint:
    validate_user_registration(request_data)
    """,
))

# Positive feedback
review.add_comment(CodeReviewComment(
    category=ReviewCategory.LEARNING,
    priority=ReviewPriority.PRAISE,
    line_number=15,
    comment="Great use of type hints!",
    explanation="""
    Adding type hints makes the code more maintainable and helps catch bugs early.
    This is a best practice that improves code quality. Well done!
    """,
))

review.add_comment(CodeReviewComment(
    category=ReviewCategory.LEARNING,
    priority=ReviewPriority.PRAISE,
    line_number=89,
    comment="Excellent error handling",
    explanation="""
    You've correctly used try/except blocks and are returning meaningful error messages
    to the client. This will make debugging much easier for API consumers.
    """,
))

# Overall feedback
review.overall_feedback = """
Great first API implementation! The overall structure is solid and you're following
REST conventions well. 

The main areas to address:
1. Security: Never log sensitive data like passwords
2. Performance: Watch out for N+1 queries as they'll cause issues at scale

These are common mistakes that even experienced developers make, so don't worry!
The important thing is learning to recognize and fix them.

Keep up the good work with type hints and error handling - those are excellent
practices that will serve you well.

Feel free to reach out if you have questions about any of these suggestions!
"""

# Generate review
review.generate_review()

print("\n→ Good code reviews teach, don't just criticize")
```

---

## 21.2 Technical Communication

### 21.2.1 Writing Technical Specifications

**Theory:**

Technical spec: blueprint for implementing a feature or system.

**Structure:**
1. **Overview**: What, why, who
2. **Goals/Non-Goals**: Scope boundaries
3. **Background**: Context, problem statement
4. **Proposal**: Detailed design
5. **Alternatives Considered**: Why this approach?
6. **Testing Plan**: How to validate
7. **Rollout Plan**: Deployment strategy
8. **Risks/Mitigations**: What could go wrong?

**Principles:**
- **Clarity**: Technical but understandable
- **Completeness**: Answers key questions
- **Conciseness**: No unnecessary detail
- **Reviewable**: Easy to give feedback
- **Living Document**: Update as decisions evolve

**WHY it matters:**

1. **Alignment**: Team understands plan
2. **Review**: Get feedback before implementation
3. **Documentation**: Record decisions
4. **Onboarding**: New team members understand system
5. **Accountability**: Clear ownership and timeline

**Example - Technical Spec Template:**

```python
class TechnicalSpecification:
    """
    Template for technical specification document.
    """
    
    @staticmethod
    def generate_template():
        template = """
# Technical Specification: [Feature/System Name]

**Author**: [Your Name]
**Reviewers**: [List reviewers]
**Status**: Draft | In Review | Approved | Implemented
**Last Updated**: [Date]

---

## 1. OVERVIEW

### 1.1 Summary (TL;DR)
[2-3 sentence summary of what you're building and why]

Example:
  "We're adding Redis caching to the user profile API to reduce database load
   and improve response times. Current P95 latency is 450ms; target is <100ms.
   This will handle projected 10x traffic growth over next year."

### 1.2 Background
- **Problem**: [What's broken or missing?]
- **Impact**: [Who's affected? How much?]
- **Current State**: [What exists today?]
- **Desired State**: [What should exist?]

### 1.3 Goals
- [ ] Goal 1: [Specific, measurable]
- [ ] Goal 2: [Specific, measurable]
- [ ] Goal 3: [Specific, measurable]

### 1.4 Non-Goals
- ✗ Not doing X because [reason]
- ✗ Not doing Y because [reason]

---

## 2. REQUIREMENTS

### 2.1 Functional Requirements
- **FR1**: System shall [specific behavior]
- **FR2**: User can [specific action]
- **FR3**: API will [specific response]

### 2.2 Non-Functional Requirements
- **Performance**: P95 latency < 100ms
- **Scalability**: Support 10,000 requests/second
- **Availability**: 99.9% uptime
- **Security**: [Security requirements]

### 2.3 Constraints
- Must work with existing PostgreSQL database
- Cannot require application downtime
- Must be backwards compatible with v1 API
- Budget: $X for infrastructure

---

## 3. PROPOSED SOLUTION

### 3.1 High-Level Design

[Architecture diagram here]

**Components:**
1. **Component A**: [Description]
2. **Component B**: [Description]
3. **Component C**: [Description]

**Data Flow:**
```
Client → Load Balancer → API Server → Cache → Database
         ↓                           ↓
      Logs                      Monitoring
```

### 3.2 Detailed Design

#### 3.2.1 Cache Layer
- **Technology**: Redis Cluster (5 nodes)
- **Eviction Policy**: LRU (Least Recently Used)
- **TTL**: 5 minutes for hot data, 1 hour for cold data
- **Key Format**: `user:profile:{user_id}`

#### 3.2.2 Cache Invalidation Strategy
- **Write-through**: Update cache on write
- **Invalidation**: Delete from cache on user update
- **Bulk invalidation**: Admin endpoint for cache flush

#### 3.2.3 Fallback Behavior
- Cache miss → fetch from database → populate cache
- Cache failure → bypass cache, serve from database
- Graceful degradation (no errors to user)

### 3.3 API Changes

**Before:**
```python
GET /api/users/{user_id}/profile
Response: { "id": 123, "name": "John", ... }
```

**After (same interface, faster):**
```python
GET /api/users/{user_id}/profile
X-Cache-Hit: true  # New header
Response: { "id": 123, "name": "John", ... }
```

### 3.4 Database Schema Changes
[List any schema changes, migrations]

---

## 4. ALTERNATIVES CONSIDERED

### 4.1 Alternative 1: In-Memory Application Cache
**Pros:**
- Simpler deployment
- No external dependency

**Cons:**
- Doesn't scale across multiple servers
- Lost on application restart
- Memory pressure on app servers

**Decision**: Rejected because we need shared cache across instances

### 4.2 Alternative 2: Memcached
**Pros:**
- Simple, mature technology
- Low operational overhead

**Cons:**
- No persistence (lost on restart)
- Limited data structures (string only)
- No built-in clustering

**Decision**: Rejected in favor of Redis for persistence and richer features

---

## 5. TESTING PLAN

### 5.1 Unit Tests
- Cache hit/miss scenarios
- Invalidation logic
- Fallback behavior

### 5.2 Integration Tests
- End-to-end API calls with cache
- Cache failure scenarios
- Load testing

### 5.3 Performance Benchmarks
- Latency: P50, P95, P99
- Throughput: requests/second
- Cache hit rate

### 5.4 Success Metrics
- [ ] P95 latency < 100ms (baseline: 450ms)
- [ ] Cache hit rate > 80%
- [ ] Database queries reduced by 70%
- [ ] No increase in error rate

---

## 6. ROLLOUT PLAN

### 6.1 Phases

**Phase 1: Infrastructure Setup (Week 1)**
- Provision Redis cluster
- Configure monitoring/alerting
- Deploy to staging environment

**Phase 2: Code Changes (Week 2)**
- Implement cache layer
- Add instrumentation
- Deploy to staging

**Phase 3: Testing (Week 3)**
- Run load tests
- Verify metrics
- Fix any issues

**Phase 4: Production Rollout (Week 4)**
- Deploy to 10% of traffic (canary)
- Monitor for 24 hours
- Gradual rollout to 100%

### 6.2 Rollback Plan
- Feature flag to disable cache
- Fallback to database-only mode
- Zero downtime rollback

### 6.3 Monitoring
- Cache hit rate dashboard
- Latency percentiles
- Error rate alerts
- Redis cluster health

---

## 7. RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Cache stampede (many requests for expired key) | High | Medium | Implement locking mechanism |
| Redis cluster failure | High | Low | Automatic failover + fallback to DB |
| Stale data served from cache | Medium | Medium | Short TTLs + invalidation on write |
| Increased operational complexity | Low | High | Comprehensive runbook + training |

---

## 8. DEPENDENCIES

- Redis 7.0 (requires infrastructure team)
- Monitoring setup (requires SRE team)
- Load testing environment (requires QA team)

---

## 9. TIMELINE

| Milestone | Date | Owner | Status |
|-----------|------|-------|--------|
| Spec review | 2024-01-15 | [Name] | ✅ |
| Infrastructure provisioned | 2024-01-22 | [Name] | ⏳ |
| Code complete | 2024-01-29 | [Name] | 📋 |
| Testing complete | 2024-02-05 | [Name] | 📋 |
| Production rollout | 2024-02-12 | [Name] | 📋 |

---

## 10. OPEN QUESTIONS

- [ ] Q: What's the expected cache hit rate?
      A: [TBD - need to analyze access patterns]

- [ ] Q: How to handle cache warmup on deployment?
      A: [TBD - discussing pre-warming vs lazy loading]

---

## 11. APPENDIX

### A. References
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [Caching Strategies](https://aws.amazon.com/caching/)
- [Internal wiki: Cache Architecture]

### B. Prototyping Results
[Link to prototype, performance benchmarks]

### C. Team Feedback
[Summarize feedback from design review meeting]

---

## CHANGELOG

- 2024-01-10: Initial draft
- 2024-01-12: Added alternative analysis
- 2024-01-15: Updated after design review
        """
        
        return template

# Example usage
spec = TechnicalSpecification()
print(spec.generate_template())

print("\n→ Good specs prevent surprises and align teams before coding starts")
```

---

## 21.3 Project Management

### 21.3.1 Agile Ceremonies

**Theory:**

Agile ceremonies: structured meetings for team coordination.

**Scrum ceremonies:**
1. **Sprint Planning**: Plan work for sprint
2. **Daily Standup**: 15-min sync (what/blockers)
3. **Sprint Review**: Demo completed work
4. **Sprint Retrospective**: Improve process

**Kanban:**
- Continuous flow (no fixed sprints)
- WIP (work in progress) limits
- Pull system

**WHY it matters:**

1. **Alignment**: Team shares understanding
2. **Visibility**: Progress transparent
3. **Adaptation**: Regular course correction
4. **Continuous Improvement**: Learn and iterate
5. **Accountability**: Clear commitments

**Example - Sprint Planning Framework:**

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"

@dataclass
class Task:
    """Sprint task/user story"""
    id: str
    title: str
    description: str
    priority: TaskPriority
    story_points: int
    assignee: str = "Unassigned"
    status: TaskStatus = TaskStatus.TODO
    blockers: List[str] = None
    
    def __post_init__(self):
        if self.blockers is None:
            self.blockers = []

class Sprint:
    """
    Sprint planning and tracking.
    """
    
    def __init__(self, sprint_number: int, team_capacity: int):
        self.sprint_number = sprint_number
        self.team_capacity = team_capacity  # Total story points available
        self.tasks: List[Task] = []
    
    def add_task(self, task: Task):
        """Add task to sprint backlog"""
        self.tasks.append(task)
    
    def calculate_commitment(self):
        """Calculate total story points committed"""
        return sum(t.story_points for t in self.tasks)
    
    def sprint_planning_summary(self):
        """Generate sprint planning summary"""
        print(f"\n{'='*60}")
        print(f"SPRINT {self.sprint_number} PLANNING")
        print(f"{'='*60}\n")
        
        print(f"Team Capacity: {self.team_capacity} story points")
        
        # Group by priority
        for priority in TaskPriority:
            priority_tasks = [t for t in self.tasks if t.priority == priority]
            if priority_tasks:
                points = sum(t.story_points for t in priority_tasks)
                print(f"\n{priority.value.upper()} ({len(priority_tasks)} tasks, {points} points):")
                for task in priority_tasks:
                    print(f"  • {task.id}: {task.title} ({task.story_points} pts) - {task.assignee}")
        
        # Commitment vs capacity
        committed = self.calculate_commitment()
        utilization = (committed / self.team_capacity * 100) if self.team_capacity > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"SPRINT COMMITMENT")
        print(f"{'='*60}")
        print(f"Committed: {committed} points")
        print(f"Capacity: {self.team_capacity} points")
        print(f"Utilization: {utilization:.0f}%")
        
        if utilization > 100:
            print("⚠ WARNING: Over-committed! Risk of not completing all work.")
        elif utilization < 70:
            print("⚠ NOTE: Under-committed. Consider adding more work.")
        else:
            print("✓ Good balance between commitment and capacity.")
    
    def daily_standup_summary(self):
        """Generate daily standup summary"""
        print(f"\n{'='*60}")
        print(f"DAILY STANDUP - Sprint {self.sprint_number}")
        print(f"{'='*60}\n")
        
        # Group by status
        for status in TaskStatus:
            status_tasks = [t for t in self.tasks if t.status == status]
            if status_tasks:
                print(f"\n{status.value.upper()} ({len(status_tasks)} tasks):")
                for task in status_tasks:
                    blocker_str = f" [BLOCKED: {', '.join(task.blockers)}]" if task.blockers else ""
                    print(f"  • {task.id} ({task.assignee}): {task.title}{blocker_str}")
        
        # Velocity tracking
        done_points = sum(t.story_points for t in self.tasks if t.status == TaskStatus.DONE)
        total_points = sum(t.story_points for t in self.tasks)
        progress = (done_points / total_points * 100) if total_points > 0 else 0
        
        print(f"\nPROGRESS: {done_points}/{total_points} points complete ({progress:.0f}%)")
        
        # Blockers
        blocked_tasks = [t for t in self.tasks if t.blockers]
        if blocked_tasks:
            print(f"\n⚠ BLOCKERS ({len(blocked_tasks)} tasks blocked):")
            for task in blocked_tasks:
                print(f"  • {task.id}: {', '.join(task.blockers)}")

# Example: Sprint 23 planning
sprint = Sprint(sprint_number=23, team_capacity=40)

# Add tasks
sprint.add_task(Task(
    id="PROJ-101",
    title="Implement Redis caching for user profiles",
    description="Add caching layer to reduce DB load",
    priority=TaskPriority.CRITICAL,
    story_points=8,
    assignee="Alice"
))

sprint.add_task(Task(
    id="PROJ-102",
    title="Fix memory leak in background worker",
    description="Worker memory grows unbounded, crashes after 2 days",
    priority=TaskPriority.CRITICAL,
    story_points=5,
    assignee="Bob",
    status=TaskStatus.IN_PROGRESS
))

sprint.add_task(Task(
    id="PROJ-103",
    title="Add rate limiting to API endpoints",
    description="Prevent abuse by limiting requests per user",
    priority=TaskPriority.HIGH,
    story_points=5,
    assignee="Carol"
))

sprint.add_task(Task(
    id="PROJ-104",
    title="Upgrade PostgreSQL from 13 to 15",
    description="Get performance improvements and new features",
    priority=TaskPriority.MEDIUM,
    story_points=8,
    assignee="Dave",
    status=TaskStatus.BLOCKED,
    blockers=["Waiting for infrastructure team approval"]
))

sprint.add_task(Task(
    id="PROJ-105",
    title="Write API documentation for v2 endpoints",
    description="OpenAPI spec + examples",
    priority=TaskPriority.MEDIUM,
    story_points=3,
    assignee="Eve"
))

sprint.add_task(Task(
    id="PROJ-106",
    title="Set up automated backups for Redis",
    description="Daily backups to S3",
    priority=TaskPriority.HIGH,
    story_points=3,
    assignee="Frank",
    status=TaskStatus.DONE
))

sprint.add_task(Task(
    id="PROJ-107",
    title="Refactor authentication middleware",
    description="Clean up legacy code",
    priority=TaskPriority.LOW,
    story_points=5,
    assignee="Alice"
))

# Sprint planning
sprint.sprint_planning_summary()

# Daily standup (mid-sprint)
sprint.daily_standup_summary()

print("\n→ Agile ceremonies keep teams aligned and moving forward")
```

---

## 21.4 Cross-Functional Collaboration

**Theory:**

Software engineering requires collaboration across disciplines.

**Key partnerships:**
- **Product Managers**: Define requirements, prioritize features
- **Designers**: Create user experiences
- **DevOps/SRE**: Deploy and operate systems
- **QA**: Test and validate quality
- **Data Scientists**: Build ML models
- **Business Stakeholders**: Align on goals

**Effective collaboration:**
1. **Speak their language**: Adapt communication to audience
2. **Shared goals**: Understand their objectives
3. **Clear interfaces**: Define handoffs and responsibilities
4. **Regular sync**: Proactive communication
5. **Mutual respect**: Value different perspectives

**WHY it matters:**

1. **Better Solutions**: Diverse perspectives improve quality
2. **Faster Execution**: Clear collaboration prevents blockers
3. **User Value**: Cross-functional teams ship complete features
4. **Career Growth**: Visibility beyond engineering
5. **Influence**: Shape product direction

---

## 21.5 Conflict Resolution

**Theory:**

Technical disagreements are natural and healthy—when resolved well.

**Types of conflict:**
- **Technical approach**: Architecture, technology choices
- **Priorities**: What to build first
- **Standards**: Code style, conventions
- **Resources**: Team capacity, budget

**Resolution strategies:**
1. **Data-driven**: Use metrics, benchmarks, prototypes
2. **Time-bound**: Try approach A for 2 weeks, evaluate
3. **Delegate**: Let most-affected person decide
4. **Escalate**: Get manager/architect involved
5. **Document**: Record decision and rationale

**Principles:**
- **Assume good intent**: Everyone wants what's best
- **Focus on problem**: Not people
- **Seek to understand**: Listen before responding
- **Find common ground**: Shared goals
- **Be willing to compromise**: No perfect solutions

**WHY it matters:**

1. **Team Health**: Unresolved conflict damages morale
2. **Decision Quality**: Constructive debate improves outcomes
3. **Velocity**: Blocked decisions slow progress
4. **Learning**: Different viewpoints expand thinking
5. **Culture**: How conflict is handled defines team culture

**Example - Technical Decision Framework:**

```python
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class DecisionStatus(Enum):
    PROPOSED = "proposed"
    DEBATED = "debated"
    DECIDED = "decided"
    IMPLEMENTED = "implemented"

@dataclass
class TechnicalOption:
    """Option being considered"""
    name: str
    pros: List[str]
    cons: List[str]
    estimated_effort: str  # "1 week", "1 month", etc.
    risk_level: str  # "low", "medium", "high"
    
    def score(self, weights: Dict[str, float]) -> float:
        """
        Simple scoring based on pros/cons and weights.
        In reality, use more sophisticated criteria.
        """
        pro_score = len(self.pros) * weights.get('pros', 1.0)
        con_score = len(self.cons) * weights.get('cons', -1.0)
        
        # Penalize effort
        effort_penalty = {
            "1 week": 0,
            "2 weeks": -0.5,
            "1 month": -1.0,
            "3 months": -2.0
        }.get(self.estimated_effort, -1.0)
        
        # Penalize risk
        risk_penalty = {
            "low": 0,
            "medium": -0.5,
            "high": -1.5
        }.get(self.risk_level, -1.0)
        
        return pro_score + con_score + effort_penalty + risk_penalty

@dataclass
class TechnicalDecision:
    """
    Structured framework for technical decisions.
    Based on DACI (Driver, Approver, Contributor, Informed) model.
    """
    title: str
    context: str
    driver: str  # Person driving the decision
    approver: str  # Person who makes final call
    contributors: List[str]  # People providing input
    informed: List[str]  # People who need to know
    
    options: List[TechnicalOption]
    status: DecisionStatus = DecisionStatus.PROPOSED
    chosen_option: str = ""
    rationale: str = ""
    
    def present_options(self):
        """Present options for discussion"""
        print(f"\n{'='*60}")
        print(f"TECHNICAL DECISION: {self.title}")
        print(f"{'='*60}\n")
        
        print(f"CONTEXT:\n{self.context}\n")
        
        print(f"STAKEHOLDERS:")
        print(f"  Driver: {self.driver}")
        print(f"  Approver: {self.approver}")
        print(f"  Contributors: {', '.join(self.contributors)}")
        print(f"  Informed: {', '.join(self.informed)}\n")
        
        print(f"OPTIONS:")
        for i, option in enumerate(self.options, 1):
            print(f"\n{i}. {option.name}")
            print(f"   Effort: {option.estimated_effort}, Risk: {option.risk_level}")
            print(f"   Pros:")
            for pro in option.pros:
                print(f"     + {pro}")
            print(f"   Cons:")
            for con in option.cons:
                print(f"     - {con}")
    
    def make_decision(self, chosen: str, rationale: str):
        """Record decision"""
        self.chosen_option = chosen
        self.rationale = rationale
        self.status = DecisionStatus.DECIDED
        
        print(f"\n{'='*60}")
        print(f"DECISION MADE")
        print(f"{'='*60}\n")
        
        print(f"Chosen: {chosen}")
        print(f"\nRationale:\n{rationale}")
        print(f"\nStatus: {self.status.value}")
        print(f"Approver: {self.approver}")
    
    def document_adr(self):
        """
        Generate Architecture Decision Record (ADR).
        
        ADRs permanently document important decisions.
        """
        adr = f"""
# ADR: {self.title}

## Status
{self.status.value}

## Context
{self.context}

## Decision
We will {self.chosen_option}.

## Rationale
{self.rationale}

## Consequences

### Positive
[List benefits]

### Negative
[List downsides]

### Neutral
[List trade-offs]

## Options Considered

"""
        for option in self.options:
            adr += f"### {option.name}\n"
            adr += f"- Effort: {option.estimated_effort}\n"
            adr += f"- Risk: {option.risk_level}\n"
            adr += "- Pros: " + ", ".join(option.pros) + "\n"
            adr += "- Cons: " + ", ".join(option.cons) + "\n\n"
        
        return adr

# Example: Database choice for new service
decision = TechnicalDecision(
    title="Database Selection for Analytics Service",
    context="""
    We're building a new analytics service that needs to:
    - Store 100M+ events per day
    - Support complex aggregation queries
    - Provide real-time dashboards (< 1s query time)
    - Scale to 5 years of historical data
    
    Current team has PostgreSQL expertise but limited experience with
    other databases.
    """,
    driver="Alice (Tech Lead)",
    approver="Bob (Engineering Manager)",
    contributors=["Carol (Backend)", "Dave (DevOps)", "Eve (Data)"],
    informed=["Product Team", "Executive Team"],
    options=[]
)

# Option 1: PostgreSQL with TimescaleDB
decision.options.append(TechnicalOption(
    name="PostgreSQL + TimescaleDB",
    pros=[
        "Team has deep PostgreSQL expertise",
        "Time-series optimizations built in",
        "SQL familiarity for analysis",
        "Mature ecosystem and tooling"
    ],
    cons=[
        "May struggle with 100M events/day at scale",
        "Complex queries can be slow on large datasets",
        "Requires careful index management"
    ],
    estimated_effort="2 weeks",
    risk_level="low"
))

# Option 2: ClickHouse
decision.options.append(TechnicalOption(
    name="ClickHouse (columnar OLAP)",
    pros=[
        "Designed for exactly this use case",
        "Extremely fast aggregations (10-100x faster)",
        "Compresses data well (less storage)",
        "Scales horizontally easily"
    ],
    cons=[
        "Team has no ClickHouse experience (learning curve)",
        "Different SQL dialect (not 100% compatible)",
        "Fewer third-party integrations",
        "Another database to operate"
    ],
    estimated_effort="1 month",
    risk_level="medium"
))

# Option 3: Apache Druid
decision.options.append(TechnicalOption(
    name="Apache Druid",
    pros=[
        "Real-time ingestion and query",
        "Sub-second query performance",
        "Built-in rollup and aggregation"
    ],
    cons=[
        "Complex architecture (many components)",
        "Steep learning curve",
        "Higher operational overhead",
        "Smaller community than alternatives"
    ],
    estimated_effort="2 months",
    risk_level="high"
))

# Present options
decision.present_options()

# Make decision (after team discussion)
decision.make_decision(
    chosen="PostgreSQL + TimescaleDB initially, with plan to migrate to ClickHouse if needed",
    rationale="""
    After prototyping and load testing, we found TimescaleDB can handle our
    current scale (100M events/day) with P95 query latency of 800ms. While
    not ideal, it's acceptable for v1.
    
    We're choosing this because:
    1. LOWEST RISK: Team expertise means faster delivery and easier debugging
    2. TIME TO MARKET: Can ship in 2 weeks vs 1-2 months for alternatives
    3. MIGRATION PATH: If we hit scaling limits, we can migrate to ClickHouse
       with the data modeling knowledge we've gained
    
    We will:
    - Monitor query performance and data volume closely
    - Set a threshold (P95 > 2s OR data > 1TB) to trigger ClickHouse migration
    - Document data schema for easier future migration
    
    This is a pragmatic choice that balances risk, timeline, and future flexibility.
    """
)

# Generate ADR
adr_document = decision.document_adr()
print(f"\n{'='*60}")
print("ARCHITECTURE DECISION RECORD")
print(f"{'='*60}")
print(adr_document)

print("\n→ Structured decision-making resolves conflicts objectively")
```

**Connections to Other Topics:**

- **Part 15 (Judgment)**: Making good decisions
- **Part 19 (Research)**: Evidence-based decisions
- **Part 10 (Testing)**: Validating decisions through experimentation
- **Part 13 (Architecture)**: System-level decisions

---

# PART 22: SPECIALIZED DOMAINS

These specialized domains represent deep technical areas where scientist-level expertise separates generalists from domain experts.

## 22.1 Computer Graphics

**Theory:**

Computer graphics: rendering visual content using computation.

**Core concepts:**
- **Rasterization**: Convert 3D geometry to 2D pixels
- **Ray tracing**: Simulate light paths for realistic rendering
- **Shaders**: GPU programs for rendering effects
- **Transform pipeline**: Model → World → View → Projection
- **Lighting models**: Phong, PBR (Physically Based Rendering)

**Applications:**
- Game engines (Unity, Unreal)
- 3D modeling software (Blender, Maya)
- Data visualization
- UI rendering
- Virtual/Augmented Reality

**WHY it matters:**

1. **Visual Interfaces**: Every UI uses graphics primitives
2. **Data Visualization**: Communicate complex data visually
3. **Performance**: GPU optimization critical for responsiveness
4. **Emerging Tech**: VR/AR rely on graphics fundamentals
5. **Cross-Domain**: Graphics concepts apply to many fields

**Key Topics:**
- Rendering pipeline (vertex → fragment shaders)
- Linear algebra for transformations
- Texture mapping and filtering
- Anti-aliasing techniques
- GPU architecture and optimization

---

## 22.2 Compilers & Language Design

**Theory:**

Compilers: translate source code to executable form.

**Phases:**
1. **Lexical Analysis**: Source → Tokens
2. **Syntax Analysis**: Tokens → AST (Abstract Syntax Tree)
3. **Semantic Analysis**: Type checking, scope resolution
4. **Optimization**: Improve performance/size
5. **Code Generation**: AST → Machine code/bytecode

**Key concepts:**
- **Parsing**: Context-free grammars, LL/LR parsers
- **Type systems**: Static vs dynamic, strong vs weak
- **Intermediate representations**: SSA (Static Single Assignment)
- **Optimization passes**: Dead code elimination, constant folding
- **Runtime**: Garbage collection, JIT compilation

**Applications:**
- Programming language implementation
- Domain-specific languages (DSLs)
- Query optimization (databases)
- Code analysis tools (linters, formatters)
- Transpilers (TypeScript → JavaScript)

**WHY it matters:**

1. **Language Design**: Create better abstractions
2. **Performance**: Understand optimization strategies
3. **Tooling**: Build analyzers, formatters, linters
4. **DSLs**: Domain-specific languages for productivity
5. **Debugging**: Understand how code executes

**Example - Simple Expression Compiler:**

```python
# Tokenizer → Parser → Code Generator

from dataclasses import dataclass
from typing import List, Union
from enum import Enum

class TokenType(Enum):
    NUMBER = "number"
    PLUS = "plus"
    MINUS = "minus"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    LPAREN = "lparen"
    RPAREN = "rparen"

@dataclass
class Token:
    type: TokenType
    value: Union[int, str]

# Lexer: Source → Tokens
class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            if char.isspace():
                self.pos += 1
            elif char.isdigit():
                tokens.append(self.read_number())
            elif char == '+':
                tokens.append(Token(TokenType.PLUS, '+'))
                self.pos += 1
            elif char == '-':
                tokens.append(Token(TokenType.MINUS, '-'))
                self.pos += 1
            elif char == '*':
                tokens.append(Token(TokenType.MULTIPLY, '*'))
                self.pos += 1
            elif char == '/':
                tokens.append(Token(TokenType.DIVIDE, '/'))
                self.pos += 1
            elif char == '(':
                tokens.append(Token(TokenType.LPAREN, '('))
                self.pos += 1
            elif char == ')':
                tokens.append(Token(TokenType.RPAREN, ')'))
                self.pos += 1
            else:
                raise ValueError(f"Unknown character: {char}")
        
        return tokens
    
    def read_number(self) -> Token:
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
        return Token(TokenType.NUMBER, int(self.source[start:self.pos]))

# AST Nodes
@dataclass
class BinOp:
    """Binary operation: left op right"""
    op: str
    left: Union['BinOp', 'Number']
    right: Union['BinOp', 'Number']

@dataclass
class Number:
    """Number literal"""
    value: int

# Parser: Tokens → AST
class Parser:
    """
    Recursive descent parser for expressions.
    
    Grammar:
      expr   → term (('+' | '-') term)*
      term   → factor (('*' | '/') factor)*
      factor → NUMBER | '(' expr ')'
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self):
        return self.expr()
    
    def expr(self):
        """expr → term (('+' | '-') term)*"""
        left = self.term()
        
        while self.pos < len(self.tokens) and \
              self.tokens[self.pos].type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.tokens[self.pos].value
            self.pos += 1
            right = self.term()
            left = BinOp(op, left, right)
        
        return left
    
    def term(self):
        """term → factor (('*' | '/') factor)*"""
        left = self.factor()
        
        while self.pos < len(self.tokens) and \
              self.tokens[self.pos].type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op = self.tokens[self.pos].value
            self.pos += 1
            right = self.factor()
            left = BinOp(op, left, right)
        
        return left
    
    def factor(self):
        """factor → NUMBER | '(' expr ')'"""
        token = self.tokens[self.pos]
        
        if token.type == TokenType.NUMBER:
            self.pos += 1
            return Number(token.value)
        elif token.type == TokenType.LPAREN:
            self.pos += 1
            node = self.expr()
            self.pos += 1  # Consume ')'
            return node
        else:
            raise ValueError(f"Unexpected token: {token}")

# Code Generator: AST → Python bytecode (simplified)
class CodeGenerator:
    """Generate executable code from AST"""
    
    def generate(self, node):
        """Generate Python code"""
        if isinstance(node, Number):
            return str(node.value)
        elif isinstance(node, BinOp):
            left = self.generate(node.left)
            right = self.generate(node.right)
            return f"({left} {node.op} {right})"
        else:
            raise ValueError(f"Unknown node type: {type(node)}")

# Example: Compile and execute
source = "3 + 4 * (2 - 1)"

print(f"Source: {source}")

# Lexical analysis
lexer = Lexer(source)
tokens = lexer.tokenize()
print(f"\nTokens: {[f'{t.type.value}:{t.value}' for t in tokens]}")

# Syntax analysis
parser = Parser(tokens)
ast = parser.parse()
print(f"\nAST: {ast}")

# Code generation
codegen = CodeGenerator()
code = codegen.generate(ast)
print(f"\nGenerated code: {code}")

# Execute
result = eval(code)
print(f"Result: {result}")

print("\n→ Compilers transform human-readable code into executable form")
```

---

## 22.3 Operating Systems Concepts

**Theory:**

Operating systems: manage hardware resources and provide abstractions.

**Core responsibilities:**
- **Process management**: Scheduling, isolation
- **Memory management**: Virtual memory, paging
- **File systems**: Storage abstraction
- **I/O management**: Devices, drivers
- **Security**: Access control, isolation

**Key concepts:**
- **System calls**: User space → Kernel space
- **Context switching**: Save/restore process state
- **Virtual memory**: Paging, page tables
- **Scheduling algorithms**: Round-robin, CFS
- **Synchronization**: Mutexes, semaphores

**WHY it matters:**

1. **Performance**: Understanding OS → better optimization
2. **Debugging**: System-level issues require OS knowledge
3. **Resource Management**: Prevent leaks, optimize usage
4. **Containerization**: Docker/K8s use OS primitives
5. **Systems Programming**: Build infrastructure tools

**Key Topics:**
- Process vs thread model
- Memory hierarchy (cache, RAM, disk)
- File system implementations (ext4, NTFS, APFS)
- Networking stack (TCP/IP, sockets)
- Security models (users, permissions, capabilities)

---

## 22.4 Networking Fundamentals

**Theory:**

Computer networking: communication between systems.

**OSI Model (7 layers):**
1. Physical: Bits on wire
2. Data Link: MAC addresses, Ethernet
3. Network: IP routing
4. Transport: TCP/UDP
5. Session: Connections
6. Presentation: Encryption, encoding
7. Application: HTTP, DNS, etc.

**Key protocols:**
- **IP**: Packet routing between networks
- **TCP**: Reliable, ordered, byte stream
- **UDP**: Unreliable, fast datagrams
- **HTTP**: Web protocol
- **DNS**: Domain name resolution
- **TLS**: Encryption

**WHY it matters:**

1. **Distributed Systems**: Network is foundation
2. **Performance**: Latency, bandwidth optimization
3. **Security**: Understand attack vectors
4. **Debugging**: Troubleshoot connectivity issues
5. **Architecture**: Design network topology

**Key Topics:**
- TCP congestion control
- HTTP/2 multiplexing
- CDN architecture
- Load balancing strategies
- Network security (firewalls, VPNs)

---

# SYNTHESIS: THE SCIENTIST-LEVEL ENGINEER

You've now traversed the full landscape of software engineering knowledge. But knowledge alone doesn't make a scientist-level engineer—it's the integration and application.

## What Separates Scientist-Level Engineers

**1. Systems Thinking**
- See connections between domains
- Understand second-order effects
- Design for long-term evolution

**2. First Principles Reasoning**
- Question assumptions
- Derive solutions from fundamentals
- Don't cargo-cult patterns

**3. Quantitative Analysis**
- Measure, don't guess
- Statistical rigor
- Data-driven decisions

**4. Research Mindset**
- Systematic experimentation
- Literature review before building
- Document and share learnings

**5. Communication & Leadership**
- Explain complex topics clearly
- Mentor and grow others
- Influence through reasoning

**6. Breadth & Depth**
- Deep expertise in 1-2 areas
- Working knowledge across all domains
- Know when to dive deep

## Continuous Growth Path

**Years 0-2: Learn Fundamentals**
- Master one language deeply
- Understand data structures, algorithms
- Build complete applications
- Read lots of code

**Years 2-5: Develop Specialization**
- Choose 1-2 domains to go deep
- Contribute to open source
- Write technical blog posts
- Mentor junior engineers

**Years 5-10: Broaden & Lead**
- Expand to adjacent domains
- Design systems, not just code
- Lead projects and teams
- Speak at conferences

**Years 10+: Innovate & Shape**
- Research novel solutions
- Publish papers
- Create new tools/frameworks
- Influence industry direction

## Your Action Plan

**Today:**
- Identify your weakest area from this document
- Read one paper or book chapter on that topic
- Build one small prototype

**This Month:**
- Complete one non-trivial project applying new knowledge
- Write one technical blog post explaining what you learned
- Do one code review focused on teaching

**This Year:**
- Contribute to one open source project
- Give one technical presentation
- Mentor one engineer
- Ship one significant feature

**Remember:**
- **Depth > Breadth initially**: Master one area before expanding
- **Build things**: Reading is learning, building is understanding
- **Teach others**: Best way to solidify knowledge
- **Stay curious**: Technology changes, fundamentals endure
- **Be patient**: Mastery takes years, not months

## Final Wisdom

The journey from code monkey to scientist-level engineer is not linear. You'll have breakthroughs and plateaus. You'll master one concept only to discover ten more you don't understand. **This is normal and healthy.**

What matters is:
- **Continuous learning**: Dedicate time weekly
- **Deliberate practice**: Work on edge of your ability
- **Reflection**: Understand not just what, but why
- **Resilience**: Learn from failures
- **Community**: Engage with other engineers

**The best time to start was yesterday. The second best time is now.**

Now go build something amazing. The field of software engineering needs scientist-level engineers who can not only implement solutions, but discover new ones, advance the state of the art, and mentor the next generation.

**You have the map. Now walk the path.**

---

## Final References & Resources

### Books (Advanced Topics)
- **"The Art of Computer Programming"** by Donald Knuth (algorithms)
- **"Introduction to Algorithms"** by CLRS (comprehensive algorithms)
- **"Computer Systems: A Programmer's Perspective"** by Bryant & O'Hallaron
- **"Database Internals"** by Alex Petrov
- **"Distributed Systems"** by Maarten van Steen & Andrew Tanenbaum
- **"The Pragmatic Programmer"** by Hunt & Thomas
- **"A Philosophy of Software Design"** by John Ousterhout

### Papers (Foundational)
- "Time, Clocks, and the Ordering of Events" (Lamport, 1978)
- "The Byzantine Generals Problem" (Lamport, Shostak, Pease, 1982)
- "MapReduce: Simplified Data Processing" (Dean & Ghemawat, 2004)
- "Dynamo: Amazon's Highly Available Key-value Store" (2007)
- "The Chubby Lock Service" (Burrows, 2006)
- "Attention Is All You Need" (Vaswani et al., 2017)

### Online Courses
- MIT OpenCourseWare: 6.824 Distributed Systems
- Stanford CS229: Machine Learning
- Coursera: Andrew Ng's Deep Learning Specialization
- Fast.ai: Practical Deep Learning

### Communities
- Papers We Love (meetup group)
- Hacker News (news.ycombinator.com)
- r/programming, r/compsci
- Engineering blogs (Google, Meta, Netflix, Uber)

### Tools for Learning
- Jupyter notebooks (experimentation)
- Obsidian/Notion (knowledge management)
- Anki (spaced repetition)
- Git (version your learning projects)

---

**VERSION**: 2.0 (Expanded with Parts 16-22)
**LAST UPDATED**: 2024-01-15
**CONTRIBUTORS**: Engineering community wisdom distilled
**LICENSE**: Share freely, attribute appropriately, use wisely

---

*This document is never "complete"—software engineering evolves continuously. Contribute your insights, challenge assumptions, and help future engineers climb higher.*

**EOF - End of Engineering Mastery Complete Guide**
