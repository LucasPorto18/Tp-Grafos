from dataclasses import dataclass


@dataclass
class ResultadoAnalise:
    graus_entrada: dict[str, int]
    ciclo: list[str] | None
    ordem_execucao: list[str] | None
    rodadas: list[list[str]] | None