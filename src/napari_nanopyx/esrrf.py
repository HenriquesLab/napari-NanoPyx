import numpy as np
from nanopyx.methods import eSRRF
from nanopyx.core.transform.sr_temporal_correlations import (
    calculate_eSRRF_temporal_correlations,
)
from napari.layers import Image
from napari import Viewer
from magicgui import magic_factory


@magic_factory(
    call_button="Generate",
    img={"label": "Image Stack"},
    magnification={"value": 5, "label": "Magnification", "min": 1, "max": 10},
    sensitivity={"value": 1, "label": "Sensitivity", "min": 1, "max": 10},
    radius={"value": 1.5, "label": "Ring Radius", "min": 0.1, "max": 3.0},
    frames_per_timepoint={
        "value": 0,
        "label": "Frames Per Time Point (0 = auto)",
        "min": 0,
        "max": 100000,
    },
    do_intensity_weighting={
        "value": True,
        "label": "Apply Intensity Weighting",
    },
    reconstruction_order={
        "widget_type": "RadioButtons",
        "orientation": "vertical",
        "value": "AVG",
        "choices": [
            ("Average", "AVG"),
            ("Variance", "VAR"),
            ("Autocorrelation", "TAC2"),
        ],
        "label": "Shift Calculation Method",
    },
)
def generate_esrrf_image(
    viewer: Viewer,
    img: Image,
    magnification: int,
    sensitivity: float,
    radius: float,
    frames_per_timepoint: int,
    do_intensity_weighting: bool,
    reconstruction_order: str,
):
    if frames_per_timepoint == 0:
        frames_per_timepoint = img.data.shape[0]
    elif frames_per_timepoint > img.data.shape[0]:
        frames_per_timepoint = img.data.shape[0]

    output_stack = []

    for i in range(img.data.shape[0] // frames_per_timepoint):
        block = img.data[
            i * frames_per_timepoint : (i + 1) * frames_per_timepoint
        ]
        output = eSRRF(
            block,
            magnification=magnification,
            radius=radius,
            sensitivity=sensitivity,
            doIntensityWeighting=do_intensity_weighting,
        )

        output_stack.append(
            calculate_eSRRF_temporal_correlations(
                output[0], reconstruction_order
            )
        )

    output_stack = np.array(output_stack)

    if output_stack is not None:
        result_esrrf_name = img.name + "_esrrf"
        try:
            # if the layer exists, update the data
            viewer.layers[result_esrrf_name].data = output_stack
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(output_stack, name=result_esrrf_name)
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
