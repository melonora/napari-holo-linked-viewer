from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from napari.utils.events import EmitterGroup, Event
from napari.utils.notifications import NotificationSeverity

from hlv.utils.utils import napari_notification


@dataclass
class DataModel:
    """
    Model keeping track of the files that have been loaded and which fields should be used for creating the plot.
    """

    events: EmitterGroup = field(init=False, default=None, repr=True)
    _csv_paths: Sequence[Path] = field(default_factory=set, init=True)
    _path_csv_mapper: dict[str, pd.DataFrame] = field(
        default_factory=dict, init=True
    )
    _base_image_dir: Path = field(default=None, init=False)
    _annotation_column: str = field(init=False)
    _axis_columns: Sequence[str] = field(default_factory=set, init=True)
    _active_x_column: str = field(init=False)
    _active_y_column: str = field(init=False)
    _filter_cols: Sequence[str] = field(default_factory=list, init=True)
    _col_string_filter: str = field(default="UMAP", init=False)

    def __post_init__(self) -> None:
        """Allow fields in the dataclass to emit events when changed."""
        self.events = EmitterGroup(source=self, csv_paths=Event)

    @property
    def csv_paths(self) -> set[Path]:
        return self._csv_paths

    @csv_paths.setter
    def csv_paths(self, path: Sequence[Path] | Path) -> None:
        if path.is_dir():
            if len(paths := set(path.glob("*.csv"))) != 0:
                self._csv_paths.update(paths)
            else:
                napari_notification(
                    f"'{path}' does not contain any csv.",
                    severity=NotificationSeverity.ERROR,
                )
        elif isinstance(path, list):
            if any(p.suffix != ".csv" for p in path):
                napari_notification(
                    f"'{path}' contains at least one file that is not a csv.",
                    severity=NotificationSeverity.ERROR,
                )
            self._csv_paths.update(set(path))
        elif path.suffix() == ".csv":
            self._csv_paths.add(path)
        else:
            napari_notification(
                f"'{path}' is not a csv file. Please provide a directory or a csv file.",
                severity=NotificationSeverity.ERROR,
            )
        self.events.csv_paths()

    @property
    def path_csv_mapper(self) -> Mapping[str, pd.DataFrame]:
        return self._path_csv_mapper

    @path_csv_mapper.setter
    def path_csv_mapper(self, mapper: Mapping[str, pd.DataFrame]) -> None:
        self._path_csv_mapper = mapper

    @property
    def axis_columns(self) -> set[str]:
        return self._axis_columns

    @axis_columns.setter
    def axis_columns(self, columns: Iterable[str]) -> None:
        self._axis_columns = columns

    @property
    def col_string_filter(self) -> str:
        return self._col_string_filter

    @col_string_filter.setter
    def col_string_filter(self, col_string_filter: str) -> None:
        self._col_string_filter = col_string_filter
