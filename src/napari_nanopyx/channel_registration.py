import pathlib
from nanopyx.methods import channel_registration
from napari import Viewer
from tifffile import imread
from napari.layers import Image
from magicgui import magic_factory
from napari.utils.notifications import show_info


@magic_factory(
    call_button="Estimate",
    img={"label": "Image Stack"},
    ref_channel={"label": "Reference Channel", "value": 0},
    max_shift={
        "label": "Maximum Shift (pxs)",
        "value": 20,
        "min": 0,
        "max": 10000,
    },
    blocks_per_axis={"label": "Blocks per Axis", "value": 3, "min": 1},
    min_similarity={
        "label": "Minimum Similarity (0-1)",
        "value": 0.5,
        "min": 0,
        "max": 1,
        "step": 0.1,
    },
    save_translation_masks={"value": True, "label": "Save Translation Masks"},
    translation_mask_save_path={
        "label": "Save Translation Masks to",
        "mode": "w",
    },
    apply={"value": True, "label": "Apply"},
)
def estimate_channel_registration(
    viewer: Viewer,
    img: Image,
    ref_channel: int,
    max_shift: int,
    blocks_per_axis: int,
    min_similarity: float,
    save_translation_masks: bool,
    apply: bool,
    translation_mask_save_path=pathlib.Path.home() / "translation_mask",
):
    result = channel_registration.estimate_channel_registration(
        img.data,
        ref_channel,
        max_shift,
        blocks_per_axis,
        min_similarity,
        save_translation_masks=save_translation_masks,
        translation_mask_save_path=str(translation_mask_save_path),
        apply=apply,
    )

    if result is not None:
        result_name = img.name + "_aligned"
        try:
            # if the layer exists, update the data
            viewer.layers[result_name].data = result
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(result, name=result_name)
            viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()


@magic_factory(
    call_button="Correct",
    translation_mask_path={"mode": "r", "label": "Path to Translation Mask"},
)
def apply_channel_registration(
    viewer: Viewer, img: Image, translation_mask_path: pathlib.Path
):
    if str(translation_mask_path).split(".")[-1] != "tif":
        show_info("Translation Mask file should be .tif file")
    else:
        translation_mask = imread(str(translation_mask_path))
        result = channel_registration.apply_channel_registration(
            img.data, translation_masks=translation_mask
        )

        if result is not None:
            result_name = img.name + "_aligned"
            try:
                # if the layer exists, update the data
                viewer.layers[result_name].data = result
                viewer.dims.current_step = (0, 0, 0, 0, 0)
            except KeyError:
                # otherwise add it to the viewer
                viewer.add_image(result, name=result_name)
                viewer.dims.current_step = (0, 0, 0, 0, 0)
            viewer.reset_view()
