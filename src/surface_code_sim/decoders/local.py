import numpy as np

from surface_code_sim.qiskit_frontend import SampledSyndromes


class LocalDecoder:
    def decode(self, syndromes: SampledSyndromes) -> dict:
        x_fail = (np.sum(syndromes.z_detection, axis=(1, 2)) > 0).astype(np.uint8)
        z_fail = (np.sum(syndromes.x_detection, axis=(1, 2)) > 0).astype(np.uint8)
        return {"x_logical": x_fail, "z_logical": z_fail}
