import numpy as np
from nanopyx.methods import SRRF
from nanopyx.core.transform.sr_temporal_correlations import (
    calculate_SRRF_temporal_correlations,
)
from napari.layers import Image
from napari import Viewer
from magicgui import magic_factory


@magic_factory(
    call_button="Generate",
    img={"label": "Image Stack"},
    magnification={"value": 4, "label": "Magnification", "min": 1, "max": 10},
    ring_radius={"value": 0.5, "label": "Ring Radius", "min": 0.1, "max": 3.0},
    frames_per_timepoint={
        "value": 0,
        "label": "Frames Per Time Point (0 = auto)",
        "min": 0,
        "max": 100000,
    },
    radiality_positivity_constraint={
        "value": True,
        "label": "Radiality Positivity Constraint",
    },
    do_intensity_weighting={
        "value": True,
        "label": "Apply Intensity Weighting",
    },
    reconstruction_order={
        "label": "Reconstruction:",
        "widget_type": "RadioButtons",
        "orientation": "vertical",
        "value": 1,
        "choices": [
            ("Sum", -1),
            ("Maximum", 0),
            ("Mean", 1),
            ("Autocorrelation Order 2", 2),
            ("Autocorrelation Order 3", 3),
            ("Autocorrelation Order 4", 4),
        ],
    },
)
def generate_srrf_image(
    viewer: Viewer,
    img: Image,
    frames_per_timepoint: int,
    magnification: int,
    ring_radius: float,
    radiality_positivity_constraint: bool,
    do_intensity_weighting: bool,
    reconstruction_order: int,
):
    if frames_per_timepoint == 0:
        frames_per_timepoint = img.data.shape[0]
    elif frames_per_timepoint > img.data.shape[0]:
        frames_per_timepoint = img.data.shape[0]

    output = []

    for i in range(img.data.shape[0] // frames_per_timepoint):
        block = img.data[
            i * frames_per_timepoint : (i + 1) * frames_per_timepoint
        ]
        result = SRRF(
            block,
            magnification=magnification,
            ringRadius=ring_radius,
            radialityPositivityConstraint=radiality_positivity_constraint,
            doIntensityWeighting=do_intensity_weighting,
        )

        output.append(
            calculate_SRRF_temporal_correlations(
                result[0], reconstruction_order
            )
        )

    output = np.array(output)

    if output is not None:
        result_output_name = img.name + "_srrf"
        try:
            # if the layer exists, update the data
            viewer.layers[result_output_name].data = output
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(output, name=result_output_name)
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
