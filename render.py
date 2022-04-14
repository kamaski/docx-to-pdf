import logging
import os
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from docxtpl import DocxTemplate
from xlsxtpl.writerx import BookWriter

from config import RENDERED_DIR

logging.basicConfig()
logger = logging.getLogger("processing")
logger.setLevel(level=logging.INFO)


def get_file_name_and_extension(file_path):
    file_name = ''
    file_extension = ''
    # Get filename from path using os
    file_name = os.path.basename(file_path)
    file_extension = file_name.split('.', 1)[1]
    print('file_name:', file_name)
    print('file_extension', file_extension)
    return file_name, file_extension


class Render:
    @classmethod
    def render_file(cls, file_path: str, context: Dict[str, Any]) -> Path:
        logger.info(f"Received context: {context}")
        file_itself, file_extension = get_file_name_and_extension(file_path)
        #
        #
        print('file_path: ', file_path)
        if file_extension == 'xlsx':
            doc = BookWriter(file_path)
        else:
            doc = DocxTemplate(file_path)
        doc.render(context)
        file_path = cls.get_path(
            base_name=context.get("FullName") or context.get("CashDocumentNumber")
        )

        logger.info("Saving rendered file to: {path}".format(path=file_path))
        doc.save(file_path)

        return file_path

    @classmethod
    def get_path(cls, base_name: str = None) -> Path:
        if base_name is None:
            base_name = str(uuid4())
        path = Path(RENDERED_DIR / base_name.lower().replace(" ", "-"))
        path.mkdir(parents=True, exist_ok=True)
        return path.joinpath("rendered-agreement.docx")
