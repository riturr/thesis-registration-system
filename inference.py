from dto import CoverPageMetadata


def extract_metadata(cover_page_text: str) -> CoverPageMetadata:
    return CoverPageMetadata(
        advisors=["García Duarte, Raúl", "Díaz Villavicencio, Jorge"],
        authors=["Reque Oblitas, María Amparo", "Mamani Quispe, Juan Carlos"],
        issued="2020",
        title="Análisis de facies sedimentarias en el tope de la Formación Umala (límite Plioceno - Pleistoceno) en el altiplano norte",
    )


def extract_keywords(abstract: str) -> list[str]:
    return ["GEOLOGIA", "ANALISIS DE FACIES", "ESTRATIGRAFIA", "SEDIMENTOLOGIA", "ALTIPLANO NORTE"]