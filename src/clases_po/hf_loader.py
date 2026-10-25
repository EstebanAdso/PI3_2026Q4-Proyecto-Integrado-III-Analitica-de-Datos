"""Carga datasets de Hugging Face como DataFrames de pandas."""
from __future__ import annotations

import pandas as pd
from datasets import load_dataset


class HFDatasetLoader:
    """Descarga un dataset (o una de sus tablas) de Hugging Face y lo devuelve como DataFrame.

    Args:
        dataset_name: Identificador del dataset en Hugging Face, por ejemplo
            ``"bulutttt/olist-raw-data"``.
        config: Configuración del dataset, si publica varias.
        data_files: Archivo (o lista de archivos) del repositorio que se desea
            cargar. Útil cuando el dataset publica cada tabla como un archivo
            suelto (por ejemplo, varios ``.csv``) sin configuraciones.
        split: División que se desea cargar.
    """

    def __init__(
        self,
        dataset_name: str,
        config: str | None = None,
        data_files: str | list[str] | None = None,
        split: str = "train",
    ) -> None:
        self.dataset_name = dataset_name
        self.config = config
        self.data_files = data_files
        self.split = split
        self.df: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        """Descarga el dataset, lo convierte a DataFrame y lo retorna."""
        dataset = load_dataset(
            self.dataset_name,
            self.config,
            data_files=self.data_files,
            split=self.split,
        )
        self.df = dataset.to_pandas()
        return self.df

    @classmethod
    def load_tables(
        cls,
        dataset_name: str,
        tables: dict[str, str],
        split: str = "train",
        **kwargs,
    ) -> dict[str, pd.DataFrame]:
        """Carga varias tablas de un mismo dataset relacional.

        Args:
            dataset_name: Identificador del dataset en Hugging Face.
            tables: Diccionario ``{nombre_tabla: archivo_en_el_repositorio}``.
            split: División que se desea cargar.
            **kwargs: Parámetros adicionales para cada ``HFDatasetLoader``.

        Returns:
            Diccionario ``{nombre_tabla: DataFrame}``.
        """
        return {
            nombre: cls(dataset_name, data_files=archivo, split=split, **kwargs).load()
            for nombre, archivo in tables.items()
        }

    def info(self) -> dict[str, str | int | list[str] | None]:
        """Devuelve información básica del último DataFrame cargado."""
        if self.df is None:
            raise RuntimeError("Llama a load() primero.")
        return {
            "dataset": self.dataset_name,
            "config": self.config,
            "data_files": self.data_files,
            "split": self.split,
            "filas": len(self.df),
            "columnas": len(self.df.columns),
        }
