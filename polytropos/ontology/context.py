import os
import shutil
from dataclasses import dataclass
from typing import Optional, Any, Type


@dataclass
class Context:
    """Context"""
    conf_dir: str
    schemas_dir: str
    lookups_dir: str
    entities_input_dir: str
    entities_output_dir: str
    output_dir: str
    temp_dir: str
    no_cleanup: bool
    process_pool_chunk_size: int

    @classmethod
    def build(cls, conf_dir: str, data_dir: str, input_dir: Optional[str] = None, output_dir: Optional[str] = None, schemas_dir: Optional[str] = None,
              temp_dir: Optional[str] = None, no_cleanup: bool = False,
              process_pool_chunk_size: Optional[int] = None) -> "Context":

        entities_input_dir = input_dir or os.path.join(data_dir, 'entities')
        entities_output_dir = output_dir or entities_input_dir

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            temp_dir = temp_dir or os.path.join(output_dir, '_tmp')
        else:
            output_dir = os.path.join(conf_dir, "..") if conf_dir else "."
            temp_dir = temp_dir or os.path.join(data_dir, '_tmp')

        print(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

        return cls(conf_dir=conf_dir,
                   schemas_dir=schemas_dir or os.path.join(conf_dir, 'schemas'),
                   lookups_dir=os.path.join(data_dir, 'lookups'),
                   entities_input_dir=entities_input_dir,
                   entities_output_dir=entities_output_dir,
                   output_dir=output_dir,
                   temp_dir=temp_dir,
                   no_cleanup=no_cleanup,
                   process_pool_chunk_size=process_pool_chunk_size if process_pool_chunk_size is not None else 1000)

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Type, exc_val: Any, exc_tb: Any) -> None:
        if not self.no_cleanup:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
