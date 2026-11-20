from dataclasses import dataclass


@dataclass(frozen=True)
class Tarefa:
    id: str
    nome: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("O identificador da tarefa deve ser um texto não vazio.")
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("O nome da tarefa deve ser um texto não vazio.")

        # Normaliza os valores durante a inicialização da dataclass imutável.
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "nome", self.nome.strip())
