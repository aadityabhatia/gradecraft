# parse the submitted python file and get a specific function

import signal
import ast
import parso


def checkSyntax(source, feedback):
    grammar = parso.load_grammar()
    module = grammar.parse(source)
    errors = grammar.iter_errors(module)

    if len(list(errors)) == 0:
        return True

    feedback.write("Syntax Errors:\n\n")

    for error in errors:
        lineNum = error.start_pos[0]
        line = source.split("\n")[lineNum - 1]
        column = error.start_pos[1]
        feedback.write(f"{lineNum:>3} {line} ## {error.message}\n")
        feedback.write(" " * (column + 4) + "^\n")

    return len(list(errors)) == 0


def parseCode(source, allowedImports=[]):
    # Parse the code into an AST
    parsed_ast = ast.parse(source)

    # Filter out top-level executable code
    allowed_node_types = (ast.FunctionDef, ast.ClassDef,
                          ast.Import, ast.ImportFrom, ast.Assign)
    new_body = [node for node in parsed_ast.body if isinstance(
        node, allowed_node_types)]
    # filter imports
    for node in parsed_ast.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in allowedImports:
                    raise ImportError(
                        f"Attempted to import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module not in allowedImports:
                raise ImportError(f"Attempted to import {node.module}")
    parsed_ast.body = new_body

    return parsed_ast


def checkFunctionDefinition(parsed_ast, fnName, argCount):
    # Check if the function is defined in the AST
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == fnName:
            return len(node.args.args) == argCount
    return False


def checkFunctionCall(parsed_ast, caller, callee):
    # Check if the caller function calls the callee function
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == caller:
            for innerNode in ast.walk(node):
                if isinstance(innerNode, ast.Call) and isinstance(innerNode.func, ast.Name) and innerNode.func.id == callee:
                    return True
    return False

def checkFunctionReturn(parsed_ast, fnName):
    # Check if the function has a return statement
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == fnName:
            for innerNode in ast.walk(node):
                if isinstance(innerNode, ast.Return):
                    return True
    return False


def compileCode(parsed_ast, filename='main.py'):
    # Compile the modified AST
    code_object = compile(parsed_ast, filename=filename, mode='exec')

    # Execute the code in a controlled namespace
    namespace = {}
    # Prevents code under if __name__ == '__main__':
    namespace['__name__'] = '__not_main__'
    exec(code_object, namespace)

    return namespace


def getFunction(namespace, fnName):

    # Access the desired function
    func = namespace.get(fnName)
    if func is None:
        raise AttributeError(f"Function '{fnName}' not found.")
    elif not callable(func):
        raise TypeError(f"Function '{fnName}' is not callable.")
    return func


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)
