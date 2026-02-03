from __future__ import annotations

from typing import Literal, Optional, TypedDict


EntityType = Literal[
    "Drawing",
    "View",
    "Callout",
    "Note",
    "Part",
    "Subassembly",
    "Feature",
    "Dimension",
    "Material",
    "Process",
    "WeldSpec",
    "ToleranceSpec",
    "InspectionRequirement",
]


class DrawingProperties(TypedDict, total=False):
    drawing_number: str
    revision: str
    title: str
    date: str
    units: str
    scale: str


class ViewProperties(TypedDict, total=False):
    view_type: str
    label: str


class CalloutProperties(TypedDict, total=False):
    label: str


class NoteProperties(TypedDict, total=False):
    note_id: str
    text: str
    category: str


class PartProperties(TypedDict, total=False):
    name: str
    part_id: str


class SubassemblyProperties(TypedDict, total=False):
    name: str


class FeatureProperties(TypedDict, total=False):
    feature_type: str
    geometry_type: str
    location_ref: str


class DimensionProperties(TypedDict, total=False):
    value: str
    unit: str
    dimension_type: str
    tolerance: str


class MaterialProperties(TypedDict, total=False):
    grade: str
    spec: str


class ProcessProperties(TypedDict, total=False):
    name: str


class WeldSpecProperties(TypedDict, total=False):
    weld_type: str
    size: str
    spacing: str
    standard_ref: str


class ToleranceSpecProperties(TypedDict, total=False):
    text: str


class InspectionRequirementProperties(TypedDict, total=False):
    text: str


class Entity(TypedDict, total=False):
    type: EntityType
    properties: dict
    source_doc_id: Optional[str]
    source_view_id: Optional[str]
    bounding_box: Optional[dict]
    source_text: Optional[str]


__all__ = [
    "EntityType",
    "DrawingProperties",
    "ViewProperties",
    "CalloutProperties",
    "NoteProperties",
    "PartProperties",
    "SubassemblyProperties",
    "FeatureProperties",
    "DimensionProperties",
    "MaterialProperties",
    "ProcessProperties",
    "WeldSpecProperties",
    "ToleranceSpecProperties",
    "InspectionRequirementProperties",
    "Entity",
]
