from __future__ import annotations

import logging
import win32com.client
# noinspection PyUnresolvedReferences
from pywintypes import com_error

from config import lang
from solidedge.comwrapper import COMWrapper

logger = logging.getLogger("LSF")

constants: COMWrapper
geometry: COMWrapper

app: COMWrapper


def connect() -> bool:
    """Attempt to connect to SolidEdge instance"""
    global app, constants, geometry
    try:
        constants = win32com.client.gencache.EnsureModule("{C467A6F5-27ED-11D2-BE30-080036B4D502}", 0, 1, 0).constants
        geometry = win32com.client.gencache.EnsureModule('{3E2B3BE1-F0B9-11D1-BDFD-080036B4D502}', 0, 1, 0)
        app = win32com.client.GetActiveObject("SolidEdge.Application")

        # Wrap COM objects
        constants = COMWrapper(constants)
        geometry = COMWrapper(geometry)
        app = COMWrapper(app)

    except Exception as e:
        print(e)
        logger.error(lang.errors.se_not_running)
        return False
    return True


def get_active_document() -> None | COMWrapper:
    """Ask for active document. If it's not part, return None"""
    try:
        doc = app.ActiveDocument
    except com_error:
        logger.error(lang.errors.se_no_document)
        return None

    if doc.Type != constants.igPartDocument:
        logger.error(lang.errors.se_not_part_document)
        return None
    return doc


def is_document_open(document) -> bool:
    """Check whether a document is open or not"""
    for i in range(1, app.Documents.Count + 1):
        if document == app.Documents.Item(i):
            return True
    return False
