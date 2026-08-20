from zoautil_py import mvscmd  # pyright: ignore[reportMissingModuleSource]
from zoautil_py.ztypes import (  # pyright: ignore[reportMissingModuleSource]
    DatasetDefinition,
    DDStatement,
)


def run(
    loadlib: str,
    pgm: str,
):
    dds: list[DDStatement] = []
    dds.append(DDStatement("STEPLIB", DatasetDefinition(loadlib, disposition="SHR")))
    print("Executing...")
    response = mvscmd.execute(pgm=pgm, dds=dds)
    print(f"Executed with rc: {response.rc}")
    print(response)


if __name__ == "__main__":
    run(loadlib="VREX006.LOADLIB", pgm="HI")
