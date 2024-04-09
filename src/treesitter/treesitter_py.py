import tree_sitter

from src.constants import Language
from src.treesitter.treesitter import Treesitter, TreesitterMethodNode
from src.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterPython(Treesitter):
    def __init__(self):
        """
        A function definition consists of an identifier followed by an expression
        statement.
        """
        super().__init__(
            Language.PYTHON, "function_definition", "identifier", "expression_statement"
        )

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        """
        Parse the given file bytes.

        Parameters
        ----------
        file_bytes : bytes
            The file bytes to parse.

        Returns
        -------
        list of TreesitterMethodNode
            The parsed methods.
        """
        self.tree = self.parser.parse(file_bytes)
        result = []
        methods = self._query_all_methods(self.tree.root_node)
        for method in methods:
            method_name = self._query_method_name(method)
            doc_comment = self._query_doc_comment(method)
            result.append(TreesitterMethodNode(method_name, doc_comment, None, method))
        return result

    def _query_method_name(self, node: tree_sitter.Node):
        """
        Get the name of the method being called.

        Parameters
        ----------
        node : tree_sitter.Node
            The node containing the method declaration.

        Returns
        -------
        str
            The name of the method being called.
        """
        if node.type == self.method_declaration_identifier:
            for child in node.children:
                if child.type == self.method_name_identifier:
                    return child.text.decode()
        return None

    def _query_all_methods(self, node: tree_sitter.Node):
        """
        Query all methods in the given node.

        Parameters
        ----------
        node : tree_sitter.Node
            The node to query.

        Returns
        -------
        methods : list of tree_sitter.Node
            The list of methods.
        """
        methods = []
        for child in node.children:
            if child.type == self.method_declaration_identifier:
                methods.append(child)
            if child.type == "class_definition":
                class_body = child.children[-1]
                for child_node in class_body.children:
                    if child_node.type == self.method_declaration_identifier:
                        methods.append(child_node)
        return methods

    def _query_doc_comment(self, node: tree_sitter.Node):
        """
        Query for doc string of a function definition.

        Parameters
        ----------
        node : tree_sitter.Node
            The node to query.

        Returns
        -------
        doc_str : str
            The doc string of the function definition.
        """
        query_code = """
            (function_definition
                body: (block . (expression_statement (string)) @function_doc_str))
        """
        doc_str_query = self.language.query(query_code)
        doc_strs = doc_str_query.captures(node)

        if doc_strs:
            return doc_strs[0][0].text.decode()
        else:
            return None


# Register the TreesitterPython class in the registry
TreesitterRegistry.register_treesitter(Language.PYTHON, TreesitterPython)
