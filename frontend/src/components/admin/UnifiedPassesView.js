import React from "react";

import AdminView from "../_base/AdminView";
import AdminViewMeta from "../_base/AdminViewMeta";
import { ORGANIZER, SUPER_ADMIN } from "../../lib/roles";
import { renderLocationName } from "../../lib/render";

const LIST_FIELDS = [
  {
    name: "ID",
    key: "id",
  },
  {
    name: "Локация",
    key: (i) => renderLocationName(i.location_data),
    realKey: "location",
  },
  {
    name: "Бот",
    key: (i) => i.bot_data.username,
    realKey: "bot",
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

export default function UnifiedPassesView({ accountRole }) {
  const meta = new AdminViewMeta({
    basePath: "/unified-passes",
    nameCases: {
      first: "Универсальный пропуск",
      firstMultiple: "Универсальные пропуска",
      second: "Универсального пропуска",
      fourth: "Универсальный пропуск",
    },
    entityListApiUrl: "/management-api/unified-passes/",
    entityApiUrlPattern: "/management-api/unified-passes/:id/",
    showFields: LIST_FIELDS.concat([
      {
        name: "QR-код",
        key: (i) => i.qr_code_computed_data.base64_image,
        type: "qr_image",
      },
      {
        name: "Ссылка",
        key: (i) => i.qr_code_computed_data.start_url,
        type: "link",
      },
    ]),
    editFields: [
      {
        name: "Локация",
        key: "location_data",
        realKey: "location",
        type: "autocomplete",
        fetchUrl: `/management-api/locations/`,
        toLabel: (option) => renderLocationName(option),
        isRequired: true,
      },
      {
        name: "Бот",
        key: "bot_data",
        realKey: "bot",
        type: "autocomplete",
        fetchUrl: `/management-api/bots/`,
        toLabel: (option) => option.username,
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
    linkedListFields: ["id"],
    processSaveData: function (formValues) {
      return {
        location: formValues.location_data ? formValues.location_data.id : null,
        bot: formValues.bot_data ? formValues.bot_data.id : null,
        organizer: formValues.organizer_data
          ? formValues.organizer_data.id
          : null,
      };
    },
    accountRole,
  });

  return <AdminView meta={meta} />;
}
