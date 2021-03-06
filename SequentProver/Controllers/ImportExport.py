import json
import os
from typing import Iterator

from Propositions.Converters import String
from Controllers.Settings import Settings
from Propositions.BaseClasses import Proposition
from Objects.Sequents import Sequent
from Objects.Trees import Tree

_current_path = os.path.dirname(__file__)


class Import:
    def __init__(self, file_path):
        with open(file_path, "r") as file:
            if file_path.endswith(".txt"):
                self.data = file.readlines()
            elif file_path.endswith(".json"):
                self.data = json.load(file)

    def sequents(self) -> Iterator[Sequent]:
        for line in self.data:
            if " |~ " in line:
                yield String(line.strip("\n")).to_sequent()

    def propositions(self) -> Iterator[Proposition]:
        for line in self.data:
            if _contains_connective(line) and " |~ " not in line:
                yield String(line).to_proposition()

    def trees(self) -> Iterator[Tree]:
        for dictionary in self.data.values():
            tree = Tree(dictionary['0000'])
            tree.fill_with(dictionary)
            yield tree


def _contains_connective(string) -> bool:
    """Checks whether the input string contains a connective."""
    test = [connective for connective in connectives if connective in string]
    if test:
        return True
    return False


connectives = ["if", "and", "or", "not"]


class Export:
    runs_file = os.path.join(_current_path, "..", "data",
                             "Runs", Settings()["Output File"])
    atoms_file = os.path.join(_current_path, "..", "data", "Atoms.json")

    def __init__(self, data):
        self.data = data

    def to_runs(self):
        str_forest = {}
        for tree in self.data:
            tree_dict = {str(key): str(sequent)
                         for key, sequent in tree.items()}
            str_forest.update({str(tree.root): tree_dict})
        with open(self.runs_file, "w") as file:
            file.write(json.dumps(str_forest, indent=4))

    def to_atoms(self):
        with open(self.atoms_file, "r") as file:
            atoms = set(json.load(file))
        for tree in self.data:
            atomic_sequents = [str(sequent) for sequent in tree.values()
                               if sequent.complexity == 0]
            atoms.update(atomic_sequents)
        with open(self.atoms_file, "w") as file:
            file.write(json.dumps(list(atoms), indent=4))


class Decompose:

    def __init__(self, file_path):
        self.file_path: str = file_path
        self.data: list = [sequent for sequent in Import(file_path).sequents()]

    def sequents(self):
        forest = []
        for line in self.data:
            tree = Tree(line)
            tree.populate()
            forest.append(tree)
        Export(forest).to_runs()
        Export(forest).to_atoms()


def _names_file_is_empty():
    names_file = os.path.join(_current_path, "..", "data", "Names.json")
    with open(names_file) as file:
        names = json.load(file)
    if names:
        return False
    return True


def decompose_sequents():
    input_file = Settings()["Input File"]
    if _names_file_is_empty():
        raise ValueError("Names.json contains no names.")
    try:
        Decompose(input_file).sequents()
    except FileNotFoundError:
        print("Input file could not be found at: \n"
              f"{input_file} \n"
              f"Please verify file name and location.")
    except ValueError as e:
        print(e)
