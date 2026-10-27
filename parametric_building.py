# FILE: parametric_building_simple.py
# PURPOSE: Ultra-Simple Parametric Building Tool - Following Original FEATURE 4
# AUTHOR: Hugo Velasco (Hugo VelP)

import pandas as pd
from typing import List, Dict

class SimpleParametricBuilder:
    def __init__(self, model):
        self.model = model

    def create_basic_building(self, config):
        """Create basic building using NewSteelDeck (2 lines)"""
        return self.model.File.NewSteelDeck(
            config['stories'], config['x_bays'], config['y_bays'],
            config['x_spacing'], config['y_spacing'], config['story_height']
        )

    def get_bay_coordinates(self, grid, bay, config):
        """Calculate bay coordinates from grid+bay"""
        if isinstance(grid, str):  # Grid letter (A, B, C)
            grid_index = ord(grid.upper()) - ord('A')
            x1 = grid_index * config['x_spacing']
            x2 = x1
            y1 = (bay - 1) * config['y_spacing']
            y2 = bay * config['y_spacing']
        else:  # Grid number (1, 2, 3)
            y1 = (grid - 1) * config['y_spacing']
            y2 = y1
            x1 = (bay - 1) * config['x_spacing']
            x2 = bay * config['x_spacing']
        return x1, x2, y1, y2

    def create_brace_by_bay(self, grid, bay, brace_type="X", stories="all", config=None):
        """Create braces in specified bay (10-15 lines)"""
        x1, x2, y1, y2 = self.get_bay_coordinates(grid, bay, config)

        story_list = list(range(1, config['stories'] + 1)) if stories == "all" else stories

        for story in story_list:
            z1 = (story - 1) * config['story_height']
            z2 = story * config['story_height']

            if brace_type == "X":
                self.model.FrameObj.AddByCoord(x1, y1, z1, x2, y2, z2, "", "HSS6X6X3/8")
                self.model.FrameObj.AddByCoord(x2, y1, z1, x1, y2, z2, "", "HSS6X6X3/8")
            elif brace_type == "V":
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                self.model.FrameObj.AddByCoord(x1, y1, z1, mid_x, mid_y, z2, "", "HSS6X6X3/8")
                self.model.FrameObj.AddByCoord(x2, y2, z1, mid_x, mid_y, z2, "", "HSS6X6X3/8")

    def read_excel_config(self, excel_path):
        """Read building config from Excel"""
        building_params = pd.read_excel(excel_path, sheet_name="Building")
        braced_bays = pd.read_excel(excel_path, sheet_name="BracedBays")

        config = building_params.set_index('Parameter')['Value'].to_dict()
        config['braced_bays'] = braced_bays.to_dict('records')
        return config

    def create_parametric_building(self, excel_path):
        """Main function (5 lines)"""
        config = self.read_excel_config(excel_path)
        self.create_basic_building(config)

        for brace in config['braced_bays']:
            self.create_brace_by_bay(brace['grid'], brace['bay'], brace['type'], brace.get('stories', 'all'), config)

        return f"Created building with {len(config['braced_bays'])} braced bays"