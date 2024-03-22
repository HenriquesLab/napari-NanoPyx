import numpy as np
from magicgui import magic_factory
from nanopyx.core.analysis.decorr import DecorrAnalysis
from nanopyx.core.analysis.frc import FIRECalculator
from nanopyx.core.transform.error_map import ErrorMap
from napari import Viewer
from napari.layers import Image


@magic_factory(
    call_button="Analyse",
    img={"label": "Image Stack"},
    frame_1={
        "label": "Frame 1",
        "value": 0,
        "min": 0,
        "max": 10000000,
        "step": 1,
    },
    frame_2={
        "label": "Frame 2",
        "value": 1,
        "min": 0,
        "max": 10000000,
        "step": 1,
    },
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
    viewer: Viewer,
    img: Image,
    frame_1: int,
    frame_2: int,
    pixel_size: float,
    units: str,
):
    calculator = FIRECalculator(pixel_size=pixel_size, units=units)
    calculator.calculate_fire_number(img.data[frame_1], img.data[frame_2])
    plot = calculator.plot_frc_curve()
    if plot is not None:
        result_name = img.name + "_frc_plot"
        try:
            viewer.layers[result_name].data = plot
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            viewer.add_image(plot, name=result_name)
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()


@magic_factory(
    call_button="Analyse",
    img={"label": "Image Stack"},
    frame={"label": "Frame", "value": 0, "min": 0, "max": 10000000, "step": 1},
    pixel_size={
        "value": 1,
        "min": 0.0000001,
        "max": 10000000,
        "step": 0.000001,
        "label": "Pixel Size",
    },
    units={"value": "px", "label": "Units"},
)
def calculate_decorr_analysis(
    viewer: Viewer, img: Image, frame: int, pixel_size: float, units: str
):
    decorr = DecorrAnalysis(pixel_size=pixel_size, units=units)
    if frame > img.data.shape[0]:
        frame = img.data.shape[0] - 1
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
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            viewer.add_image(plot, name=result_name)
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()


@magic_factory(
        img_ref={
            "label":"Reference Image"
        },
        img_sr={
            "label":"Super-resolved Image"
        }
)
def calculate_error_map(viewer: Viewer, img_ref: Image, img_sr: Image):
    squirrel_error_map = ErrorMap()
    if len(img_ref.data.shape) == 3:
        ref = np.mean(img_ref.data, axis=0)
    elif len(img_ref.data.shape) == 2:
        ref = img_ref.data
    else:
        print("Error: Reference image shape must be 2 or 3 (mean projected)")
    if len(img_sr.data.shape) == 3:
        sr = np.mean(img_sr.data, axis=0)
    elif len(img_sr.data.shape) == 2:
        sr = img_sr.data
    else:
        print("Error: Reference image shape must be 2 or 3 (mean projected)")
    squirrel_error_map.optimise(ref, sr)

    result = np.asarray(squirrel_error_map.imRSE, dtype=np.float32)

    if result is not None:
        result_name = img_sr.name + "_error_map"
        try:
            # if the layer exists, update the data
            viewer.layers[result_name].data = result
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(result, name=result_name, colormap="viridis")
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
