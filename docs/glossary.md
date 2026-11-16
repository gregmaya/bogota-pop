# Glossary · Glosario

Every acronym and local term the project uses, in English and Spanish. Issues, pull requests and docs spell out an acronym the first time it appears and can link here (ADR-0011).

Rows marked **to confirm / por confirmar** are terms whose meaning is not yet verified. Don't use them in issues until they are.

Cada sigla y término local del proyecto, en inglés y español. Los issues, pull requests y documentos escriben la sigla completa la primera vez y pueden enlazar aquí (ADR-0011).

Las filas marcadas **to confirm / por confirmar** son términos cuyo significado aún no está verificado. No se usan en issues hasta confirmarlos.

## Institutions and sources · Instituciones y fuentes

| Term · Término | English | Español |
| --- | --- | --- |
| **DANE** | Departamento Administrativo Nacional de Estadística: Colombia's national statistics office | Departamento Administrativo Nacional de Estadística: la oficina nacional de estadística |
| **SDP** | Secretaría Distrital de Planeación: Bogotá's planning department | Secretaría Distrital de Planeación de Bogotá |
| **UAECD** | Unidad Administrativa Especial de Catastro Distrital: Bogotá's cadastre office (Catastro Bogotá) | Unidad Administrativa Especial de Catastro Distrital (Catastro Bogotá) |
| **CNPV 2018** | Censo Nacional de Población y Vivienda 2018: the 2018 national population and housing census | Censo Nacional de Población y Vivienda 2018 |
| **MGN** | Marco Geoestadístico Nacional: DANE's geographic framework of census areas (sectors, sections, blocks) | Marco Geoestadístico Nacional: el marco geográfico del DANE (sectores, secciones, manzanas) |
| **EM** | Encuesta Multipropósito: Bogotá's large household survey, run by DANE with SDP | Encuesta Multipropósito: la gran encuesta de hogares de Bogotá, del DANE con la SDP |
| **Encuesta de Movilidad** | Bogotá's travel survey; reports population by transport analysis zone (ZAT) | Encuesta de Movilidad de Bogotá; reporta población por zona de análisis de transporte (ZAT) |
| **POT** | Plan de Ordenamiento Territorial: the city's land-use plan; Bogotá's current one is Decreto 555 | Plan de Ordenamiento Territorial; el vigente en Bogotá es el Decreto 555 |
| **WorldPop** | Global gridded population estimates (University of Southampton); used as a benchmark only | Estimaciones mundiales de población en grilla (Universidad de Southampton); solo como referencia |
| **GHS-POP** | Global Human Settlement Layer population grid (European Commission, Joint Research Centre); benchmark only | Grilla de población del Global Human Settlement Layer (Comisión Europea, JRC); solo como referencia |
| **HRSL** | High Resolution Settlement Layer (Meta); benchmark only | High Resolution Settlement Layer (Meta); solo como referencia |
| **INPEC** | Instituto Nacional Penitenciario y Carcelario: runs Colombia's prisons and publishes their population | Instituto Nacional Penitenciario y Carcelario: administra las cárceles y publica su población |
| **IDOM / ODUR** | **To confirm.** A layer named in the plan's open research questions; what it is and its licence are Phase 1 questions | **Por confirmar.** Capa mencionada en las preguntas abiertas del plan; qué es y su licencia son preguntas de la Fase 1 |

## Geography · Geografía

| Term · Término | English | Español |
| --- | --- | --- |
| **Manzana** | City block. Census blocks (MGN) and cadastral blocks (UAECD) are different geometries with different codes | Manzana. Las censales (MGN) y las catastrales (UAECD) tienen geometrías y códigos distintos |
| **Sección** | Census section: a group of census blocks in the MGN | Sección censal: grupo de manzanas censales del MGN |
| **Clase** | DANE's split of a municipality into cabecera (1), centro poblado (2) and rural disperso (3). People DANE cannot show in a block (LEA residents, anonymised blocks) are published at this level | División del DANE de cada municipio en cabecera (1), centro poblado (2) y rural disperso (3). Las personas que el DANE no puede mostrar por manzana (residentes de LEA, manzanas anonimizadas) se publican en este nivel |
| **LEA** | Lugar Especial de Alojamiento: group quarters such as prisons, barracks, care homes, convents and student residences | Lugar Especial de Alojamiento: cárceles, cuarteles, hogares geriátricos, conventos, residencias estudiantiles |
| **UPZ** | Unidad de Planeamiento Zonal: planning zone; the geography of the population projections | Unidad de Planeamiento Zonal; geografía de las proyecciones de población |
| **UPL** | Unidad de Planeamiento Local: the planning units introduced by POT Decreto 555 | Unidad de Planeamiento Local: unidades introducidas por el POT, Decreto 555 |
| **ZAT** | Zona de Análisis de Transporte: transport analysis zone of the Encuesta de Movilidad | Zona de Análisis de Transporte de la Encuesta de Movilidad |
| **UTIEM** | **To confirm.** Territorial unit of the Encuesta Multipropósito | **Por confirmar.** Unidad territorial de la Encuesta Multipropósito |
| **Rural disperso** | Dispersed rural area; out of scope for v1 (high census omission) | Área rural dispersa; fuera del alcance de la v1 (alta omisión censal) |
| **H3** | A global grid of hexagons (Uber); outputs are published on it at resolution 9 or 10 | Grilla global de hexágonos (Uber); se publican resultados en resolución 9 o 10 |

