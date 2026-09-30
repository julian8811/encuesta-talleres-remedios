/**
 * Crea las preguntas de la Encuesta de satisfacción y atractivos del territorio
 * (Talleres Remedios, Colegio Mayor de Antioquia) en el formulario FORM_ID.
 *
 * Uso: en script.google.com cree un proyecto, pegue este archivo, guarde y ejecute crearEncuesta.
 * Autorice con jose.gomez.lopez@colmayor.edu.co.
 *
 * Los títulos de las preguntas deben quedar tal cual: la encuesta HTML los usa para conectar cada campo.
 */

const FORM_ID = "1FqxuMXYOtEZaQwMNlTYXA9TfYZxeJ5e_CjJu_H4ZmM8";
const CORREO_AVISOS = "jose.gomez.lopez@colmayor.edu.co";

const TALLERES = [
  "1 · Instalación y mapa de actores",
  "2 · Diagnóstico participativo",
  "3 · Visión y ejes estratégicos",
  "4 · Programas y proyectos",
  "5 · Plan de acción y validación"
];
const SECTORES = ["Público", "Privado", "Sociedad civil", "Academia y cooperación", "Habitante / independiente"];
const ROLES = ["Prestador de servicios turísticos", "Comerciante", "Minero artesanal / barequero", "Agricultor / campesino",
  "Líder comunitario / JAC", "Gestor cultural / artesano", "Servidor público", "Docente / estudiante", "Otro"];
const ZONAS_VIVE = ["Cabecera municipal", "Corregimiento", "Vereda", "Otro municipio"];
const EDADES = ["18 a 28", "29 a 45", "46 a 60", "Más de 60"];
const GENEROS = ["Mujer", "Hombre", "Otra identidad", "Prefiere no decir"];
const ASPECTOS = ["Metodología y actividades", "Trabajo del equipo facilitador", "Claridad de la información",
  "Oportunidad de participar y ser escuchado", "Lugar, refrigerio y logística", "Horario y duración",
  "Utilidad para el plan de turismo", "Satisfacción general con el taller"];
const NECESIDADES = ["Vías y acceso", "Seguridad", "Formación y capacitación", "Promoción", "Señalización",
  "Alojamiento y servicios", "Cuidado del patrimonio y la naturaleza", "Financiación", "Organización de los actores"];
const TIPOS = ["Natural (río, quebrada, cascada, cueva, sendero, mirador)", "Histórico o arquitectónico", "Religioso",
  "Minero y aurífero (mina, barequeo, orfebrería)", "Gastronomía", "Fiesta o evento", "Saber u oficio tradicional", "Otro"];
const ZONAS_ATR = ["Cabecera municipal", "Corregimiento", "Vereda"];
const ACCESOS = ["A pie", "Moto", "Carro", "Por río", "A caballo o mula"];
const ESTADOS = ["Bueno", "Regular", "Malo"];
const VISITANTES = ["Sí", "A veces", "No"];
const SI_NO = ["Sí", "No"];

function crearEncuesta() {
  const form = FormApp.openById(FORM_ID);
  form.getItems().forEach(function (it) { form.deleteItem(it); });

  form.setTitle("Encuesta de satisfacción y atractivos del territorio")
    .setDescription("Plan Municipal de Turismo · Remedios, Antioquia. Talleres participativos · Institución Universitaria Colegio Mayor de Antioquia.")
    .setConfirmationMessage("Gracias. Su respuesta quedó registrada.")
    .setCollectEmail(false)
    .setLimitOneResponsePerUser(false)
    .setAllowResponseEdits(false)
    .setProgressBar(false);
  // La encuesta HTML envía de forma anónima: el formulario no puede exigir cuenta de Google.
  try { form.setRequireLogin(false); } catch (err) { Logger.log("setRequireLogin: %s", err); }

  const lista = function (t, opts, req) { return form.addListItem().setTitle(t).setChoiceValues(opts).setRequired(!!req); };
  const unica = function (t, opts) { return form.addMultipleChoiceItem().setTitle(t).setChoiceValues(opts); };
  const corta = function (t, req) { return form.addTextItem().setTitle(t).setRequired(!!req); };
  const parrafo = function (t) { return form.addParagraphTextItem().setTitle(t); };

  form.addSectionHeaderItem().setTitle("1. Datos del taller");
  lista("Taller", TALLERES, true);
  form.addDateItem().setTitle("Fecha");
  corta("Sede del taller", true);
  corta("Encuestador");

  form.addSectionHeaderItem().setTitle("2. Participante");
  unica("Sector", SECTORES);
  lista("Ocupación o rol", ROLES);
  lista("Dónde vive", ZONAS_VIVE);
  corta("Corregimiento, vereda o municipio");
  unica("Edad", EDADES);
  unica("Se identifica como", GENEROS);
  corta("Nombre");
  corta("Teléfono");
  unica("Autoriza datos", SI_NO).setHelpText("Tratamiento de datos personales para la formulación del Plan Municipal de Turismo (Ley 1581 de 2012).");

  form.addSectionHeaderItem().setTitle("3. Satisfacción con el taller");
  ASPECTOS.forEach(function (a, i) {
    form.addScaleItem().setTitle(a).setBounds(1, 5).setLabels("Muy insatisfecho", "Muy satisfecho")
      .setRequired(i === ASPECTOS.length - 1);
  });
  unica("Recomendaría participar", ["Sí", "Tal vez", "No"]);
  parrafo("Qué fue lo que más le gustó");
  parrafo("Qué deberíamos mejorar");

  form.addSectionHeaderItem().setTitle("5. Para el plan de turismo");
  form.addCheckboxItem().setTitle("Necesidades del turismo").setChoiceValues(NECESIDADES)
    .setValidation(FormApp.createCheckboxValidation().requireSelectAtMost(2).build());
  parrafo("Idea o proyecto");

  for (let n = 1; n <= 5; n++) {
    form.addSectionHeaderItem().setTitle("Atractivo " + n);
    const p = "Atractivo " + n + " · ";
    corta(p + "Nombre");
    lista(p + "Tipo", TIPOS);
    lista(p + "Ubicación", ZONAS_ATR);
    corta(p + "Corregimiento o vereda");
    lista(p + "Cómo se llega", ACCESOS);
    lista(p + "Estado actual", ESTADOS);
    unica(p + "Recibe visitantes", VISITANTES);
    parrafo(p + "Por qué lo recomendaría");
    unica(p + "Es el más representativo", SI_NO);
  }

  let destino = null;
  try { destino = form.getDestinationId(); } catch (err) { destino = null; }
  if (!destino) {
    const hoja = SpreadsheetApp.create("Respuestas · Encuesta Talleres Remedios");
    form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());
  }

  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === "avisarRespuesta") ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger("avisarRespuesta").forForm(form).onFormSubmit().create();

  Logger.log("Listo: %s preguntas. Hoja: %s", form.getItems().length,
    SpreadsheetApp.openById(form.getDestinationId()).getUrl());
}

