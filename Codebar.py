from pathlib import Path
import barcode
import barcode.codex
from barcode.writer import ImageWriter
import uuid

class Codebar:
    def __init__(self, target_dir:Path):
        self.target_dir = target_dir

    def save(self, code):
        """
        Generate the barcode and save into file target_dir/UUID.png

        Returns:
            The full path of the generated image file
        """
        c39 = barcode.codex.Code39(code, writer=ImageWriter(), add_checksum=True)
        filepath = c39.save(self.target_dir / str(uuid.uuid4()), options={"write_text": False})
        return Path(filepath)


if __name__ == "__main__":
    import os
    work = os.path.expandvars("%APPDATA%") / Path('CDItiquettes/workk')
    work.mkdir(parents=True, exist_ok=True)
    bc = Codebar(work)
    bc.save("1234")