## Cadastre and housing · Catastro y vivienda

| Term · Término | English | Español |
| --- | --- | --- |
| **Lote** | Cadastral lot: the unit the model estimates (kept private, ADR-0006) | Lote catastral: unidad que estima el modelo (privada, ADR-0006) |
| **CHIP** | **To confirm.** UAECD's identifier for each predio (`PRECHIP` in Predio); its expansion is not yet verified | **Por confirmar.** Identificador de cada predio de la UAECD (`PRECHIP` en Predio); su expansión no está verificada |
| **Predio** | Cadastral property; a lot can hold many predios (e.g. flats in a building) | Predio; un lote puede tener muchos (p. ej. apartamentos de un edificio) |
| **PH / NPH** | Propiedad horizontal / no propiedad horizontal: buildings divided into separately owned units (flats) vs single-owner lots | Propiedad horizontal / no propiedad horizontal |
| **Vigencia** | The year a cadastral record applies to; UAECD publishes a new vigencia each year | Año al que corresponde el registro catastral; la UAECD publica una vigencia cada año |
| **Estrato** | Socioeconomic stratum (1–6) assigned to dwellings, used for utility tariffs | Estrato socioeconómico (1 a 6) de las viviendas, usado en tarifas de servicios |
| **Inquilinato** | Rooming house where households rent single rooms | Inquilinato: vivienda donde los hogares arriendan cuartos |
| **Licencia de construcción** | Building permit | Licencia de construcción |
| **Curaduría urbana** | Office that issues building permits in Bogotá | Curaduría urbana: entidad que expide licencias en Bogotá |
| **Tratamiento urbanístico** | POT zoning category (e.g. renovation, development) that sets what can be built | Tratamiento urbanístico del POT (p. ej. renovación, desarrollo) |
| **Edificabilidad** | Permitted building volume under the POT | Edificabilidad permitida por el POT |
| **Derecho de petición** | Formal legal request to a public body for information; it must answer within legal deadlines | Derecho de petición: solicitud formal a una entidad pública, con plazos legales de respuesta |

## Source fields · Campos de las fuentes

| Field · Campo | English | Español |
| --- | --- | --- |
| **TP27_PERSO** | Persons counted per census block (MGN integrado, manzana layer) | Personas censadas por manzana (MGN integrado, capa de manzanas) |
| **STP27_PERS** | Persons counted, in DANE's department, municipality and clase layers only. Not in the block layer, despite what ADR-0004 and ADR-0006 say | Personas censadas, solo en las capas de departamento, municipio y clase. No está en la capa de manzanas, aunque lo digan los ADR-0004 y ADR-0006 |
| **DATO_ANM** | Name of the geographic level a unit's census data is published at. It is `MANZANA` for every Bogotá block, so it does not mark anonymised blocks (ADR-0004 and ADR-0006 call it a flag; that is wrong). Anonymised blocks would show 0 persons; in Bogotá's cabecera no household people are missing from blocks (plan, Q2) | Nombre del nivel geográfico en que se publican los datos censales de la unidad. Es `MANZANA` en todas las manzanas de Bogotá, así que no marca las manzanas anonimizadas (los ADR-0004 y ADR-0006 lo llaman marca; es un error). Una manzana anonimizada aparecería con 0 personas; en la cabecera de Bogotá no falta ninguna persona de hogares en las manzanas (plan, Q2) |
| **CLAS_CCDGO** | Clase code: 1 cabecera, 2 centro poblado, 3 rural disperso | Código de clase: 1 cabecera, 2 centro poblado, 3 rural disperso |
| **STPERSON_L** | Persons in group quarters (LEA), clase layer | Personas en lugares especiales de alojamiento (LEA), capa de clase |
| **STPERSON_S** | Persons in households (not in LEA), clase layer. `STPERSON_L` + `STPERSON_S` = `STP27_PERS` | Personas en hogares (fuera de LEA), capa de clase. `STPERSON_L` + `STPERSON_S` = `STP27_PERS` |
| **PERSONAS_L** | Persons in group quarters (LEA) per unit. 0 in every Bogotá block: DANE publishes LEA residents at clase level | Personas en lugares especiales de alojamiento (LEA) por unidad. 0 en todas las manzanas de Bogotá: el DANE publica a los residentes de LEA a nivel de clase |
| **LOTCODIGO / LOTECODIGO / USOCLOTE / BARMANPRE** | The same 12-character cadastral lot code, named differently in Lote, Construcción, Uso and Predio | El mismo código de lote catastral de 12 caracteres, con nombre distinto en Lote, Construcción, Uso y Predio |
| **CONNPISOS** | Number of floors of a building (UAECD Construcción) | Número de pisos de una construcción (Construcción de la UAECD) |
| **USOTUSO** | Use code of a built area in UAECD Uso. **To confirm:** code meanings need UAECD's data dictionary | Código de uso de un área construida en Uso de la UAECD. **Por confirmar:** el significado de los códigos requiere el diccionario de datos de la UAECD |
| **PREUVIVIEN, PREUSOPH, PRECLASE, PRECDESTIN** | **To confirm.** Predio fields read as dwelling flag, PH flag, class and economic destination; meanings and codes need UAECD's data dictionary | **Por confirmar.** Campos de Predio que parecen indicar vivienda, PH, clase y destino económico; significado y códigos requieren el diccionario de datos de la UAECD |

