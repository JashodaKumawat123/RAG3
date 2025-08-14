# Linked Lists in Data Structures

## Introduction
A linked list is a linear data structure where elements are stored in nodes, and each node contains a data field and a reference (link) to the next node in the sequence. Unlike arrays, linked lists are dynamic in size and do not require contiguous memory allocation.

## Node Structure
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
```

## Types of Linked Lists

### 1. Singly Linked List
Each node has data and a reference to the next node.
```
Node1 -> Node2 -> Node3 -> None
```

### 2. Doubly Linked List
Each node has data and references to both next and previous nodes.
```
None <- Node1 <-> Node2 <-> Node3 -> None
```

### 3. Circular Linked List
The last node points back to the first node.
```
Node1 -> Node2 -> Node3 -> Node1
```

## Basic Operations

### 1. Insertion
```python
class LinkedList:
    def __init__(self):
        self.head = None
    
    def insert_at_beginning(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def insert_at_end(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def insert_after(self, prev_node, data):
        if not prev_node:
            return
        
        new_node = Node(data)
        new_node.next = prev_node.next
        prev_node.next = new_node
```

### 2. Deletion
```python
def delete_node(self, key):
    current = self.head
    
    # If head node itself holds the key
    if current and current.data == key:
        self.head = current.next
        current = None
        return
    
    # Search for the key to delete
    while current and current.data != key:
        prev = current
        current = current.next
    
    # If key was not present
    if not current:
        return
    
    # Unlink the node
    prev.next = current.next
    current = None
```

### 3. Traversal
```python
def print_list(self):
    current = self.head
    while current:
        print(current.data, end=" -> ")
        current = current.next
    print("None")
```

## Two Pointer Technique
A powerful technique for solving linked list problems:

```python
def find_middle(self):
    slow = fast = self.head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    
    return slow

def detect_cycle(self):
    slow = fast = self.head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:
            return True
    
    return False
```

## Advantages
1. **Dynamic Size**: Can grow and shrink at runtime
2. **Efficient Insertion/Deletion**: O(1) at beginning, O(n) at end
3. **No Memory Wastage**: Allocates memory as needed
4. **Easy Implementation**: Simple to understand and implement

## Disadvantages
1. **No Direct Access**: Cannot access elements by index
2. **Extra Memory**: Requires extra space for pointers
3. **Cache Performance**: Poor cache locality due to scattered memory
4. **Reverse Traversal**: Difficult in singly linked lists

## Common Applications
- **Memory Management**: Operating system memory allocation
- **Undo Functionality**: Browser back/forward buttons
- **Music Player**: Playlist management
- **Hash Tables**: Chaining for collision resolution
- **Polynomial Arithmetic**: Sparse polynomial representation

## Time Complexity Summary
| Operation | Time Complexity |
|-----------|-----------------|
| Access    | O(n)           |
| Search    | O(n)           |
| Insertion | O(1) at head, O(n) at end |
| Deletion  | O(1) at head, O(n) at end |

## Space Complexity
- **Space**: O(n) where n is the number of nodes
- **Auxiliary Space**: O(1) for most operations

## Practice Problems
1. Reverse a linked list
2. Find the middle element
3. Detect cycle in linked list
4. Remove nth node from end
5. Merge two sorted linked lists
6. Add two numbers represented by linked lists