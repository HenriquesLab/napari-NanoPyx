import os
import pathlib

import numpy as np
import pandas as pd
from magicgui import magic_factory
from nanopyx.core.analysis.decorr import DecorrAnalysis
from nanopyx.core.analysis.frc import FIRECalculator
from nanopyx.core.transform.sr_error_map import ErrorMap
from napari import Viewer
from napari.layers import Image
from napari.utils.notifications import show_info


@magic_factory(
    call_button="Analyse",
    img={"label": "Image Stack"},
    frame_1={"label": "Frame 1", 
           "value": 0,
           "min": 0,
           "max": 10000000, 
           "step": 1},
    frame_2={"label": "Frame 2", 
           "value": 1,
           "min": 0,
           "max": 10000000, 
           "step": 1},
    pixel_size={
        "value": 1,
        "min": 0.0000001,
        "max": 10000000,
        "step": 0.000001,
        "label": "Pixel Size",
    },
    units={"value": "px", "label": "Units"},
)
def calculate_frc(
    viewer: Viewer, img: Image, frame_1: int, frame_2: int, pixel_size: float, units: str
):
    calculator = FIRECalculator(pixel_size=pixel_size, units=units)
    calculator.calculate_fire_number(img.data[frame_1], img.data[frame_2])
    # fire_numbers = np.zeros((img.data.shape[0] - 1))
    # results_table = pd.DataFrame(
    #     columns=["Frame 1", "Frame 2", "Pixel Size", "Units", "FIRE"]
    # )
    # for i in range(1, img.data.shape[0]):
    #     fire_n = calculator.calculate_fire_number(img.data[i - 1], img.data[i])
    #     fire_numbers[i - 1] = fire_n
    #     results_table.loc[len(results_table)] = [
    #         i - 1,
    #         i,
    #         pixel_size,
    #         units,
    #         fire_n,
    #     ]
    plot = calculator.plot_frc_curve()
    if plot is not None:
        result_name = img.name + "_frc_plot"
        try:
            viewer.layers[result_name].data = plot
        except KeyError:
            viewer.add_image(plot, name=result_name)
    # table_name = img.name + "_FRC_results.csv"
    # results_table.to_csv(str(save_path) + os.sep + table_name)


@magic_factory(
    call_button="Analyse",
    img={"label": "Image Stack"},
    frame={"label": "Frame", 
           "value": 0,
           "min": 0,
           "max": 10000000, 
           "step": 1},
    pixel_size={
        "value": 1,
        "min": 0.0000001,
        "max": 10000000,
        "step": 0.000001,
        "label": "Pixel Size",
    },
    units={"value": "px", "label": "Units"},
)
def calculate_decorr_analysis(viewer: Viewer, img: Image, frame: int, pixel_size: float, units: str):

    decorr = DecorrAnalysis(pixel_size=pixel_size, units=units)
    if frame > img.data.shape[0]:
        frame = img.data.shape[0]-1
    if len(img.data.shape) > 2:
        # plot dims 720, 960, 4
        if len(img.data.shape) == 3:
            decorr.run_analysis(img.data[frame])
            plot = decorr.plot_results()

    else:
        image = img.data
        decorr.run_analysis(image)
        plot = decorr.plot_results()
        
    if plot is not None:
        result_name = img.name + "_decorr_plot"
        try:
            viewer.layers[result_name].data = plot
        except KeyError:
            viewer.add_image(plot, name=result_name)


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
