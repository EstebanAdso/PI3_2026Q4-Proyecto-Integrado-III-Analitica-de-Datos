"""Resumen descriptivo de un DataFrame exportable a un archivo .txt."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


class DatasetSummarizer:
    """Recibe un DataFrame y genera un resumen legible de su contenido.

    El resumen incluye dimensiones, nombres y tipos de columnas, valores
    nulos, duplicados, estadísticas numéricas, valores más frecuentes de las
    columnas categóricas y rango de las columnas de fecha.

    Args:
        df: DataFrame que se va a resumir.
        titulo: Título que encabeza el resumen.
        top_n: Cantidad de valores frecuentes a mostrar por columna categórica.
        metadatos: Datos de origen que encabezan el resumen, por ejemplo
            ``{"Dataset": "usuario/dataset", "Split": "train"}``.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        titulo: str = "Resumen del DataFrame",
        top_n: int = 5,
        metadatos: dict[str, str] | None = None,
    ) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df debe ser un pandas.DataFrame.")
        if top_n < 1:
            raise ValueError("top_n debe ser mayor que cero.")
        self.df = df
        self.titulo = titulo
        self.top_n = top_n
        self.metadatos = metadatos or {}

    def origen(self) -> list[str]:
        """Metadatos del origen de los datos (dataset, split, archivos, etc.)."""
        if not self.metadatos:
            return ["(sin metadatos de origen)"]
        return [f"- {clave}: {valor}" for clave, valor in self.metadatos.items()]

    def dimensiones(self) -> list[str]:
        """Cantidad de filas, columnas, duplicados y memoria usada."""
        memoria_kb = self.df.memory_usage(deep=True).sum() / 1024
        return [
            f"Filas: {len(self.df)}",
            f"Columnas: {len(self.df.columns)}",
            f"Filas duplicadas: {int(self.df.duplicated().sum())}",
            f"Memoria aproximada: {memoria_kb:,.1f} KB",
        ]

    def columnas(self) -> list[str]:
        """Nombre, tipo y cantidad de valores únicos de cada columna."""
        return [
            f"- {columna}: {tipo} ({self.df[columna].nunique()} valores únicos)"
            for columna, tipo in self.df.dtypes.items()
        ]

    def nulos(self) -> list[str]:
        """Cantidad y porcentaje de valores nulos por columna."""
        total = len(self.df) or 1
        conteo = self.df.isna().sum()
        lineas = [
            f"- {columna}: {cantidad} ({cantidad / total:.2%})"
            for columna, cantidad in conteo.items()
        ]
        lineas.append(f"Total de valores nulos: {int(conteo.sum())}")
        return lineas

    def estadisticas_numericas(self) -> list[str]:
        """Estadísticas descriptivas de las columnas numéricas."""
        numericas = self.df.select_dtypes(include="number")
        if numericas.empty:
            return ["(sin columnas numéricas)"]
        return [numericas.describe().round(3).to_string()]

    def frecuencias_categoricas(self) -> list[str]:
        """Valores más frecuentes de las columnas de texto o categóricas."""
        categoricas = self.df.select_dtypes(include=["object", "category", "string"])
        if categoricas.empty:
            return ["(sin columnas categóricas)"]
        lineas: list[str] = []
        for columna in categoricas.columns:
            top = categoricas[columna].value_counts(dropna=False).head(self.top_n)
            valores = ", ".join(f"{valor} ({cantidad})" for valor, cantidad in top.items())
            lineas.append(f"- {columna}: {valores}")
        return lineas

    def rangos_fechas(self) -> list[str]:
        """Fecha mínima y máxima de las columnas de tipo fecha."""
        fechas = self.df.select_dtypes(include=["datetime", "datetimetz"])
        if fechas.empty:
            return ["(sin columnas de fecha)"]
        return [
            f"- {columna}: {fechas[columna].min()} -> {fechas[columna].max()}"
            for columna in fechas.columns
        ]

    def generar(self) -> str:
        """Construye el texto completo del resumen."""
        secciones = [
            ("Origen de los datos", self.origen()),
            ("Dimensiones", self.dimensiones()),
            ("Columnas y tipos", self.columnas()),
            ("Valores nulos por columna", self.nulos()),
            ("Estadísticas numéricas", self.estadisticas_numericas()),
            (f"Top {self.top_n} valores de columnas categóricas", self.frecuencias_categoricas()),
            ("Rango de columnas de fecha", self.rangos_fechas()),
        ]
        lineas = [
            self.titulo.upper(),
            "=" * 70,
            f"Generado: {datetime.now():%Y-%m-%d %H:%M:%S}",
        ]
        for nombre, contenido in secciones:
            lineas += ["", nombre, "-" * len(nombre), *contenido]
        return "\n".join(lineas) + "\n"

    def imprimir(self) -> None:
        """Muestra el resumen en la consola."""
        print(self.generar(), end="")

    def guardar(self, ruta: str | Path) -> Path:
        """Guarda el resumen en un archivo .txt (UTF-8) y retorna su ruta."""
        path = Path(ruta)
        if path.suffix.lower() != ".txt":
            path = path.with_suffix(".txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar(), encoding="utf-8")
        return path
