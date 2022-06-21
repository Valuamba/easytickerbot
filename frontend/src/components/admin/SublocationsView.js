import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";

const LIST_FIELDS = [
  {
    name: "Название",
    key: "name",
  },
  {
    name: "Локация",
    key: (i) => i.location_data.name,
    realKey: "location",
  },
  {
    name: "Владелец",
    key: (i) => i.location_owner_data.email,
    realKey: "location_owner",
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function SublocationsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/sublocations",
    nameCases: {
      first: "саблокация",
      firstMultiple: "саблокации",
      second: "саблокации",
      fourth: "саблокацию",
    },
    entityListApiUrl: "/management-api/sublocations/",
    entityApiUrlPattern: "/management-api/sublocations/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Организаторы, которым доступна саблокация",
        key: (i) => (i.organizers_data || []).map((v) => v.email).join(", "),
      },
    ]),
    editFields: [
      {
        name: "Локация",
        key: "location_data",
        realKey: "location",
        type: "autocomplete",
        fetchUrl: `/management-api/locations/`,
        toLabel: (option) => option.name,
        isRequired: true,
      },
      {
        name: "Название",
        key: "name",
        isRequired: true,
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["name"],
    processSaveData: function (formValues) {
      return {
        name: formValues.name,
        location: formValues.location_data ? formValues.location_data.id : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
