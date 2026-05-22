import os
import json

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.metadata = None

class TagTrieEngine:
    def __init__(self):
        self.root = TrieNode()
        self.hs_codes_index = {} # O(1) lookup for exact HS codes
        # Pre-seed the trie index with valid logistics domain search tags
        default_tags = [
            "hardware", "fasteners", "steel", "fluids", 
            "maintenance", "hydraulic", "hoses", "pneumatic", 
            "rubber", "washers", "precision", "logistics",
            "electronics", "automotive", "safety", "packaging"
        ]
        for tag in default_tags:
            self.insert(tag)

        # Attempt to load HS code data from the seeded tariff file
        self._load_tariffs()

    def _load_tariffs(self):
        tariff_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_tariffs.json")
        if os.path.exists(tariff_path):
            try:
                with open(tariff_path, "r", encoding="utf-8") as f:
                    tariffs = json.load(f)
                    for code, data in tariffs.items():
                        desc = data.get("description", "")
                        # Store in exact lookup index
                        self.hs_codes_index[str(code).strip()] = desc
                        
                        # Also index description words in the Trie for semantic search
                        words = desc.lower().split()[:3]
                        for word in words:
                            clean_word = "".join(filter(str.isalnum, word))
                            if clean_word:
                                self.insert(clean_word, metadata={"code": code, "desc": desc})
            except Exception:
                pass

    def validate_hs_code(self, code: str) -> dict:
        """Checks if an HS code exists in the database and returns its validation status and duty rates."""
        code_clean = str(code).strip().replace('.', '')
        if code_clean in self.hs_codes_index:
            tariff_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_tariffs.json")
            try:
                with open(tariff_path, "r", encoding="utf-8") as f:
                    tariffs = json.load(f)
                    data = tariffs.get(code_clean, {})
                    return {
                        "valid": True, 
                        "description": data.get("description", "Validated"),
                        "rates": data.get("rates", {"CA": 0.0, "US": 0.0, "EU": 0.0})
                    }
            except:
                pass
            return {"valid": True, "description": self.hs_codes_index[code_clean], "rates": {"CA": 0.0, "US": 0.0, "EU": 0.0}}
        return {"valid": False, "description": "Unknown or Invalid HS Code", "rates": {"CA": 0.0, "US": 0.0, "EU": 0.0}}

    def insert(self, word: str, metadata=None):
        """Inserts a normalized word into the prefix trie structure."""
        node = self.root
        for char in word.lower().strip():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        if metadata:
            node.metadata = metadata

    def search_prefix(self, prefix: str) -> list:
        """Finds all words in the trie that match the given incoming prefix string."""
        node = self.root
        prefix_clean = prefix.lower().strip()
        for char in prefix_clean:
            if char not in node.children:
                return []
            node = node.children[char]
        results = []
        self._dfs(node, prefix_clean, results)
        return results

    def _dfs(self, node: TrieNode, current_word: str, results: list):
        if node.is_end_of_word:
            results.append(current_word)
        for char, child_node in node.children.items():
            self._dfs(child_node, current_word + char, results)


# Instantiate a singleton system instance for the execution pipeline
_trie_subsystem = TagTrieEngine()

def validate_hs_code(code: str) -> dict:
    """
    Interface function required by app.py.
    Validates a raw HS code against the pre-loaded 1.2MB tariff index.
    """
    return _trie_subsystem.validate_hs_code(code)

def autocomplete_search_tags(incoming_tags: list) -> list:
    """
    Interface function required by app.py.
    """
    if not incoming_tags or not isinstance(incoming_tags, list):
        return []
    resolved_tags = []
    for tag in incoming_tags:
        tag_str = str(tag).strip()
        matches = _trie_subsystem.search_prefix(tag_str)
        if matches:
            resolved_tags.append(matches[0])
        else:
            resolved_tags.append(tag_str.lower())
    return list(set(resolved_tags))
