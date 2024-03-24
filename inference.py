from dto import CoverPageMetadata
import es_metaextract_umsa_v2
import configparser

nlp = es_metaextract_umsa_v2.load()

config = configparser.ConfigParser()
config.read("config.conf", encoding="utf-8")
college_name = config["GENERAL"]["college_name"]


def extract_metadata(cover_page_text: str) -> CoverPageMetadata:
    doc = nlp(cover_page_text)

    department = [ent.text for ent in doc.ents if ent.label_ == "DEPARTMENT"][0]
    faculty = [ent.text for ent in doc.ents if ent.label_ == "FACULTY"][0]

    return CoverPageMetadata(
        advisors=[ent.text for ent in doc.ents if ent.label_ == "ADVISOR"],
        authors=[ent.text for ent in doc.ents if ent.label_ == "AUTHOR"],
        issued=[ent.text for ent in doc.ents if ent.label_ == "YEAR"][0],
        title=[ent.text for ent in doc.ents if ent.label_ == "TITLE"][0],
        thesis_degree_grantor=f"{college_name}. {faculty}. {department}"
    )


def extract_keywords(abstract: str) -> list[str]:
    return ["GEOLOGIA", "ANALISIS DE FACIES", "ESTRATIGRAFIA", "SEDIMENTOLOGIA", "ALTIPLANO NORTE"]