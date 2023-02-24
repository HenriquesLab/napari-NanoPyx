from nanopyx.core.sr.frc import FIRECalculator
from nanopyx.core.sr.decorr import DecorrAnalysis
from nanopyx.core.sr.error_map import ErrorMap

import os
import pathlib
import numpy as np
import pandas as pd
from napari.layers import Image
from napari import Viewer
from magicgui import magic_factory
from napari.utils.notifications import show_info

@magic_factory(call_button="Analyse",
               img={"label": "Image Stack"},
               pixel_size={"value": 1,
                           "min": 0.0000001,
                           "max": 10000000,
                           "step": 0.000001,
                           "label": "Pixel Size"},
               units={"value": "px",
                      "label": "Units"},
               save_path={"label": "Save Results Table to:",
                          "mode": "w"})
def calculate_frc(img: Image, pixel_size: float, units: str,
                              save_path=pathlib.Path.home()):
    calculator = FIRECalculator(pixel_size=pixel_size, units=units)
    fire_numbers = np.zeros((img.data.shape[0]-1))
    results_table = pd.DataFrame(columns=["Frame 1", "Frame 2", "Pixel Size", "Units", "FIRE"])
    for i in range(1, img.data.shape[0]):
        fire_n = calculator.calculate_fire_number(img.data[i-1], img.data[i])
        fire_numbers[i-1] = fire_n
        results_table.loc[len(results_table)] = [i-1, i, pixel_size, units, fire_n]
    show_info(f"Mean Resolution: {np.mean(fire_numbers)} {units}")
    table_name = img.name + "_FRC_results.csv"
    results_table.to_csv(str(save_path) + os.sep + table_name)

@magic_factory(call_button="Analyse",
               img={"label": "Image Stack"},
               pixel_size={"value": 1,
                           "min": 0.0000001,
                           "max": 10000000,
                           "step": 0.000001,
                           "label": "Pixel Size"},
               units={"value": "px",
                      "label": "Units"},
               save_path={"label": "Save Results Table to:",
                          "mode": "w"})
def calculate_decorr_analysis(img: Image, pixel_size: float, units: str,
                              save_path=pathlib.Path.home()):
    if len(img.data.shape) == 2:
        image = img.data.reshape(1, img.data.shape[0], img.data.shape[1])
    else:
        image = img.data
    print(pixel_size, units)
    decorr = DecorrAnalysis(image, pixel_size=pixel_size, units=units)
    decorr.run_analysis()
    show_info(f"Resolution: {decorr.resolution} {units}")
    table_name = img.name + "_DecorrAnalysis_results.csv"
    decorr.results_table.to_csv(str(save_path) + os.sep + table_name)
    
    

def calculate_error_map(viewer: Viewer, img_ref: Image, img_sr: Image):
    
    squirrel_error_map = ErrorMap()
    squirrel_error_map.optimise(img_ref.data, img_sr.data)
    
    result = squirrel_error_map.imRSE
    
    if result is not None:
        result_name = img_sr.name + "_error_map"
        try:
            # if the layer exists, update the data
            viewer.layers[result_name].data = result
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(result, name=result_name, colormap="viridis")
    