import abc

class KB(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def size(self):
        return NotImplemented

    @abc.abstractmethod
    def copy(self):
        return NotImplemented

    # Add a single rml to the KB
    def add_rml(self, rml):
        assert isinstance(rml, RML)

    # Remove a single rml from the KB
    def remove_rml(self, rml):
        assert isinstance(rml, RML)

    # Expand a KB by adding the self of rmls
    @abc.abstractmethod
    def expand(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)

    # Remove the set of rmls from the KB
    @abc.abstractmethod
    def contract(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)

    # Remove a set of RMLs and anything that implies them from the KB
    @abc.abstractmethod
    def remove(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)

    # Update a compiled KB with a set of rmls, removing anything that
    # is inconsistent with the new information
    @abc.abstractmethod
    def update(self, rmls):
        assert all(isinstance(rml, RML) for rml in rmls)