/**
 * Resumen para la pestaña Resultados de la encuesta HTML.
 * Implementar > Nueva implementación > Aplicación web · Ejecutar como: yo · Acceso: cualquier persona.
 * No publica nombre, teléfono ni encuestador.
 */
const CLAVES_ASPECTOS = ["metodologia", "facilitacion", "informacion", "participacion", "logistica", "horario", "utilidad", "general"];

function doGet() {
  const respuestas = FormApp.openById(FORM_ID).getResponses().map(function (resp) {
    const v = {};
    resp.getItemResponses().forEach(function (ir) { v[ir.getItem().getTitle()] = ir.getResponse(); });
    const txt = function (t) { const x = v[t]; return x == null ? "" : String(x); };
    const num = function (t) { const x = parseInt(v[t], 10); return isNaN(x) ? null : x; };
    const sat = {};
    ASPECTOS.forEach(function (a, i) { if (CLAVES_ASPECTOS[i] !== "general") sat[CLAVES_ASPECTOS[i]] = num(a); });
    const atractivos = [];
    for (let n = 1; n <= 5; n++) {
      const p = "Atractivo " + n + " · ";
      if (!txt(p + "Nombre")) continue;
      atractivos.push({
        nombre: txt(p + "Nombre"), tipo: txt(p + "Tipo"), zona: txt(p + "Ubicación"), lugar: txt(p + "Corregimiento o vereda"),
        acceso: txt(p + "Cómo se llega"), estado: txt(p + "Estado actual"), visitantes: txt(p + "Recibe visitantes"),
        porque: txt(p + "Por qué lo recomendaría"), representativo: txt(p + "Es el más representativo") === "Sí"
      });
    }
    return {
      id: resp.getId(), creado: resp.getTimestamp().toISOString(),
      taller: txt("Taller").charAt(0), fecha: txt("Fecha"), sede: txt("Sede del taller"),
      sector: txt("Sector"), rol: txt("Ocupación o rol"), zona: txt("Dónde vive"), residencia: txt("Corregimiento, vereda o municipio"),
      edad: txt("Edad"), genero: txt("Se identifica como"),
      sat: sat, general: num("Satisfacción general con el taller"), recomienda: txt("Recomendaría participar"),
      gusto: txt("Qué fue lo que más le gustó"), mejorar: txt("Qué deberíamos mejorar"),
      necesidad: v["Necesidades del turismo"] || [], idea: txt("Idea o proyecto"), atractivos: atractivos
    };
  });
  return ContentService.createTextOutput(JSON.stringify({ ok: true, respuestas: respuestas }))
    .setMimeType(ContentService.MimeType.JSON);
}

function avisarRespuesta(e) {
  const filas = e.response.getItemResponses()
    .filter(function (r) { const v = r.getResponse(); return v !== "" && v !== null && !(Array.isArray(v) && !v.length); })
    .map(function (r) {
      const v = r.getResponse();
      return r.getItem().getTitle() + ": " + (Array.isArray(v) ? v.join(", ") : v);
    });
  MailApp.sendEmail(CORREO_AVISOS, "Nueva respuesta · Encuesta Talleres Remedios", filas.join("\n"));
}
