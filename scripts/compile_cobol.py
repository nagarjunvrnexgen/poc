from pathlib import Path
from typing import Final

from zoautil_py import mvscmd  # pyright: ignore[reportMissingModuleSource]
from zoautil_py.ztypes import (  # pyright: ignore[reportMissingModuleSource]
    DatasetDefinition,
    DDStatement,
    FileDefinition,
    ZOAUResponse,
)

# File paths
CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent
SRCLIB_DIR = ROOT_DIR / "srclib"
COPYLIB_DIR = ROOT_DIR / "copylib"
LOADLIB_DIR = ROOT_DIR / "loadlib"
SPOOL_DIR = ROOT_DIR / "spool"
DUMP_DIR = ROOT_DIR / "dump"
TEMP_DIR = ROOT_DIR / "tmp"


def get_mvs_cmd(response: ZOAUResponse):
    return "\n".join(response.command.split("--"))


def compile_cobol(
    filename: str,
    langprfx: str = "IGY640",
    libprfx: str = "CEE",
):

    OBJECT_DATASET = f"{TEMP_DIR}/{filename.rsplit('.', 1)[0]}.obj"

    dds: list[DDStatement] = []
    # STEPLIB
    dds.append(
        DDStatement(
            "STEPLIB",
            definition=[
                DatasetDefinition(f"{langprfx}.SIGYCOMP", disposition="SHR"),
                DatasetDefinition(f"{libprfx}.SCEERUN", disposition="SHR"),
                DatasetDefinition(f"{libprfx}.SCEERUN2", disposition="SHR"),
            ],
        )
    )

    # SYSIN
    dds.append(
        DDStatement(
            "SYSIN",
            FileDefinition(
                path_name=f"{SRCLIB_DIR}/{filename}",
                file_data="TEXT",
                status_group="ORDONLY",
                record_format="FB",
                record_length="80",
                block_size="3200",
            ),
        )
    )
    # SYSLIB
    dds.append(
        DDStatement(
            "SYSLIB",
            FileDefinition(path_name=f"{COPYLIB_DIR}", status_group="ORDONLY"),
        )
    )

    # SYSPRINT
    dds.append(
        DDStatement(
            "SYSPRINT",
            FileDefinition(
                path_name=f"{SPOOL_DIR}/comp.lst",
                status_group="OCREAT,OWRONLY,OTRUNC",
                file_data="TEXT",
            ),
        )
    )

    # SYSLIN
    dds.append(
        DDStatement(
            "SYSLIN",
            FileDefinition(
                OBJECT_DATASET,
                file_data="BINARY",
                normal_disposition="KEEP",
                status_group="OCREAT,ORDWR,OTRUNC",
                record_format="FB",
                record_length="80",
                block_size="800",
            ),
        )
    )

    # Temporary compiler work files.
    for i in range(1, 16):
        dds.append(
            DDStatement(
                f"SYSUT{i}",
                FileDefinition(
                    path_name=f"{TEMP_DIR}/sysut{i}",
                    file_data="BINARY",
                    status_group="OCREAT,ORDWR,OTRUNC",
                    normal_disposition="DELETE",
                    abnormal_disposition="DELETE",
                    record_format="FB",
                    record_length="80",
                    block_size="800",
                ),
            )
        )

    # # SYSMDECK
    # dds.append(
    #     DDStatement(
    #         "SYSMDECK",
    #         FileDefinition(
    #             path_name=f"{DUMP_DIR}/deck.obj",
    #             status_group="OCREAT,OWRONLY,OTRUNC",
    #             file_data="BINARY",
    #             normal_disposition="KEEP",
    #             abnormal_disposition="DELETE",
    #             record_format="FB",
    #             record_length="80",
    #             block_size="800",
    #         ),
    #     )
    # )
    dds: Final

    compile_response = mvscmd.execute(pgm="IGYCRCTL", dds=dds)  # pyright: ignore[reportUnknownMemberType]
    if compile_response.rc not in {0, 4}:
        print("Here is the MVS Command Executed by compiler.")
        print(get_mvs_cmd(compile_response))
        print(f"Compile error occurred with rc : {compile_response.rc}")
        print(f"Standard Error: {compile_response.stderr_response}")
    else:
        print(f"Compiled Succesfully with rc: {compile_response.rc}")
        print("Link Editing ....")
        linkedit_dds: list[DDStatement] = []

        # SYSLIB
        linkedit_dds.append(
            DDStatement(
                "SYSLIB",
                definition=list(  # noqa: C410
                    (
                        DatasetDefinition(f"{libprfx}.SCEELKEX"),
                        DatasetDefinition(f"{libprfx}.SCEELKED"),
                    )
                ),
            )
        )

        # SYSLIN
        linkedit_dds.append(
            DDStatement(
                "SYSLIN",
                FileDefinition(
                    OBJECT_DATASET, file_data="BINARY", status_group="ORDONLY"
                ),
            )
        )

        # SYSLMOD
        linkedit_dds.append(
            DDStatement(
                "SYSLMOD",
                FileDefinition(
                    path_name=f"{LOADLIB_DIR}/{filename.rsplit('.', 1)[0]}",
                    file_data="BINARY",
                    status_group="OCREAT,ORDWR,OTRUNC",
                    normal_disposition="KEEP",
                    path_mode="0755",
                ),
            )
        )

        # SYSPRINT
        linkedit_dds.append(
            DDStatement(
                "SYSPRINT",
                FileDefinition(
                    f"{SPOOL_DIR}/link.lst",
                    status_group="OWRONLY,OTRUNC",
                    file_data="TEXT",
                ),
            )
        )

        linkedit_response = mvscmd.execute(pgm="IEWL", dds=linkedit_dds)  # pyright: ignore[reportUnknownMemberType]
        if linkedit_response.rc not in {0, 4}:
            print("Here is the MVS Command Executed by Link Editor.")
            print(get_mvs_cmd(linkedit_response))
            print(f"Link Edit error occurred with rc : {linkedit_response.rc}")
            print(f"Standard Error: {linkedit_response.stderr_response}")
        else:
            print(f"Link Edit Succesfully with rc: {linkedit_response.rc}")


if __name__ == "__main__":
    compile_cobol(filename="loop.cbl")
