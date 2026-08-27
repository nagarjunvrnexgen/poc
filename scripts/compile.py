from typing import Final

from zoautil_py import datasets as ds  # pyright: ignore[reportMissingModuleSource]
from zoautil_py import mvscmd  # pyright: ignore[reportMissingModuleSource]
from zoautil_py.ztypes import (  # pyright: ignore[reportMissingModuleSource]
    DatasetDefinition,
    DDStatement,
    FileDefinition,
)


def compile_cobol_from_uss(
    source_path: str,
    member: str,
    copylib: str,
    loadlib: str,
    langprfx: str = "IGY640",
    libprfx: str = "CEE",
    temp_hlq: str = "VREX006",
):
    """
    Same as compile_cobol, but SYSIN is read directly from a zFS/USS file
    (e.g. /u/yourid/poc/hi.cbl) instead of a PDS member.

    source_path: full absolute path to the .cbl file on zFS, e.g.
                 "/u/yourid/poc/hi.cbl"
    """

    OBJECT_DATASET = ds.tmp_name(temp_hlq)

    dds: list[DDStatement] = []
    # STEPLIB
    dds.append(
        DDStatement(
            "STEPLIB",
            definition=list(  # noqa: C410
                (
                    DatasetDefinition(f"{langprfx}.SIGYCOMP", disposition="SHR"),
                    DatasetDefinition(f"{libprfx}.SCEERUN", disposition="SHR"),
                    DatasetDefinition(f"{libprfx}.SCEERUN2", disposition="SHR"),
                )
            ),
        )
    )

    # SYSIN -- now a zFS/USS file instead of a PDS member.
    # file_data="TEXT" tells z/OS to treat the byte stream as text and
    # convert it based on the file's tag (must be IBM-1047/EBCDIC to match
    # what IGYCRCTL expects -- verify with `chtag -p` before running).
    # record_length/record_format/block_size mirror the FB 80 layout the
    # compiler expects, since a zFS file is normally just a byte stream.
    dds.append(
        DDStatement(
            "SYSIN",
            FileDefinition(
                path_name=source_path,
                file_data="TEXT",
                status_group="ORDONLY",
                record_format="FB",
                record_length="80",
                block_size="3200",
            ),
        )
    )

    # SYSLIB -- copybooks still come from a PDS, unchanged
    dds.append(DDStatement("SYSLIB", DatasetDefinition(copylib, disposition="SHR")))

    # SYSPRINT
    dds.append(
        DDStatement(
            "SYSPRINT",
            DatasetDefinition("VREX006.POC.SPOOL(COMPLIST)", normal_disposition="KEEP"),
            
        )
    )

    # SYSLIN
    dds.append(
        DDStatement(
            "SYSLIN",
            DatasetDefinition(
                OBJECT_DATASET,
                disposition="NEW",
                normal_disposition="KEEP",
                abnormal_disposition="DELETE",
                conditional_disposition="DELETE",
                type="SEQ",
                primary_unit="CYL",
                primary="1",
                secondary_unit="CYL",
                secondary="1",
                record_format="FB",
                record_length="80",
                block_size="3200",
            ),
        )
    )

    # Temporary compiler work files.
    for i in range(1, 16):
        dds.append(
            DDStatement(
                f"SYSUT{i}",
                DatasetDefinition(
                    dataset_name=ds.tmp_name(temp_hlq),  # pyright: ignore[reportUnknownMemberType]
                    disposition="NEW",
                    normal_disposition="DELETE",
                    abnormal_disposition="DELETE",
                    conditional_disposition="DELETE",
                    type="SEQ",
                    primary_unit="CYL",
                    primary="1",
                    secondary_unit="CYL",
                    secondary="1",
                    record_format="FB",
                    record_length="80",
                    block_size="3200",
                ),
            )
        )

    # SYSMDECK
    dds.append(
        DDStatement(
            "SYSMDECK",
            DatasetDefinition(
                dataset_name=ds.tmp_name(temp_hlq),
                type="SEQ",
                disposition="NEW",
                normal_disposition="KEEP",
                abnormal_disposition="DELETE",
                conditional_disposition="DELETE",
                record_format="FB",
                record_length="80",
                block_size="3200",
                primary="1",
                primary_unit="CYL",
                secondary="1",
                secondary_unit="CYL",
            ),
        )
    )
    dds: Final

    compile_response = mvscmd.execute(pgm="IGYCRCTL", dds=dds)
    with open("compile_response.txt", "w") as f:
        f.write(f"Standard Output:\n{compile_response.stdout_response}\n")
        f.write(f"Standard Error:\n{compile_response.stderr_response}\n")
        f.write(f"Return Code: {compile_response.rc}\n")
    
    if compile_response.rc not in {0, 4}:
        print(compile_response.stderr_response)
        print(f"Compile error occurred with rc : {compile_response.rc}")
        
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

        linkedit_dds.append(
            DDStatement("SYSLIN", DatasetDefinition(OBJECT_DATASET, disposition="SHR"))
        )

        # SYSLMOD
        linkedit_dds.append(
            DDStatement("SYSLMOD", DatasetDefinition(f"{loadlib}({member})"))
        )

        # SYSPRINT
        linkedit_dds.append(
            DDStatement(
                "SYSPRINT",
                DatasetDefinition("VREX006.POC.SPOOL(LINKLIST)", normal_disposition="KEEP"),
            )
        )

        linkedit_response = mvscmd.execute(pgm="IEWL", dds=linkedit_dds)
        print(f"Link edit complete with rc: {linkedit_response.rc}")
        print(linkedit_response)


if __name__ == "__main__":
    compile_cobol_from_uss(
        source_path="/u/vrex006/poc/srclib/emp.cbl",
        member="EMP",
        copylib="VREX006.POC.COPYLIB",
        loadlib="VREX006.POC.LOADLIB",
    )