import numpy as np
import pymatching

from surface_code_sim.qiskit_frontend.layout import RotatedCodeLayout, build_layout
from surface_code_sim.qiskit_frontend.sampler import SampledSyndromes


def _build_boundary_matching(detector_count: int) -> pymatching.Matching:
    m = pymatching.Matching()
    boundary = detector_count
    m.set_boundary_nodes({boundary})
    for i in range(detector_count):
        m.add_edge(i, boundary, fault_ids={i})
    return m


class MwpmDecoder:
    def __init__(self, layout: RotatedCodeLayout):
        self.layout = layout

    @classmethod
    def from_distance(cls, distance: int) -> "MwpmDecoder":
        layout = build_layout(distance)
        return cls(layout)

    def decode(self, syndromes: SampledSyndromes) -> dict:
        shots = syndromes.x_detection.shape[0]

        z_detectors = syndromes.z_detection.reshape(shots, -1)
        x_detectors = syndromes.x_detection.reshape(shots, -1)

        matcher_z = _build_boundary_matching(z_detectors.shape[1])
        matcher_x = _build_boundary_matching(x_detectors.shape[1])

        z_out = matcher_z.decode_batch(z_detectors)
        x_out = matcher_x.decode_batch(x_detectors)

        z_logical = (np.sum(z_out, axis=1) % 2).astype(np.uint8)
        x_logical = (np.sum(x_out, axis=1) % 2).astype(np.uint8)
        return {"x_logical": x_logical, "z_logical": z_logical}
