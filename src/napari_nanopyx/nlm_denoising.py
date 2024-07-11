import numpy as np

from napari import Viewer
from napari.layers import Image
from magicgui import magic_factory
from nanopyx.core.transform import NLMDenoising


@magic_factory(
    call_button="Generate",
    img={"label": "Image Stack"},
    patch_size={"label": "Patch Size", "min": 2, "value": 7},
    patch_distance={
        "label": "Patch Distance",
        "min": 2,
        "value": 11,
    },
    h={"min": 0.0, "value": 0.1},
    sigma={"min": 0.0, "value": 0.0},
)
def denoising_img(
    viewer: Viewer,
    img: Image,
    patch_size: int = 7,
    patch_distance: int = 11,
    h: float = 0.1,
    sigma: float = 0.0,
):
    denoiser = NLMDenoising(verbose=False)
    output = denoiser.run(
        img.data,
        patch_size=patch_size,
        patch_distance=patch_distance,
        h=h,
        sigma=sigma,
    )
    output = np.array(output)

    if output is not None:
        result_output_name = img.name + "_denoised"
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
