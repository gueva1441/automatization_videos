# F7a — Fuentes de Orleans (R1 descubrimiento + R2 descarga)

Topic `ba6c3cac-f7r3` · R1 `f7a-1` · costo R1 US$ 0.4773 (529.5 s) · 20 fuentes aceptadas del grounding, 21 descartadas · **10 documentos bajados**.

Ficha: `exacta` / `similar x` = la del modelo para esa URL del grounding; `ficha_flash` = URL del grounding que el modelo no listó, fichada por Flash. Ninguna URL sale del modelo.

Código: `researcher_steps/research_v3.py` (R1 `discover_sources`, R2 `download_sources` + `refine_fichas`) · runner `lab/hyperframes/f7/f7a_fuentes_orleans.py` · copias versionadas: `fuentes_orleans.json` (R1, con grounding y descartes) y `manifest_orleans.json` (R2: url, sha1, bytes, idioma, intentos, recorte). Los archivos bajados están en `data/scripts/_steps/ba6c3cac-f7r3/fuentes/` (fuera de git).

## Lectura

**Los 10 documentos** (≥ 8 pedidos): ACLU *Abandoned & Abused* completo (F01, PDF enlazado desde la portada), los 400 testimonios resumidos de la ACLU (F03, PDF), HRW 2005 (F02, por Wayback: hrw.org da 403), las cartas de presos de HRW 2005 (F05, por Wayback), la carta de hallazgos del DOJ de 2009 (F09, la copia en PDF de Prison Legal News; es OCR), la nota de la ACLU sobre abusos (F06), Vera Institute 2015 (F08), The Lens 2025 (F10, copia local de F6c: misma URL, no se volvió a pedir), la página del libro *Voices from the Storm* (F12, 3.7 k: solo la ficha de los narradores) y la lista de casos del DOJ (F04: 200 k caracteres con 6 menciones de OPP; R3 lee solo esa ventana).

**Contra la lista del handoff (§4):**

| pedido | estado |
|---|---|
| ACLU completo | ✔ F01 (+ F03, los 400 testimonios) |
| HRW 2005 | ✔ F02 (Wayback) + F05 (cartas) |
| DOJ 2010 findings letter | ✔ F09 (la carta es del 11-sep-2009; copia de PLN) |
| BBC 2006 | ✖ ninguna URL de la BBC en el grounding (2 búsquedas + la pista); la página de WordPress que lo reproduce (F11) devolvió 429 |
| Times-Picayune / NOLA semana del 29-ago-2005 | ✖ el modelo nombra la nota del Pulitzer («Help us, please») pero no sale en el grounding |
| The Lens 2025 | ✔ F10 |
| Toledo Blade 2005 | ✖ no sale en el grounding |
| Fallo Waganfeald/Kunkel | ✖ justia/findlaw no salen en el grounding; sí la nota de CBS sobre el jurado (F14), fuera del cupo de 10 |

