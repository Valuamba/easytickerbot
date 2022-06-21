import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { LOCATION_OWNER, ORGANIZER, SUPER_ADMIN } from "../../lib/roles";

const LIST_FIELDS = [
  {
    name: "Название",
    key: "name",
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

export default function LocationsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/locations",
    nameCases: {
      first: "локация",
      firstMultiple: "локации",
      second: "локации",
      fourth: "локацию",
    },
    entityListApiUrl: "/management-api/locations/",
    entityApiUrlPattern: "/management-api/locations/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "Организаторы, которым доступна локация",
        key: (i) => (i.organizers_data || []).map((v) => v.email).join(", "),
      },
    ]),
    editFields: [
      {
        name: "Название",
        key: "name",
        isRequired: true,
      },
      {
        name: "Владелец локации",
        key: "location_owner_data",
        realKey: "location_owner",
        type: "autocomplete",
        fetchUrl: `/management-api/admin-accounts/?role=${LOCATION_OWNER}`,
        toLabel: (option) => option.email,
        isRequired: true,
        availableFor: [SUPER_ADMIN],
      },
      {
        name: "Организаторы, которым доступна локация",
        key: "organizers_data",
        realKey: "organizers",
        type: "autocomplete",
        isMultiple: true,
        toLabel: (option) => option.email,
        fetchUrl: `/management-api/admin-accounts/?role=${ORGANIZER}`,
        availableFor: [SUPER_ADMIN, LOCATION_OWNER],
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["name"],
    processSaveData: function (formValues) {
      const organizersData = formValues.organizers_data;
      return {
        name: formValues.name,
        location_owner: formValues.location_owner_data
          ? formValues.location_owner_data.id
          : null,
        organizers: organizersData
          ? organizersData.map((value) => value.id)
          : [],
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
