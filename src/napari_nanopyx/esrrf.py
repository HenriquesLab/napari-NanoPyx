import numpy as np
from nanopyx.methods import eSRRF, eSRRF3D, run_esrrf_parameter_sweep
from nanopyx.core.transform.sr_temporal_correlations import (
    calculate_eSRRF_temporal_correlations,
)
from napari.layers import Image
from napari import Viewer
from magicgui import magic_factory
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import warnings


@magic_factory(
    call_button="Generate",
    img={"label": "Image Stack"},
    magnification={"value": 2, "label": "Magnification", "min": 1, "max": 10},
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
        "label": "Reconstruction",
    },
    macro_pixel_correction={
        "value": True,
        "label": "Apply Macro Pixel Correction",
    },
    run_type={
        "widget_type": "RadioButtons",
        "orientation": "vertical",
        "value": "opencl",
        "choices": [
            ("Auto", "auto"),
            ("OpenCL", "opencl"),
            ("Threaded", "threaded"),
            ("Unthreaded", "unthreaded"),
        ],
        "label": "Run Type",
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
    macro_pixel_correction: bool = True,
    run_type: str = "auto",
):
    if frames_per_timepoint == 0:
        frames_per_timepoint = img.data.shape[0]
    elif frames_per_timepoint > img.data.shape[0]:
        frames_per_timepoint = img.data.shape[0]

    output_stack = []
    if run_type == "auto":
        run_type = None
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
            macro_pixel_correction=macro_pixel_correction,
            _force_run_type=run_type,
        )

        output_stack.append(
            calculate_eSRRF_temporal_correlations(output, reconstruction_order)
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


@magic_factory(
    call_button="Generate",
    img={"label": "Image Stack"},
    magnification={"value": 2, "label": "Magnification", "min": 1, "max": 10},
    sensitivities={
        "widget_type": "LineEdit",
        "label": "Sensitivities (comma-separated floats)",
        "value": "1.0",
    },
    radii={
        "widget_type": "LineEdit",
        "label": "Ring Radii (comma-separated floats)",
        "value": "1.5",
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
        "label": "Reconstruction",
    },
)
def parameter_sweep(
    viewer: Viewer,
    img: Image,
    magnification: int,
    sensitivities: str,
    radii: str,
    reconstruction_order: str,
):
    # Parse comma-separated floats from the string inputs
    sensitivities_list = [
        float(s.strip()) for s in sensitivities.split(",") if s.strip()
    ]
    radii_list = [float(r.strip()) for r in radii.split(",") if r.strip()]

    output_stack = run_esrrf_parameter_sweep(
        img.data,
        magnification=magnification,
        radii=radii_list,
        sensitivities=sensitivities_list,
        temporal_correlation=reconstruction_order,
        use_decorr=False,
        return_qnr=True,
    )

    if np.sum(np.isnan(output_stack)) > 0:
        warnings.warn(
            "The parameter sweep returned NaN values. This is likely caused by the generated frames being too similar, try splitting the image into blocks."
        )
        output_stack = np.nan_to_num(np.array(output_stack), nan=1.0)
    # Generate matplotlib QnR plot as image
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    ax.imshow(output_stack, cmap="berlin_r")
    ax.set_xticks(np.arange(len(radii_list)))
    ax.set_yticks(np.arange(len(sensitivities_list)))
    ax.set_xticklabels([str(r) for r in radii_list])
    ax.set_yticklabels([str(s) for s in sensitivities_list])

    for i in range(len(sensitivities_list)):
        for j in range(len(radii_list)):
            ax.text(
                j,
                i,
                round(output_stack[i, j], 2),
                ha="center",
                va="center",
                color="w",
            )

    ax.set_title("Parameter Sweep QnR")
    ax.set_xlabel("Radii")
    ax.set_ylabel("Sensitivities")
    fig.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    width, height = canvas.get_width_height()
    img_array = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8).reshape(
        (height, width, 4)
    )
    img_array = img_array[:, :, :3]  # Drop alpha channel to make it RGB
    plt.close(fig)

    if output_stack is not None:
        result_esrrf_name = img.name + "_qnr"
        try:
            viewer.layers[result_esrrf_name].data = img_array
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            viewer.add_image(img_array, name=result_esrrf_name)
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()


@magic_factory(
    call_button="Generate",
    img={"label": "Image Stack"},
    magnification_xy={
        "value": 2,
        "label": "Magnification XY",
        "min": 1,
        "max": 10,
    },
    magnification_z={
        "value": 2,
        "label": "Magnification Z",
        "min": 1,
        "max": 10,
    },
    sensitivity={"value": 1, "label": "Sensitivity", "min": 1, "max": 10},
    radius={"value": 1.5, "label": "Ring Radius XY", "min": 0.1, "max": 3.0},
    radius_z={"value": 1.5, "label": "Ring Radius Z", "min": 0.1, "max": 3.0},
    voxel_ratio={
        "value": 4.0,
        "label": "Voxel Ratio (Z/XY)",
        "min": 0.1,
        "max": 100.0,
    },
    do_intensity_weighting={
        "value": True,
        "label": "Apply Intensity Weighting",
    },
    reconstruction_order={
        "widget_type": "RadioButtons",
        "orientation": "vertical",
        "value": "average",
        "choices": [
            ("Average", "average"),
            ("Standard Deviation", "std"),
        ],
        "label": "Reconstruction",
    },
    macro_pixel_correction={
        "value": True,
        "label": "Apply Macro Pixel Correction",
    },
    run_type={
        "widget_type": "RadioButtons",
        "orientation": "vertical",
        "value": "opencl",
        "choices": [
            ("Auto", "auto"),
            ("OpenCL", "opencl"),
            ("Threaded", "threaded"),
            ("Unthreaded", "unthreaded"),
        ],
        "label": "Run Type",
    },
)
def generate_esrrf_3d_image(
    viewer: Viewer,
    img: Image,
    magnification_xy: int,
    magnification_z: int,
    sensitivity: float,
    radius: float,
    radius_z: float,
    voxel_ratio: float,
    do_intensity_weighting: bool,
    reconstruction_order: str,
    macro_pixel_correction: bool = True,
    run_type: str = "auto",
):
    if run_type == "auto":
        run_type = None

    output_stack = eSRRF3D(
        img.data,
        magnification_xy=magnification_xy,
        magnification_z=magnification_z,
        radius=radius,
        radius_z=radius_z,
        sensitivity=sensitivity,
        voxel_ratio=voxel_ratio,
        mode=reconstruction_order,
        macro_pixel_correction=macro_pixel_correction,
        doIntensityWeighting=do_intensity_weighting,
        _force_run_type=run_type,
    )

    if output_stack is not None:
        result_esrrf_name = img.name + "_esrrf3d"
        try:
            # if the layer exists, update the data
            viewer.layers[result_esrrf_name].data = output_stack
            viewer.dims.current_step = (0, magnification_z + 1, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(output_stack, name=result_esrrf_name)
            viewer.dims.current_step = (0, magnification_z + 1, 0, 0, 0)
            viewer.reset_view()