**Decisiones de F7a** (en el código, comentadas):
1. **Candidatos = URLs del grounding.** El primer diseño (aceptar la ficha del modelo solo si su URL era idéntica a una del grounding) descartó 18 de 23 fuentes reales: el modelo escribe `aclu.org/report/…` y la búsqueda vio `aclu.org/publications/…`. Ahora la URL sale siempre del grounding y el modelo solo le pone la ficha (misma URL, o mismo sitio y ≥ 50 % de las palabras de la ruta). Las URLs del grounding que el modelo no fichó las ficha Flash (1 llamada); los listados (`/category/`, `/tag/`) no son documentos. Ninguna URL inventada entra: las 21 fichas del modelo sin URL del grounding están abajo.
2. **Pro con temperatura 0.7** (como el research viejo). Con 0.0, Pro contestó de memoria en 4 de 4 búsquedas (0 chunks de grounding). Aun con 0.7, algunas búsquedas vuelven sin grounding: hasta 2 reintentos con «no respondas de memoria» (eso explica la mayor parte del costo de R1).
3. **Una búsqueda por pista** del analista que los focos no trajeron (5 de 8).
4. **Ficha leída del documento** (`refine_fichas`, 1 Flash con los primeros 2.5 k caracteres de cada uno): la de la búsqueda era una conjetura sobre la URL (la carta del DOJ venía como «académico, sin año»). La ficha de la búsqueda queda en `ficha_busqueda`.
5. **R2:** portada corta con un PDF del mismo sitio → se baja el PDF (ACLU). Duplicados por hash o por texto (otra edición del mismo PDF: F07 = F01). Mínimo 3 000 caracteres (las páginas de 2 k eran resúmenes o portadas). Videos sin texto (YouTube) no se piden. Wayback: API de disponibilidad + copia cruda (`id_`), con 3 s de pausa; un 429 se anota y no se reintenta en bucle (en la primera corrida archive.org dio 429; HRW 2005 bajó en un reintento una hora después).
6. **PDF → texto:** `pdftotext` (poppler) primero, si está instalado; `pdfplumber` por columnas y `pypdf` de respaldo. Ver F7b §3: con `pdfplumber` el informe de la ACLU (dos columnas) salía intercalado y la cita literal no aparecía.
7. **Recorte a 300 k por secciones:** F01 pierde las notas finales (98 k) y 71 k del cuerpo; F03 (los 400 testimonios, 473 k) pierde 175 k: unos 150 testimonios quedan sin leer. Ver propuestas en F7b.

