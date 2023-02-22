from nanopyx.methods.srrf import SRRF
from napari.layers import Image
from napari import Viewer
from napari.layers import Image
from magicgui import magic_factory


@magic_factory(call_button="Generate",
               img={"label": "Image Stack"},
               magnification={"value": 4,
                              "label": "Magnification",
                              "min": 1,
                              "max": 10},
               ring_radius={"value": 0.5,
                            "label": "Ring Radius",
                            "min": 0.1,
                            "max": 3.0},
               frames_per_timepoint={"value": 0,
                                     "label": "Frames Per Time Point (0 = auto)",
                                     "min": 0,
                                     "max": 100000},
               radiality_positivity_constraint={"value": True,
                                                "label": "Radiality Positivity Constraint"},
               do_intensity_weighting={"value": True,
                                       "label": "Apply Intensity Weighting"})
def generate_srrf_image(viewer: Viewer, img: Image, frames_per_timepoint: int, magnification: int, ring_radius: float,
                        radiality_positivity_constraint: bool, do_intensity_weighting: bool):
    
    srrf_generator = SRRF(magnification=magnification, ringRadius=ring_radius,
                          radialityPositivityConstraint=radiality_positivity_constraint,
                          doIntensityWeighting=do_intensity_weighting)
    
    result = srrf_generator.calculate(img.data, frames_per_timepoint)
    data_srrf = result[0]
    data_intensity = result[1]
    
    if data_srrf is not None:
        result_srrf_name = img.name + "_srrf"
        try:
            # if the layer exists, update the data
            viewer.layers[result_srrf_name].data = data_srrf
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(data_srrf, name=result_srrf_name)
    if data_intensity is not None:
        result_intensity_name = img.name + "_intensity"
        try:
            # if the layer exists, update the data
            viewer.layers[result_intensity_name].data = data_intensity
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(data_intensity, name=result_intensity_name)

