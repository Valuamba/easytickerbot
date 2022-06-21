import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";

const LIST_FIELDS = [
  {
    name: "Название",
    key: "username",
  },
  {
    name: "Организатор",
    key: (i) => i.organizer_data.email,
    realKey: "organizer",
  },
  {
    name: "Дата создания",
    key: "created_at",
    type: "datetime",
  },
];

export default function BotsView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/bots",
    entityListApiUrl: "/management-api/bots/",
    entityApiUrlPattern: "/management-api/bots/:id/",
    nameCases: {
      first: "бот",
      firstMultiple: "боты",
      second: "бота",
      fourth: "бота",
    },
    showFields: LIST_FIELDS,
    editFields: [
      {
        name: "Токен",
        key: "token",
        isRequired: true,
      },
      {
        name: "Организатор",
        key: "organizer_data",
        realKey: "organizer",
        type: "autocomplete",
        fetchUrl: `/management-api/admin-accounts/?role=${ORGANIZER}`,
        toLabel: (option) => option.email,
        isRequired: true,
        availableFor: [SUPER_ADMIN],
      },
    ],
    listFields: LIST_FIELDS,
    linkedListFields: ["username"],
    processSaveData: function (formValues) {
      const organizersData = formValues.organizers_data;
      return {
        token: formValues.token,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