| id | tipo | año | prio | ficha | título | url | bytes | caracteres txt | idioma | ok | nota |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F01 | informe_oficial | 2006 | 1 | exacta | Abandoned & Abused: Orleans Parish Prisoners in the Wake of Hurricane  | https://www.aclu.org/publications/abandoned-and-abused | 4064571 | 296928 | en | ✔ | vía pdf_enlazado; fuera la cola desde «ENDNOTES» (98482 caracteres); cortado en el último párrafo antes de 300000 (71139 caracteres fuera) |
| F02 | informe_oficial | 2005 | 1 | exacta | New Orleans: Prisoners Abandoned in Floodwaters | https://www.hrw.org/news/2005/09/21/new-orleans-prisoners-abandoned-floodwaters | 40461 | 6351 | en | ✔ | vía wayback |
| F03 | testimonio | 2006 | 1 | exacta | Testimonials from Inmates Incarcerated at Orleans Parish Prison during | https://www.aclu.org/documents/summaries-400-testimonials-inmates-incarcerated-orleans-parish-prison-during-hurricane-katrina | 506990 | 297707 | en | ✔ | vía pdf_enlazado; cortado en el último párrafo antes de 300000 (174992 caracteres fuera) |
| F04 | informe_oficial | 2009 | 1 | exacta | Special Litigation Section Case Summaries | https://www.justice.gov/crt/special-litigation-section-case-summaries | 410786 | 200675 | en | ✔ |  |
| F05 | testimonio | 2005 | 1 | exacta | Excerpts of letters from prisoners abandoned in Katrina | https://www.hrw.org/news/2005/10/30/excerpts-letters-prisoners-abandoned-katrina | 142990 | 11094 | en | ✔ | vía wayback |
| F06 | informe_oficial | 2006 | 1 | ficha_flash | Prison Conditions and Prisoner Abuse after Katrina | https://www.aclu.org/documents/prison-conditions-and-prisoner-abuse-after-katrina | 50616 | 3691 | en | ✔ |  |
| F07 | informe_oficial | 2006 | 1 | ficha_flash | Abandoned & Abused: Complete Report | https://www.aclu.org/publications/abandoned-abused-complete-report | 4064571 | 296928 | en | ✖ | original: 200 → pdf_enlazado: 200 |
| F08 | informe_oficial | 2015 | 1 | ficha_flash | Justice in Katrina’s Wake: Changing Course on Incarceration in New Orl | https://www.prisonpolicy.org/scans/vera/justice-in-katrinas-wake.pdf | 484504 | 53592 | en | ✔ |  |
| F09 | informe_oficial | 2009 | 1 | ficha_flash | Department of Justice Civil Rights Division Letter: Re: Orleans Parish | https://www.prisonlegalnews.org/media/publications/doj_cripa_findings_on_orleans_parish_prison_system_conditions_2009.pdf | 1601586 | 82710 | en | ✔ |  |
| F10 | prensa_posterior | 2025 | 2 | similar 0.88 | Reforms resulted from the thousands left to drown in OPP | https://thelensnola.org/2025/08/29/reforms-resulted-from-the-thousands-left-to-drown-in-opp/ | 142587 | 14045 | en | ✔ | copia local de F6c |
| F11 | documental | 2012 | 2 | exacta | Prisoners of Katrina, a BBC Documentary | https://watchopp.wordpress.com/2012/04/24/prisoners-of-katrina-a-bbc-documentary/ |  |  |  | ✖ | original: 200 → wayback: 429 |
| F12 | libro | 2006 | 2 | exacta | Voices from the Storm: The People of New Orleans on Hurricane Katrina  | https://voiceofwitness.org/books/voices-from-the-storm/ | 144883 | 3712 | en | ✔ |  |
| F13 | prensa_posterior | 2015 | 2 | exacta | Hurricane Katrina Was a Nightmare for Inmates in New Orleans | https://www.vice.com/en/article/hurricane-katrina-was-a-nightmare-for-inmates-in-new-orleans-829/ |  |  |  | ✖ | ya hay 10 documentos |
| F14 | prensa_posterior | 2010 | 2 | exacta | Katrina Jail Lawsuit: Jury Awards Tourists $650K | https://www.cbsnews.com/news/katrina-jail-lawsuit-jury-awards-tourists-650k/ |  |  |  | ✖ | ya hay 10 documentos |
| F15 | academico | 2006 | 2 | ficha_flash | Abandoned and Abused: Orleans Parish Prisoners in the Wake of Hurrican | https://www.ojp.gov/ncjrs/virtual-library/abstracts/abandoned-and-abused-orleans-parish-prisoners-wake-hurricane |  |  |  | ✖ | ya hay 10 documentos |
| F16 | academico | 2023 | 2 | ficha_flash | Prisons, Immigration Detention Centers, and Natural Disasters (Sulliva | https://sites.utexas.edu/tjclcr/wp-content/uploads/sites/3748/2023/05/Sullivan.-Prisons-Immigration-Detention-Centers-and-Natural-Diasters.pdf |  |  |  | ✖ | ya hay 10 documentos |
| F17 | prensa_posterior | 2020 | 2 | ficha_flash | Hurricane Katrina, US: 15 Years Later | https://www.hrw.org/news/2020/08/29/hurricane-katrina-us-15-years-later |  |  |  | ✖ | ya hay 10 documentos |
| F18 | academico |  | 2 | ficha_flash | Document from University of Michigan Clearinghouse (PDF) | https://clearinghouse-umich-production.s3.amazonaws.com/media/doc/47486.pdf |  |  |  | ✖ | ya hay 10 documentos |
| F19 | prensa_posterior | 2009 | 2 | ficha_flash | DOJ Investigation Finds Conditions at Orleans Parish Prison Unconstitu | https://www.laaclu.org/press-releases/doj-investigation-finds-conditions-orleans-parish-prison-unconstitutional/ |  |  |  | ✖ | ya hay 10 documentos |
| F20 | academico |  | 2 | ficha_flash | Artículo de Revista de Derecho (American University) | https://digitalcommons.wcl.american.edu/facsch_lawrev/1026/ |  |  |  | ✖ | ya hay 10 documentos |

## Fuentes del modelo fuera (URL que no está en el grounding)

- Re: Orleans Parish Prison System, New Orleans, Louisiana — `https://www.justice.gov/sites/default/files/crt/legacy/2012/04/24/opp_findings_let_9-11-09.pdf`
- Wagenfeald, et al. v. Gusman, et al., No. 11-30081 (5th Cir. 2012) — `https://law.justia.com/cases/federal/appellate-courts/ca5/11-30081/11-30081-2012-03-12.html`
- Department of Justice Issues Scathing Update on Conditions at Orleans Parish Pri — `https://www.aclu-la.org/en/news/department-justice-issues-scathing-update-conditions-orleans-parish-prison`
- WAGANFEALD v. GUSMAN | 674 F.3d 475 (2012) — `https://caselaw.findlaw.com/us-5th-circuit/1596541.html`
- Were Inmates Abandoned at Orleans Parish Prison During Hurricane Katrina? — `https://www.snopes.com/fact-check/opp-katrina-abandoned/`
- After Katrina: Washed Away? The Impact of Hurricane Katrina on the Criminal Just — `https://www.urban.org/sites/default/files/publication/46946/411598-After-Katrina-Washed-Away-.PDF`
- U.S. Department of Justice, Civil Rights Division, Orleans Parish Prison finding — `https://www.justice.gov/sites/default/files/crt/legacy/2012/12/13/Jones_v_Gusman_Findings_Letter.pdf`
- Waganfeald, et al. v. Gusman, et al., No. 11-30081 (5th Cir. 2012) — `https://law.justia.com/cases/federal/appellate-courts/ca5/11-30081/11-30081-2012-03-12.html`
- DOJ Investigation Finds Conditions At Orleans Parish Prison Unconstitutional — `https://www.aclu-la.org/en/news/doj-investigation-finds-conditions-orleans-parish-prison-unconstitutional`
- Criminal Justice Collapse: The Constitution After Hurricane Katrina — `https://scholarship.law.duke.edu/cgi/viewcontent.cgi?article=1383&context=lcp`
- Lessons from Hurricane Katrina: Prison Emergency Preparedness as a Constitutiona — `https://digitalcommons.wcl.american.edu/cgi/viewcontent.cgi?article=1248&context=jgspl`
- Voices from the Storm: Dan Bright — `https://www.voiceofwitness.org/narrators/dan-bright/`
- Orleans Parish Prison System: New Orleans, Louisiana. U.S. Department of Justice — `https://www.justice.gov/crt/about/spl/documents/parish_findlet.pdf`
- Orleans Parish Prison System -- Findings Letter - Prison Legal News — `https://www.prisonlegalnews.org/media/publications/Orleans%20Parish%20Prison%20Findings%20Letter%20re%20CRIPA%20Investigation%209-11-2009.pdf`
- 'Help us, please' — `https://www.pulitzer.org/winners/times-picayune`
- Lessons from Hurricane Katrina: Prison Emergency Preparedness as a Constitutiona — `https://digitalcommons.wcl.american.edu/jlr/vol42/iss1/1/`
- Were Inmates Abandoned at Orleans Parish Prison During Hurricane Katrina? — `https://www.snopes.com/fact-check/orleans-parish-prison-katrina/`
- Abandoned and Abused: Orleans Parish Prisoners in the Wake of Hurricane Katrina — `https://www.aclu.org/sites/default/files/pdfs/prison/abandonedandabused.pdf`
- Criminal Justice Collapse: The Constitution After Hurricane Katrina — `https://scholarship.law.duke.edu/cgi/viewcontent.cgi?article=1148&context=lcp`
- Wagenfeald, et al. v. Gusman, et al., No. 11-30081 (5th Cir. 2012) — `https://law.justia.com/cases/federal/appellate-courts/ca5/11-30081/11-30081-2012-03-12.html`
- 5th Circuit tosses jury’s award in Katrina jail lawsuit — `https://www.themarylanddailyrecord.com/2012/03/12/5th-circuit-tosses-jurys-award-in-katrina-jail-lawsuit/`
