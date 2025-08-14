from typing import List, Dict, Set

# Simple competency graph and objectives repository
COMPETENCY_PREREQS: Dict[str, List[str]] = {
	"arrays": [],
	"linked-lists": ["arrays"],
	"stacks": ["arrays"],
	"queues": ["arrays"],
	"trees": ["arrays", "linked-lists"],
	"graphs": ["arrays", "trees"],
	"dp": ["arrays", "graphs"]
}

COMPETENCY_OBJECTIVES: Dict[str, List[str]] = {
	"arrays": [
		"Define arrays and their memory layout",
		"Perform traversal and element access",
		"Analyze time/space complexity for core operations"
	],
	"linked-lists": [
		"Explain node structure and pointers",
		"Implement insertion/deletion at head/tail",
		"Compare linked lists vs arrays"
	],
	"stacks": [
		"Explain LIFO behavior",
		"Use stacks for expression evaluation",
		"Implement stack using arrays or linked lists"
	],
	"queues": [
		"Explain FIFO behavior",
		"Implement queue and circular queue",
		"Apply queues in BFS"
	],
	"trees": [
		"Define tree terminology (root, leaf, depth)",
		"Traverse trees (pre/in/post/level)",
		"Explain BST properties"
	],
	"graphs": [
		"Define graphs (directed/undirected, weighted)",
		"Traverse with DFS/BFS",
		"Compute shortest paths (Dijkstra/Bellman-Ford)"
	],
	"dp": [
		"Explain overlapping subproblems and optimal substructure",
		"Formulate state and transitions",
		"Implement memoization and tabulation"
	]
}


def get_prerequisites(competency: str) -> List[str]:
	return COMPETENCY_PREREQS.get(competency, [])


def get_objectives(competency: str) -> List[str]:
	return COMPETENCY_OBJECTIVES.get(competency, [])


def topological_sequence(goals: List[str]) -> List[str]:
	# Simple DFS-based topo sort restricted to the goal-induced subgraph
	visited: Set[str] = set()
	order: List[str] = []

	def dfs(node: str):
		if node in visited:
			return
		for pre in COMPETENCY_PREREQS.get(node, []):
			dfs(pre)
		visited.add(node)
		order.append(node)

	for g in goals:
		dfs(g)
	# Deduplicate while preserving order and include only requested + prereqs
	seen: Set[str] = set()
	seq: List[str] = []
	for c in order:
		if c not in seen:
			seq.append(c)
			seen.add(c)
	return seq


def objectives_for_goals(goals: List[str]) -> Dict[str, List[str]]:
	return {c: get_objectives(c) for c in topological_sequence(goals)}
