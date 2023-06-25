import solidedge.seconnect as se


def derive_curve():
    """Derive curve of the last construction body"""
    # Derive curve
    doc = se.get_active_document()
    constructions = doc.Constructions
    derived_curves = constructions.DerivedCurves
    body = constructions.Item(constructions.Count).Body

    body_edges = body.Edges(se.constants.igQueryAll)
    edges = [body_edges.Item(1)]
    derived_curve = derived_curves.Add(1, edges, se.constants.igDCComposite)

    return derived_curve


def cleanup(drop_parents = None, ordered_delete = None, delete = None):
    """Clean up help commands, drop parents where necessary"""
    doc = se.get_active_document()
    is_ordered = doc.ModelingMode == se.constants.seModelingModeOrdered

    # Drop parents for ordered features
    if is_ordered and drop_parents is not None:
        drop_parents.DropParents()

    # Delete ordered features
    if is_ordered and ordered_delete is not None:
        ordered_delete.Delete()

    # Delete features
    if delete is not None:
        delete.Delete()