## Method · Método

| Term · Término | English | Español |
| --- | --- | --- |
| **Dasymetric mapping** | Redistributing population from large areas to smaller ones using ancillary data (here, residential cadastre) | Mapeo dasimétrico: redistribuir población de áreas grandes a pequeñas con datos auxiliares (aquí, el catastro residencial) |
| **CEDS** | Cadastral-based Expert Dasymetric System (Maantay et al., 2007): the method behind the MVP | Cadastral-based Expert Dasymetric System (Maantay et al., 2007): método base del MVP |
| **MVP** | Minimum viable product: the first working model, release v0.1 | Producto mínimo viable: el primer modelo funcional, versión v0.1 |
| **Housing-unit method** | Population = dwellings × occupancy rate × persons per household (v1.0) | Método de unidades de vivienda: viviendas × ocupación × personas por hogar (v1.0) |
| **Control total** | Official total the estimates must add up to (DANE–SDP projections, ADR-0008) | Total de control: total oficial al que deben sumar las estimaciones (ADR-0008) |
| **Raking** | Scaling estimates so they match the control total in each area | Ajuste (raking): escalar estimaciones para que coincidan con el total de control de cada área |
| **Back-cast** | Modelling a past year (2018) and comparing it with known values (the census) | Retroestimación: modelar un año pasado (2018) y compararlo con valores conocidos (el censo) |
| **MAPE** | Mean absolute percentage error | Error porcentual absoluto medio |
| **RMSE** | Root mean square error | Raíz del error cuadrático medio |
| **Census omission** | People the census missed (3.1% in Bogotá per DANE) | Omisión censal: personas que el censo no contó (3,1 % en Bogotá según el DANE) |

## Tools and formats · Herramientas y formatos

| Term · Término | English | Español |
| --- | --- | --- |
| **CRS / EPSG:9377** | Coordinate reference system; the project uses MAGNA-SIRGAS Origen Nacional (EPSG code 9377) | Sistema de referencia de coordenadas; el proyecto usa MAGNA-SIRGAS Origen Nacional (código EPSG 9377) |
| **GeoParquet** | Columnar file format for geographic data; the internal format | Formato de archivo columnar para datos geográficos; formato interno |
| **PMTiles** | Single-file map tiles read directly by the web viewer | Teselas de mapa en un solo archivo que lee el visor web |
| **Etapas** | The viewer mode that shows each pipeline stage as a map layer | Modo del visor que muestra cada etapa del pipeline como capa |
| **ADR** | Architecture Decision Record: a short file recording one decision (docs/decisions/) | Registro de decisión de arquitectura (docs/decisions/) |
| **CI** | Continuous integration: GitHub Actions checks run on every push | Integración continua: verificaciones de GitHub Actions en cada push |
| **DOI** | Digital Object Identifier: a permanent citable link, minted by Zenodo for major releases | Identificador de objeto digital: enlace permanente citable, emitido por Zenodo |
| **Tag / Release** | A named point in the git history / a GitHub page with notes and files built on a tag | Etiqueta: punto con nombre en el historial / Release: página de GitHub con notas y archivos sobre una etiqueta |
