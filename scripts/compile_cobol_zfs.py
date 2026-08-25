from typing import Final

from zoautil_py import mvscmd  # pyright: ignore[reportMissingModuleSource]
from zoautil_py.ztypes import (  # pyright: ignore[reportMissingModuleSource]
    DatasetDefinition,
    DDStatement,
    FileDefinition,
    ZOAUResponse,
)


def get_mvs_cmd(inp: ZOAUResponse):
    return "\n".join(inp.command.split("--"))


def compile_cobol(
    source: str,
    copylib: str,
    loadlib: str,
    langprfx: str = "IGY640",
    libprfx: str = "CEE",
):

    OBJECT_DATASET = f"/u/vrex006/poc/tmp/{source.rsplit('.', 1)[0]}.obj"

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
                path_name=f"/u/vrex006/poc/srclib/{source}",
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
            FileDefinition(
                path_name=f"/u/vrex006/poc/{copylib}", status_group="ORDONLY"
            ),
        )
    )

    # SYSPRINT
    dds.append(
        DDStatement(
            "SYSPRINT",
            FileDefinition(
                path_name="/u/vrex006/poc/spool/comp.lst",
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
                    path_name=f"/u/vrex006/poc/tmp/sysut{i}",
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

    # SYSMDECK
    dds.append(
        DDStatement(
            "SYSMDECK",
            FileDefinition(
                path_name=f"/u/vrex006/poc/dump/{source.rsplit('.', 1)[0]}.dmp",
                status_group="OCREAT,OWRONLY,OTRUNC",
                file_data="TEXT",
                normal_disposition="DELETE",
                abnormal_disposition="KEEP",
                record_format="FB",
                record_length="80",
                block_size="3200",
            ),
        )
    )
    dds: Final

    compile_response = mvscmd.execute(pgm="IGYCRCTL", dds=dds)  # pyright: ignore[reportUnknownMemberType]
    if compile_response.rc not in {0, 4}:
        print("Here is the MVS Command Executed by compiler.")
        print(get_mvs_cmd(compile_response))
        print(f"Compile error occurred with rc : {compile_response.rc}")
        print(f"Standard Error: {compile_response.stderr_response}")
        print(f"Standard Output: {compile_response.stdout_response}")
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
                    OBJECT_DATASET, 
                    file_data="BINARY", 
                    status_group="ORDONLY", 
                    normal_disposition="DELETE"
                ),
            )
        )

        # SYSLMOD
        linkedit_dds.append(
            DDStatement(
                "SYSLMOD",
                FileDefinition(
                    path_name=f"/u/vrex006/poc/{loadlib}/{source.rsplit('.', 1)[0]}",
                    file_data="BINARY",
                    status_group="OCREAT,ORDWR,OTRUNC",
                    normal_disposition="KEEP",
                    path_mode="0755"
                ),
            )
        )

        # SYSPRINT
        linkedit_dds.append(
            DDStatement(
                "SYSPRINT",
                FileDefinition(
                    "/u/vrex006/poc/spool/link.lst",
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
    compile_cobol(source="vote.cbl", copylib="copylib", loadlib="loadlib")
