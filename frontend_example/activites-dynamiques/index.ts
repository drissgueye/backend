/**
 * Module activités dynamiques — exports publics pour intégration dans une app Next.js.
 */

export type {
  TypeChampActivite,
  OptionChoice,
  ChampActiviteTemplate,
  ActiviteTemplate,
  ActiviteTemplateListe,
  ActiviteRequete,
  PayloadActiviteTemplate,
  PayloadActiviteRequete,
} from "./types";
export { TYPE_CHAMP_ACTIVITE } from "./types";

export { ExtraDataFields } from "./ExtraDataFields";
export { ActiviteRequeteForm } from "./ActiviteRequeteForm";
export { ActiviteTemplateForm } from "./ActiviteTemplateForm";
export { ActiviteTemplateList } from "./ActiviteTemplateList";
export { SectionRequeteActivites } from "./SectionRequeteActivites";

export {
  fetchActiviteTemplates,
  fetchActiviteTemplate,
  fetchActivitesDisponibles,
  createActiviteTemplate,
  updateActiviteTemplate,
  deleteActiviteTemplate,
  fetchActivitesRequete,
  createActiviteRequete,
  updateActiviteRequete,
  fetchPoles,
} from "./api";
