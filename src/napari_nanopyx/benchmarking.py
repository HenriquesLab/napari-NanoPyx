import math
import napari
import nanopyx
import numpy as np
from magicgui import magic_factory


@magic_factory(
        call_button="Benchmark",
        n_benchmark_runs={"label": "Number of benchmark runs (min. 3 recommended)"},
        img_dims={
            "label": "Image Dimensions (px)",
            "value": 100,
            "min": 50
            },
        shift={
            "label": "Image Shift (px)",
            "value": 0,
            "min": 0
            },
        magnification={
            "label": "Magnification (int)",
            "value": 5,
            "min": 1
            },
        rotation={
            "label": "Rotation (degress)",
            "value": 15.0,
            "min": 0.0
            },
        conv_kernel_dims={
            "label": "Convolution Kernel Dimensions (px)",
            "value": 3,
            "min": 1
            }
)
def benchmark_nanopyx(viewer: napari.Viewer, n_benchmark_runs: int = 3, img_dims: int = 100, shift: int = 2, magnification: int = 5, rotation: float = 15.0, conv_kernel_dims: int = 23):
    """
    Runs benchmark tests for all LE methods.
    Args:
        n_benchmark_runs (int): The number of benchmark runs to perform. Default is 3.
        img_dims (int): The dimensions of the input image. Default is 100.
        shift (int): The amount of shift to apply to the image during benchmarking. Default is 2.
        magnification (int): The magnification factor to apply to the image during benchmarking. Default is 5.
        rotation (float): The rotation angle to apply to the image during benchmarking. Default is 0.2617993877991494 (equal to 15 degrees in radians).
        conv_kernel_dims (int): The dimensions of the convolution kernel to use during benchmarking. Default is 23.
    Returns:
        None
    """
    rotation = math.radians(rotation)
    img = np.random.random((img_dims, img_dims)).astype(np.float32)
    img_int = np.random.random((img_dims * magnification, img_dims * magnification)).astype(np.float32)
    kernel = np.ones((conv_kernel_dims, conv_kernel_dims)).astype(np.float32)

    bicubic_sm = nanopyx.core.transform._le_interpolation_bicubic.ShiftAndMagnify()
    bicubic_ssr = nanopyx.core.transform._le_interpolation_bicubic.ShiftScaleRotate()
    cr_sm = nanopyx.core.transform._le_interpolation_catmull_rom.ShiftAndMagnify()
    cr_ssr = nanopyx.core.transform._le_interpolation_catmull_rom.ShiftScaleRotate()
    l_sm = nanopyx.core.transform._le_interpolation_lanczos.ShiftAndMagnify()
    l_ssr = nanopyx.core.transform._le_interpolation_lanczos.ShiftScaleRotate()
    nn_sm = nanopyx.core.transform._le_interpolation_nearest_neighbor.ShiftAndMagnify()
    nn_ssr = nanopyx.core.transform._le_interpolation_nearest_neighbor.ShiftScaleRotate()
    nn_pt = nanopyx.core.transform._le_interpolation_nearest_neighbor.PolarTransform()

    conv2d = nanopyx.core.transform._le_convolution.Convolution()

    rad = nanopyx.core.transform._le_radiality.Radiality()
    rc = nanopyx.core.transform._le_roberts_cross_gradients.GradientRobertsCross()
    rgc = nanopyx.core.transform._le_radial_gradient_convergence.RadialGradientConvergence()

    esrrf = nanopyx.core.transform._le_esrrf.eSRRF()

    nlm = nanopyx.core.transform._le_nlm_denoising.NLMDenoising()

    methods = [bicubic_sm, bicubic_ssr, cr_sm, cr_ssr, l_sm, l_ssr, nn_sm, nn_ssr, nn_pt, conv2d, rad, rc, rgc, esrrf, nlm]

    total_runs = n_benchmark_runs * len(methods)
    pbr = napari.utils.progress(total=total_runs)

    pbr.set_description("Benchmarking Bicubic Shift and Magnify")
    for i in range(n_benchmark_runs):
        bicubic_sm.benchmark(img, shift, shift, magnification, magnification)
        pbr.update(1)

    pbr.set_description("Benchmarking Catmull-rom Shift and Magnify")
    for i in range(n_benchmark_runs):
        cr_sm.benchmark(img, shift, shift, magnification, magnification)
        pbr.update(1)

    pbr.set_description("Benchmarking Lanczos Shift and Magnify")
    for i in range(n_benchmark_runs):
        l_sm.benchmark(img, shift, shift, magnification, magnification)
        pbr.update(1)

    pbr.set_description("Benchmarking Nearest-neighbour Shift and Magnify")
    for i in range(n_benchmark_runs):
        nn_sm.benchmark(img, shift, shift, magnification, magnification)
        pbr.update(1)

    pbr.set_description("Benchmarking Bicubic Shift, Scale and Rotate")
    for i in range(n_benchmark_runs):
        bicubic_ssr.benchmark(img, shift, shift, magnification, magnification, rotation)
        pbr.update(1)

    pbr.set_description("Benchmarking Catmull-rom Shift, Scale and Rotate")
    for i in range(n_benchmark_runs):
        cr_ssr.benchmark(img, shift, shift, magnification, magnification, rotation)
        pbr.update(1)

    pbr.set_description("Benchmarking Lanczos Shift, Scale and Rotate")
    for i in range(n_benchmark_runs):
        l_ssr.benchmark(img, shift, shift, magnification, magnification, rotation)
        pbr.update(1)

    pbr.set_description("Benchmarking Nearest-neighbour Shift, Scale and Rotate")
    for i in range(n_benchmark_runs):
        nn_ssr.benchmark(img, shift, shift, magnification, magnification, rotation)
        pbr.update(1)

    pbr.set_description("Benchmarking Nearest-neighbour Polar transform")
    for i in range(n_benchmark_runs):
        nn_pt.benchmark(img, (img_dims, img_dims), "log")
        pbr.update(1)

    pbr.set_description("Benchmarking 2D Convolution")
    for i in range(n_benchmark_runs):
        conv2d.benchmark(img, kernel)
        pbr.update(1)

    pbr.set_description("Benchmarking Radiality calculation")
    for i in range(n_benchmark_runs):
        rad.benchmark(img, img_int)
        pbr.update(1)

    pbr.set_description("Benchmarking Robert's Cross calculation")
    for i in range(n_benchmark_runs):
        rc.benchmark(img)
        pbr.update(1)

    pbr.set_description("Benchmarking Radial Gradient Convergence calculation")
    for i in range(n_benchmark_runs):
        rgc.benchmark(img_int, img_int, img_int)
        pbr.update(1)

    pbr.set_description("Benchmarking eSRRF calculation")
    for i in range(n_benchmark_runs):
        esrrf.benchmark(img)
        pbr.update(1)

    pbr.set_description("Benchmarking Non-local Means Denoising")
    for i in range(n_benchmark_runs):
        nlm.benchmark(img)
        pbr.update(1)
    napari.utils.notifications.show_info("NanoPyx bencharking has finished, ready to zoom!")
