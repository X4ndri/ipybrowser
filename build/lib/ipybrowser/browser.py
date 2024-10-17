from IPython.display import display, clear_output
from ipydatagrid import DataGrid
import ipywidgets as widgets
from warnings import warn
from pathlib import Path
from typing import *
import pandas as pd
import numpy as np
import os


TO_MB = 1048576
class Browser:
    """Creates a datagrid showing the files and allows navigation and choosing a path"""

    def __init__(self, data_grid_kwargs: dict = None, parent_path=None):
        self.path_textbox = widgets.Text(description="Selected:")
        self.path_textbox.layout.width = "700px"
        self.path_textbox.on_submit(self.textbox_navigate_callback)
        self.back_button = widgets.Button(description="Back")
        self.select_button = widgets.Button(description="Select")
        self.back_button.on_click(self._go_back)
        if parent_path is not None:
            parent_path = self.get_absolute_path(parent_path)
            self.current_path = Path(parent_path)
        else:
            self.current_path = Path.cwd()
        self.path_textbox.value = self.current_path.as_posix()
        self.df = self._create_file_dataframe(self.current_path)
        self.current_index = 0
        self.previous_path = ''
        self.sidecar = None
        if data_grid_kwargs is None:
            data_grid_kwargs = dict()

        self._default_widths = {
         'Name': 350,
         'Path' : 400,
         'Size' : 100
        }
        
        self.datagrid = DataGrid(self.df,
        selection_mode="row",
        layout={"height": "350px", "width": "1000px"},
        base_row_size=24,
        index_name="file",
        column_widths=self._default_widths,
        **data_grid_kwargs)
        self.datagrid.on_cell_click(self._update_grid)
        self.datagrid.select(
            row1=0,
            column1=0)

    def _create_file_dataframe(self, path) -> pd.DataFrame:
        try:
            file_info = []
            files = os.listdir(path)
            if files == []:
                file_info.append({"Name": '<Empty>', "Size": '<na>', "Path": "<na>"})
                return pd.DataFrame(file_info)
            for file in files:
                file_path = os.path.join(path, file)
                size = os.path.getsize(file_path)/TO_MB if os.path.isfile(file_path) else "<Folder>"
                if size != "<Folder>":
                    size = f"{size:.2f} MB"
                file_info.append({"Name": file, "Size": size, "Path": file_path})
            
            # sort
            file_info = self._sort_folders_and_files(file_info)
            data = pd.DataFrame(file_info)
            return data
        except Exception as e:
            print("Error")
            print(f"Error: {e}")
            return pd.DataFrame()

    def _sort_folders_and_files(self, arr) -> list:

        # sep folders from files
        folders = [item for item in arr if item["Size"] == "<Folder>"]
        files = [item for item in arr if item["Size"] != "<Folder>"]
        
        # sort alph. by the name vlaue
        sorted_folders = sorted(folders, key=lambda x: x["Name"])
        sorted_files = sorted(files, key=lambda x: x["Name"])
        
        return sorted_folders + sorted_files


    def _get_selected_row(self) -> Union[int, None]:

        print(self.datagrid.selections)
        r1 = self.datagrid.selections[0]["r1"]
        r2 = self.datagrid.selections[0]["r2"]
        if r1 != r2:
            warn("Only single row selection is currently allowed")
            return

        # get corresponding dataframe index from currently visible dataframe
        # since filtering etc. is possible
        index = self.datagrid.get_visible_data().index[r1]

        return index   

    def _go_back(self, ev) -> None:
        selpath = self.current_path
        if selpath.is_dir():
            self.current_path = self.current_path.parent
            self.path_textbox.value = self.current_path.as_posix()
            self.df = self._create_file_dataframe(self.current_path)
            self.datagrid.data = self.df
        else:
            self.current_path = self.current_path.parent.parent
            self.path_textbox.value = self.current_path.as_posix()
            self.df = self._create_file_dataframe(self.current_path)
            self.datagrid.data = self.df
        
    def get_selected_path(self, row):
        path = self.df.iloc[row]["Path"]
        return path

    def _update_grid(self, ev):
        path = Path(self.get_selected_path(ev['row']))
        self.path_textbox.value = path.as_posix()
        if os.path.isdir(path):
            self.current_path = path
            self.df = self._create_file_dataframe(path)
            self.datagrid.data=self.df
        else:
            self.current_path = path

    def hide(self):
        self.datagrid.layout.visibility = 'hidden'
        self.path_textbox.layout.visibility = 'hidden'
        self.back_button.layout.visibility = 'hidden'

    def unhide(self):
        self.datagrid.layout.visibility = 'visible'
        self.path_textbox.layout.visibility = 'visible'
        self.back_button.layout.visibility = 'visible'
    
    def show(self, sidecar: bool = False):
        # TODO: I'll impelement the sidecar func later
        widget = widgets.VBox([
            widgets.HBox([self.path_textbox, self.back_button]),
            self.datagrid
        ])
        if sidecar:
            from sidecar import Sidecar
            sc = Sidecar(title='browser')
            with sc:
                display(widget)
                return

        else:
            return widget

    def textbox_navigate_callback(self, change):
        try:
            self.df = self._create_file_dataframe(change.value)
            self.datagrid.data=self.df
            self.current_path = change.value
        except:
            warn("error while navigating")
    def get_absolute_path(self, shorthand_path):
        # Expand the ~ to the full home directory path
        expanded_path = os.path.expanduser(shorthand_path)
        # Get the absolute path
        absolute_path = os.path.abspath(expanded_path)
        return absolute_path