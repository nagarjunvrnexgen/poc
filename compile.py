from typing import Final

from zoautil_py import datasets as ds  # pyright: ignore[reportMissingModuleSource]
from zoautil_py import mvscmd  # pyright: ignore[reportMissingModuleSource]
from zoautil_py.ztypes import (  # pyright: ignore[reportMissingModuleSource]
    DatasetDefinition,
    DDStatement,
)


def compile_cobol(
    source: str,
    member: str,
    copylib: str,
    loadlib: str,
    langprfx: str = "IGY640",
    libprfx: str = "CEE",
    temp_hlq: str = "VREX006",
):

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

    # SYSIN
    dds.append(
        DDStatement(
            "SYSIN", DatasetDefinition(f"{source}({member})", disposition="SHR")
        )
    )
    # SYSLIB
    dds.append(DDStatement("SYSLIB", DatasetDefinition(copylib, disposition="SHR")))

    # SYSPRINT
    dds.append(
        DDStatement(
            "SYSPRINT",
            DatasetDefinition("VREX006.SPOOL(COMPLIST)", normal_disposition="KEEP"),
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
    if compile_response.rc not in {0, 4}:
        print(f"Compile error occured with rc : {compile_response.rc}")
        print(compile_response.stderr_response)
    else:
        print(f"Compiled Successfully with rc: {compile_response.rc}")
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
                DatasetDefinition("VREX006.SPOOL(LINKLIST)", normal_disposition="KEEP"),
            )
        )

        linkedit_response = mvscmd.execute(pgm="IEWL", dds=linkedit_dds)
        print(f"Link edit complete with rc: {linkedit_response.rc}")
        print(linkedit_response)


if __name__ == "__main__":
    compile_cobol(
        source="VREX006.SRCLIB",
        member="HI",
        copylib="VREX006.COPYLIB",
        loadlib="VREX006.LOADLIB",
    )
